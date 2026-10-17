"""Shared validation and rendering helpers. No network or publication side effects."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from PIL import Image

PACKAGE = Path(__file__).resolve().parents[1]
ID = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$')
URL = re.compile(r'https?://\S+')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, field):
    require(isinstance(value, str) and bool(value.strip()), f'{field}: non-empty text required')
    return value.strip()


def identifier(value, field):
    require(isinstance(value, str) and ID.fullmatch(value), f'{field}: use letters, digits, hyphens or underscores, at most 64 characters')
    return value


def safe_path(root, relative):
    require(isinstance(relative, str) and not Path(relative).is_absolute(), 'A relative local path is required')
    target = (root / relative).resolve()
    require(target.is_relative_to(root.resolve()), f'Path escapes its root: {relative}')
    return target


def public_url(value):
    value = text(value, 'URL')
    p = urlsplit(value)
    require(p.scheme in ('http', 'https') and p.hostname and not p.username and not p.password, 'Use an absolute HTTP(S) URL without credentials')
    require(not any(c.isspace() or ord(c) < 32 for c in value), 'URL contains whitespace or control characters')
    require(p.port in (None, 80, 443), 'Only standard public web ports are supported')
    return value


def tracked_url(url, campaign, platform, post_id):
    public_url(url)
    if not campaign:
        return url
    p = urlsplit(url)
    params = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k not in ('utm_source', 'utm_medium', 'utm_campaign', 'utm_content')]
    params += [('utm_source', platform), ('utm_medium', 'organic_social'), ('utm_campaign', campaign), ('utm_content', post_id.lower())]
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(params), p.fragment))


def count_caption(caption, mode):
    normalized = unicodedata.normalize('NFC', caption)
    if mode == 'raw':
        return len(normalized)
    require(mode == 'x_conservative', f'Unsupported count mode: {mode}')
    total = 0
    start = 0
    for match in URL.finditer(normalized):
        total += sum(1 if ord(c) < 128 else 2 for c in normalized[start:match.start()]) + 23
        start = match.end()
    return total + sum(1 if ord(c) < 128 else 2 for c in normalized[start:])


def timestamp(day, clock, zone, fold=None):
    require(fold is None or (type(fold) is int and fold in (0, 1)), 'fold must be 0 or 1 when supplied')
    require(re.fullmatch(r'\d{2}:\d{2}', clock), 'Use HH:MM local time')
    naive = datetime.fromisoformat(f'{day}T{clock}')
    tz = ZoneInfo(zone)
    candidates = [naive.replace(tzinfo=tz, fold=f) for f in (0, 1)]
    valid = [d for d in candidates if d.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None) == naive]
    require(valid, f'{day} {clock} does not exist in {zone} (DST transition)')
    ambiguous = len({d.utcoffset() for d in valid}) > 1
    require(not ambiguous or fold in (0, 1), f'{day} {clock} is ambiguous in {zone}; set fold to 0 or 1')
    local = candidates[fold or 0]
    return local.isoformat(), local.astimezone(timezone.utc).isoformat()


def image_info(path):
    require(path.is_file(), f'Missing image: {path.name}')
    with Image.open(path) as im:
        require(im.format in ('PNG', 'JPEG', 'WEBP'), f'Unsupported image format: {im.format}')
        result = {'width': im.width, 'height': im.height, 'format': im.format}
        im.verify()
    # Reopen and decode pixel data as well as checking the file container.
    with Image.open(path) as im:
        im.load()
    result.update(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return result


def normalize(data, source_root):
    require(data.get('schema_version') == 1, 'schema_version must be 1')
    data = json.loads(json.dumps(data))
    for key in ('brand', 'platforms', 'strategy'):
        require(isinstance(data.get(key), dict), f'{key} must be an object')
    text(data['brand'].get('name'), 'brand.name')
    public_url(data['brand'].get('website'))
    text(data.get('audience'), 'audience')
    text(data.get('language'), 'language')
    require(re.fullmatch(r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*', data['language']), 'language must be a language tag such as en or es')
    require(isinstance(data.get('goals'), list) and all(isinstance(x, str) and x for x in data['goals']) and data['goals'], 'goals must be a non-empty text array')
    start = date.fromisoformat(data['start_date'])
    days = data['duration_days']
    require(type(days) is int and 1 <= days <= 366, 'duration_days must be 1..366')
    ZoneInfo(data['timezone'])
    require(data['platforms'], 'At least one platform is required')
    for key, profile in data['platforms'].items():
        identifier(key, 'platform key')
        text(profile.get('label'), f'{key}.label')
        for field in ('caption_limit', 'alt_limit'):
            require(type(profile.get(field)) is int and profile[field] > 0, f'{key}.{field} must be positive')
        require(profile.get('format', 'image') in ('image', 'pin'), 'format must be image or pin')
        require(profile.get('link_mode', 'inline') in ('inline', 'separate'), 'link_mode must be inline or separate')
        require(profile.get('count_mode', 'raw') in ('raw', 'x_conservative'), 'Unknown count_mode')
        if profile.get('format') == 'pin':
            require(profile.get('link_mode') == 'separate', 'Pins require separate destination URLs')
            require(type(profile.get('title_limit')) is int and profile['title_limit'] > 0, 'Pins require title_limit')
        if profile.get('image_ratio'):
            require(re.fullmatch(r'[1-9]\d*:[1-9]\d*', profile['image_ratio']), 'image_ratio must be positive W:H')
        require(type(profile.get('max_image_mb', 20)) in (int, float) and profile.get('max_image_mb', 20) > 0, 'max_image_mb must be positive')
    require(isinstance(data.get('posts'), list) and data['posts'], 'Provide at least one finished post')
    ids = set()
    for p in data['posts']:
        identifier(p.get('id'), 'post.id')
        require(p['id'].lower() not in ids, 'Post IDs must be unique, ignoring case')
        ids.add(p['id'].lower())
        require(p.get('platform') in data['platforms'], f"Unknown platform for {p['id']}")
        profile = data['platforms'][p['platform']]
        day = date.fromisoformat(p['date'])
        require(start <= day < start + timedelta(days=days), f"{p['id']} is outside the campaign")
        p['local_timestamp'], p['utc_timestamp'] = timestamp(p['date'], p['time'], data['timezone'], p.get('fold'))
        for field in ('title', 'topic', 'intent', 'body', 'alt', 'visual_note', 'evidence_note'):
            p[field] = text(p.get(field), f"{p['id']}.{field}")
        require(isinstance(p.get('source_urls'), list) and p['source_urls'], f"{p['id']} needs source_urls")
        for source in p['source_urls']:
            public_url(source)
        p['destination_url'] = public_url(p['destination_url'])
        p['url'] = tracked_url(p['destination_url'], data.get('utm_campaign'), p['platform'], p['id'])
        p['caption'] = p['body'] + ('\n\n' + p['url'] if profile.get('link_mode', 'inline') == 'inline' else '')
        p['count'] = count_caption(p['caption'], profile.get('count_mode', 'raw'))
        require(p['count'] <= profile['caption_limit'], f"{p['id']}: caption {p['count']} exceeds {profile['caption_limit']}")
        require(len(p['alt']) <= profile['alt_limit'], f"{p['id']}: alt text exceeds limit")
        if profile.get('format') == 'pin':
            p['pin_title'] = text(p.get('pin_title'), f"{p['id']}.pin_title")
            require(len(p['pin_title']) <= profile['title_limit'], f"{p['id']}: Pin title exceeds limit")
            require(not URL.search(p['body']), f"{p['id']}: put the Pin URL in its destination field")
        source_path = safe_path(source_root, p['image'])
        p['image_info'] = image_info(source_path)
        info = p['image_info']
        require(info['bytes'] <= profile.get('max_image_mb', 20) * 1024 * 1024, f"{p['id']}: image exceeds byte budget")
        ratio = '2:3' if profile.get('format') == 'pin' else profile.get('image_ratio')
        if ratio:
            a, b = map(int, ratio.split(':'))
            require(info['width'] * b == info['height'] * a, f"{p['id']}: image must be {ratio}")
    data['posts'].sort(key=lambda p: (p['local_timestamp'], p['id']))
    return data
