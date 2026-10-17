#!/usr/bin/env python3
"""Package finished campaign JSON and images into an offline publication kit."""
from __future__ import annotations

import argparse
import base64
import csv
import html
import io
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from kitlib import PACKAGE, normalize, require, safe_path


def esc(value):
    return html.escape(str(value), quote=True)


def field(post_id, key, label, value, language):
    ident = f'{post_id}-{key}'
    return f'<label class="field-label" for="{esc(ident)}">{esc(label)}</label><textarea id="{esc(ident)}" rows="5" readonly lang="{esc(language)}">{esc(value)}</textarea><button type="button" class="copy" data-copy="{esc(ident)}">Copy {esc(label.lower())}</button>'


def card(p, campaign, downloads):
    profile = campaign['platforms'][p['platform']]
    pin = profile.get('format') == 'pin'
    lang = campaign['language']
    week = (date.fromisoformat(p['date']) - date.fromisoformat(campaign['start_date'])).days // 7 + 1
    search = ' '.join(str(p.get(k, '')) for k in ('id', 'title', 'topic', 'intent', 'caption', 'board')).lower()
    fields = field(p['id'], 'title', 'Pin title', p['pin_title'], lang) if pin else ''
    fields += field(p['id'], 'caption', 'Description' if pin else 'Caption', p['caption'], lang)
    limit_label = 'conservative weighted' if profile.get('count_mode') == 'x_conservative' else 'characters'
    sources = ''.join(f'<li><a class="long-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(url)}</a></li>' for url in p['source_urls'])
    title_count = f"Title: {len(p['pin_title'])}/{profile['title_limit']} · " if pin else ''
    board = f'<p class="meta">Suggested board: {esc(p["board"])}</p>' if p.get('board') else ''
    return f'''<article class="card" id="post-{esc(p['id'])}" data-platform="{esc(p['platform'])}" data-week="{week}" data-search="{esc(search)}">
<a class="image-link" href="{esc(p['image'])}" target="_blank" rel="noopener" aria-label="Open image {esc(p['id'])}"><img src="{esc(p['image'])}" width="{p['image_info']['width']}" height="{p['image_info']['height']}" alt="{esc(p['alt'])}" lang="{esc(lang)}" loading="lazy"></a>
<div class="card-body"><div class="card-top"><span>{esc(profile['label'])}</span><span>{esc(p['id'])}</span></div>
<p class="meta">{esc(p['date'])} · {esc(p['time'])} {esc(campaign['timezone'])}<br>UTC: {esc(p['utc_timestamp'])}<br>{p['image_info']['width']} × {p['image_info']['height']} px</p>
<h3 lang="{esc(lang)}">{esc(p['title'])}</h3><p class="meta">{esc(p['topic'])} · {esc(p['intent'])}</p>{fields}
<p class="count">{title_count}{p['count']}/{profile['caption_limit']} {limit_label}</p>{board}
<details><summary>Alt text and destination</summary>{field(p['id'], 'alt', 'Alt text', p['alt'], lang)}{field(p['id'], 'url', 'Destination URL', p['url'], 'en')}<p class="meta">{esc(profile.get('notes', ''))}</p></details>
<div class="actions"><a class="button" href="{esc(downloads.get(p['image'], p['image']))}" download="{esc(p['id'])}{Path(p['image']).suffix}">Download image</a><a class="button" href="{esc(p['folder'])}/caption.txt">Text file</a><a class="button" href="{esc(p['folder'])}/publish-notes.txt">Publishing notes</a></div>
<details><summary>Sources and visual notes</summary><ul class="sources">{sources}</ul><p class="sources">{esc(p['evidence_note'])}</p><p class="sources">{esc(p['visual_note'])}</p></details></div></article>'''


