#!/usr/bin/env python3
"""Validate a local kit; optionally check public HTTP destinations without credentials."""
from __future__ import annotations

import argparse
import http.client
import ipaddress
import json
import socket
import ssl
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from kitlib import normalize, public_url, require, safe_path


def check_url(url):
    original = url
    for _ in range(6):
        public_url(url)
        parsed = urlsplit(url)
        host = parsed.hostname.encode('idna').decode('ascii')
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        addresses = list({x[4][0] for x in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)})
        require(addresses and all(ipaddress.ip_address(ip).is_global for ip in addresses), 'Link resolves to a non-public address')
        # Pin this connection to a checked address. Use the original host for TLS and Host.
        connection = http.client.HTTPConnection(addresses[0], port, timeout=15)
        sock = socket.create_connection((addresses[0], port), timeout=15)
        connection.sock = ssl.create_default_context().wrap_socket(sock, server_hostname=host) if parsed.scheme == 'https' else sock
        try:
            target = (parsed.path or '/') + ('?' + parsed.query if parsed.query else '')
            connection.request('GET', target, headers={'Host': parsed.netloc, 'User-Agent': 'SocialContentKit-LinkCheck/1.0', 'Accept': 'text/html,*/*;q=0.5'})
            response = connection.getresponse()
            status = response.status
            location = response.getheader('Location')
            response.read(65536)
        finally:
            connection.close()
        if status in (301, 302, 303, 307, 308) and location:
            url = urljoin(url, location)
            continue
        return {'url': original, 'final_url': url, 'status': status, 'pass': 200 <= status < 300, 'checked_at': datetime.now(timezone.utc).isoformat()}
    raise ValueError('Too many redirects')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.local = []
        self.external_assets = []
        self.ids = set()
        self.posts = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'article' and 'card' in attrs.get('class', '').split():
            self.posts += 1
        for key in ('href', 'src'):
            value = attrs.get(key)
            if not value:
                continue
            if tag == 'a' and 'download' in attrs and value.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,', 'data:image/webp;base64,', 'data:text/csv;base64,')):
                continue
            if value.startswith(('http:', 'https:', '//')):
                if key == 'src' or tag == 'link':
                    self.external_assets.append(value)
            else:
                self.local.append(value)


def validate(root, check_links=False):
    root = root.resolve()
    data = json.loads((root / 'campaign.json').read_text(encoding='utf-8'))
    normalized = normalize(data, root)
    failures, images = [], []
    for expected, stored in zip(normalized['posts'], data['posts']):
        require(expected == stored, f"{expected['id']}: generated metadata, counts, dates, or image hash no longer matches")
        p = expected
        for name, value in [('caption.txt', p['caption']), ('alt-text.txt', p['alt']), ('destination-link.txt', p['url']), ('source-links.txt', '\n'.join(p['source_urls']))]:
            require(safe_path(root, p['folder'] + '/' + name).read_text(encoding='utf-8').rstrip('\n') == value, f"{p['id']}: {name} differs from campaign.json")
        require(json.loads(safe_path(root, p['folder'] + '/post.json').read_text(encoding='utf-8')) == p, f"{p['id']}: post.json mismatch")
        require(safe_path(root, p['folder'] + '/publish-notes.txt').is_file(), 'Missing publishing notes')
        if data['platforms'][p['platform']].get('format') == 'pin':
            for filename, value in [('title.txt', p['pin_title']), ('description.txt', p['body'])]:
                require(safe_path(root, p['folder'] + '/' + filename).read_text(encoding='utf-8').rstrip('\n') == value, f'{filename} mismatch')
        images.append({'id': p['id'], **p['image_info'], 'caption_count': p['count']})
    parser = Links()
    parser.feed((root / 'index.html').read_text(encoding='utf-8'))
    require(parser.posts == len(data['posts']), 'Catalog post count differs')
    require(not parser.external_assets, 'Catalog loads external assets')
    for link in parser.local:
        if link.startswith('#'):
            require(link == '#' or link[1:] in parser.ids, f'Broken anchor: {link}')
        else:
            require(safe_path(root, unquote(link.split('#')[0])).is_file(), f'Broken local link: {link}')
    links = []
    if check_links:
        urls = sorted({p['url'] for p in data['posts']} | {s for p in data['posts'] for s in p['source_urls']} | {data['brand']['website']})
        for url in urls:
            try:
                result = check_url(url)
            except (OSError, ValueError, http.client.HTTPException) as exc:
                result = {'url': url, 'pass': False, 'error': str(exc)}
            links.append(result)
        failures += [x['url'] for x in links if not x['pass']]
    result = {'status': 'FAIL' if failures else 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(), 'posts': len(images), 'images': images, 'local_references': len(parser.local), 'links_checked': check_links, 'links': links, 'failures': failures, 'manual_checks_required': ['Factual claims and destination relevance', 'Image pixels and alt text', 'Catalog interaction and mobile layout', 'Current platform specifications'], 'scope': 'Local package validation; no posts published or scheduled'}
    (root / 'validation.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    report = f"# Automated validation: {result['status']}\n\nChecked: {result['checked_at']}\n\n- Posts and decoded images: {len(images)}\n- Local HTML references: {len(parser.local)}\n- Character budgets, dates, image ratios, hashes, and companion files: PASS\n- Public HTTP links: {'PASS' if check_links and not failures else 'FAIL' if failures else 'NOT RUN'}\n\n## Manual review still required\n\n" + '\n'.join('- ' + x for x in result['manual_checks_required']) + '\n\nA passing script is not proof of editorial accuracy, visual quality, or successful publication. See validation.json for details.\n'
    (root / 'QA_REPORT.md').write_text(report, encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--check-links', action='store_true', help='GET public HTTP(S) destinations; no credentials or private addresses')
    args = parser.parse_args()
    try:
        result = validate(args.folder, args.check_links)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'Validation failed: {exc}\n')
    print(json.dumps({k: result[k] for k in ('status', 'posts', 'local_references', 'links_checked', 'failures')}))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