def catalog(campaign, downloads=None):
    downloads = downloads or {}
    posts, platforms = campaign['posts'], campaign['platforms']
    counts = Counter(p['platform'] for p in posts)
    stats = ''.join(f'<div class="stat"><strong>{counts[k]}</strong><span>{esc(v["label"])}</span></div>' for k, v in platforms.items())
    filters = '<button type="button" data-filter="all" class="active" aria-pressed="true">All</button>' + ''.join(f'<button type="button" data-filter="{esc(k)}" aria-pressed="false">{esc(v["label"])} {counts[k]}</button>' for k, v in platforms.items())
    weeks = ''.join(f'<option value="{i}">Week {i}</option>' for i in range(1, (campaign['duration_days'] + 6) // 7 + 1))
    start = date.fromisoformat(campaign['start_date'])
    rows = []
    for offset in range(campaign['duration_days']):
        day = (start + timedelta(days=offset)).isoformat()
        cells = []
        for key in platforms:
            matches = [p for p in posts if p['date'] == day and p['platform'] == key]
            cells.append(''.join(f'<a href="#post-{esc(p["id"])}" data-open-post="{esc(p["id"])}"><strong>{esc(p["id"])} · {esc(p["time"])}</strong><small>{esc(p["title"])}</small></a>' for p in matches) or '—')
        rows.append('<tr><th scope="row">' + day + '</th>' + ''.join('<td>' + cell + '</td>' for cell in cells) + '</tr>')
    pillars = ''.join(f'<article class="panel"><h3>{esc(p["name"])}</h3><p><b>Say:</b> {esc(p["say"])}</p><p><b>Show:</b> {esc(p["show"])}</p></article>' for p in campaign['strategy'].get('pillars', []))
    css = (PACKAGE / 'assets/catalog.css').read_text(encoding='utf-8')
    js = (PACKAGE / 'assets/catalog.js').read_text(encoding='utf-8')
    brand = esc(campaign['brand']['name'])
    end = start + timedelta(days=campaign['duration_days'] - 1)
    label = 'Fictional demonstration · not a live campaign' if campaign.get('demo') else 'Local publication kit · nothing published'
    serialized = json.dumps(campaign, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{brand} · Social Content Kit</title><style>{css}</style></head><body>
<a href="#materials" class="skip">Skip to materials</a><header><div class="wrap"><p class="eyebrow">{brand} / Social studio</p><span class="status">{label}</span><h1>{brand}.<br><em>Useful content, ready to review.</em></h1><p>{esc(campaign['audience'])}</p><p><b>{start} — {end}</b><br>{len(posts)} posts · {esc(campaign['timezone'])} · Publication language: {esc(campaign['language'])}</p><div class="stats">{stats}</div></div></header>
<nav aria-label="Catalog"><div class="wrap"><a class="brand" href="#">{brand}</a><a href="#strategy">Strategy</a><a href="#calendar">Calendar</a><a href="#materials">Materials</a><a href="QA_REPORT.md">Checks</a></div></nav>
<main class="wrap"><div class="notice"><b>Prepared for manual publication.</b><br>No posts are sent or scheduled by this catalog. Times are test slots unless supported by account analytics. External destinations open only when you choose a link.</div>
<section id="strategy"><p class="eyebrow">01 / Editorial direction</p><h2>A useful idea. A clear next step.</h2><p>{esc(campaign['strategy'].get('summary', ''))}</p><p><b>Goals:</b> {esc(', '.join(campaign['goals']))}</p><div class="pillars">{pillars}</div><div class="panel"><h3>Measurement</h3><p>{esc(campaign['strategy'].get('measurement', 'Record observed results in the tracker.'))}</p></div><div class="resources"><a class="button" href="START-HERE.md">Start here</a><a class="button" href="content-plan.md">Content plan</a><a class="button" href="results-tracker.csv">Results tracker</a><a class="button" href="campaign.json">Campaign JSON</a></div></section>
<section id="calendar"><p class="eyebrow">02 / Publication calendar</p><h2>{campaign['duration_days']} days at a glance</h2><p>Local dates and times use {esc(campaign['timezone'])}. Each post also shows its full UTC date and time. Empty cells are intentionally unscheduled.</p><div class="table-scroll" tabindex="0" role="region" aria-label="Publication calendar; scroll horizontally on small screens"><table><thead><tr><th scope="col">Local date</th>{''.join('<th scope="col">'+esc(v['label'])+'</th>' for v in platforms.values())}</tr></thead><tbody>{''.join(rows)}</tbody></table></div><div class="resources"><a class="button" href="{esc(downloads.get('calendar.csv', 'calendar.csv'))}" download="calendar.csv">Download calendar CSV</a><a class="button" href="calendar.md">Text calendar</a></div></section>
<section id="materials"><p class="eyebrow">03 / Ready materials</p><h2>Copy. Image. Destination.</h2><p>Each post includes its finished copy, image, alt text, and link. Pins have separate title, description, and destination fields.</p><div class="controls"><div class="filters" role="group" aria-label="Filter platform">{filters}</div><div class="form-row"><label for="week">Week<select id="week"><option value="all">All weeks</option>{weeks}</select></label><label for="search">Search<input type="search" id="search" placeholder="Topic, title, or post ID"></label><button type="button" id="reset">Reset filters</button></div><p id="result-count" role="status" aria-live="polite">Showing {len(posts)} of {len(posts)} posts</p></div><div class="grid">{''.join(card(p, campaign, downloads) for p in posts)}</div><div class="empty" id="empty" hidden>No matching posts. Try another filter.</div></section>
<footer>Local Social Content Kit. No external scripts, fonts, analytics, or publishing API.<br>Review the QA report and current product terms before publishing.</footer></main>
<dialog id="copy-dialog" aria-labelledby="copy-title"><h2 id="copy-title">Copy the selected text</h2><p>Your browser restricted clipboard access. Press Ctrl+C or Command+C.</p><textarea id="copy-fallback" readonly aria-label="Text to copy"></textarea><button type="button" id="close-dialog">Done</button></dialog><div id="toast" role="status" hidden></div><script type="application/json" id="campaign-data">{serialized}</script><script>{js}</script></body></html>'''


def table_csv(fields, rows):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        # Spreadsheet-safe CSV: neutralize formula-leading cells in untrusted prose.
        writer.writerow({k: ("'" + str(v) if str(v).startswith(('=', '+', '-', '@', '\t', '\r')) else v) for k, v in row.items()})
    return '\ufeff' + buffer.getvalue()


def build(config, output, overwrite=False):
    config, output = config.resolve(), output.resolve()
    require(output != config.parent and output not in config.parents, 'Output must not contain or replace the input campaign')
    data = normalize(json.loads(config.read_text(encoding='utf-8-sig')), config.parent)
    marker = output / '.kit-manifest.json'
    old = json.loads(marker.read_text(encoding='utf-8')) if marker.is_file() else None
    require(not output.exists() or not any(output.iterdir()) or (overwrite and old and old.get('generator') == 'social-content-kit'), 'Output is non-empty. Use a new folder or --overwrite for an existing generated kit')
    files = {}
    def add(relative, content):
        files[relative] = content.encode('utf-8') if isinstance(content, str) else content
    for p in data['posts']:
        source = safe_path(config.parent, p['image'])
        suffix = {'PNG': '.png', 'JPEG': '.jpg', 'WEBP': '.webp'}[p['image_info']['format']]
        p['folder'] = f"{p['platform']}/{p['date']}_{p['id']}"
        p['image'] = p['folder'] + '/image' + suffix
        add(p['image'], source.read_bytes())
        for name, value in [('caption.txt', p['caption']), ('alt-text.txt', p['alt']), ('destination-link.txt', p['url']), ('source-links.txt', '\n'.join(p['source_urls']))]:
            add(p['folder'] + '/' + name, value + '\n')
        profile = data['platforms'][p['platform']]
        notes = f"{p['id']} | {profile['label']}\nLocal: {p['local_timestamp']} ({data['timezone']})\nUTC: {p['utc_timestamp']}\nGoal: {p['intent']}\n\nUpload the image and add the supplied alt text. "
        if profile.get('format') == 'pin':
            add(p['folder'] + '/title.txt', p['pin_title'] + '\n')
            add(p['folder'] + '/description.txt', p['body'] + '\n')
            notes += 'Put title, description, and destination into their separate fields.\n'
        else:
            notes += 'Paste caption.txt exactly.\n'
        notes += profile.get('notes', '') + '\n' + p['visual_note'] + '\n' + p['evidence_note'] + '\nNo publication or scheduling has been performed.\n'
        add(p['folder'] + '/publish-notes.txt', notes)
        add(p['folder'] + '/post.json', json.dumps(p, ensure_ascii=False, indent=2) + '\n')
    add('campaign.json', json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    fields = ['id', 'platform', 'local_timestamp', 'timezone', 'utc_timestamp', 'title', 'topic', 'intent', 'url', 'image', 'alt', 'caption']
    add('calendar.csv', table_csv(fields, [{k: data['timezone'] if k == 'timezone' else p[k] for k in fields} for p in data['posts']]))
    downloads = {}
    for p in data['posts']:
        mime = {'PNG': 'image/png', 'JPEG': 'image/jpeg', 'WEBP': 'image/webp'}[p['image_info']['format']]
        downloads[p['image']] = 'data:' + mime + ';base64,' + base64.b64encode(files[p['image']]).decode('ascii')
    downloads['calendar.csv'] = 'data:text/csv;base64,' + base64.b64encode(files['calendar.csv']).decode('ascii')
    add('index.html', catalog(data, downloads))
    calendar = ['# Publication calendar', '', f"Timezone: {data['timezone']}. UTC dates and times are shown separately.", '']
    for i in range(data['duration_days']):
        day = (date.fromisoformat(data['start_date']) + timedelta(days=i)).isoformat()
        calendar += ['## ' + day, '']
        matches = [p for p in data['posts'] if p['date'] == day]
        calendar += [f"- {p['time']} {data['timezone']} | UTC {p['utc_timestamp']} | {p['platform']} {p['id']}: {p['title']}" for p in matches] or ['- No new post. Review replies and available results.']
        calendar += ['']
    add('calendar.md', '\n'.join(calendar))
    plan = ['# Content plan', '', data['strategy'].get('summary', ''), '', '**Audience:** ' + data['audience'], '**Goals:** ' + ', '.join(data['goals']), '**Publication language:** ' + data['language'], '**Timezone:** ' + data['timezone'], '']
    for pillar in data['strategy'].get('pillars', []):
        plan += ['## ' + pillar['name'], '', 'Say: ' + pillar['say'], '', 'Show: ' + pillar['show'], '']
    plan += ['## Measurement', '', data['strategy'].get('measurement', ''), '', '## Research notes', '', data.get('research_notes', 'Source evidence is recorded per post. Add editorial research notes before delivery.'), '']
    add('content-plan.md', '\n'.join(plan))
    add('START-HERE.md', '# Start here\n\nOpen index.html locally. Everything works offline except external destination links. No account connection or web server is needed.\n\nFor each post, upload its image, paste caption.txt, and enter alt-text.txt in the accessibility field. For Pins, use title.txt, description.txt, and destination-link.txt separately. Read publish-notes.txt for network-specific steps.\n\nThe calendar includes local and UTC dates. Use the specified timezone in your own scheduler if you later choose to schedule. No posts have been sent or scheduled by this package.\n\nReview QA_REPORT.md and current product conditions before publishing. Keep measured results in results-tracker.csv.\n')
    add('QA_REPORT.md', '# Validation pending\n\nRun scripts/validate_kit.py against this folder. Generated files are not proof of factual, visual, link, or browser review.\n')
    tracker_fields = ['id', 'platform', 'planned_local', 'live_url', 'measured_at', 'impressions', 'outbound_clicks', 'saves', 'meaningful_replies', 'visits_if_available', 'verified_accounts_if_attributable', 'paid_conversions_if_attributable', 'notes']
    if not (output / 'results-tracker.csv').exists():
        add('results-tracker.csv', table_csv(tracker_fields, [dict(id=p['id'], platform=p['platform'], planned_local=p['local_timestamp']) for p in data['posts']]))
    # Preflight all writes before modifying anything. Preserve unowned files.
    for relative in files:
        target = safe_path(output, relative)
        require(not target.exists() or (overwrite and old and relative in old['files']), f'Refusing to overwrite an unowned file: {relative}')
    output.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        target = safe_path(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    tracked_files = sorted(set(files) | ({'results-tracker.csv'} if (output / 'results-tracker.csv').exists() else set()))
    marker.write_text(json.dumps({'generator': 'social-content-kit', 'schema_version': 1, 'files': tracked_files}, indent=2), encoding='utf-8')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--overwrite', action='store_true', help='Refresh owned files in an existing generated kit; preserve results tracker and unrelated files')
    args = parser.parse_args()
    try:
        data = build(args.campaign, args.output, args.overwrite)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'Build failed: {exc}\n')
    print(f"Built {len(data['posts'])} posts in {args.output.resolve()}")


if __name__ == '__main__':
    main()
