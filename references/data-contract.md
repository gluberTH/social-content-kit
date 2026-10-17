# Campaign JSON contract

Read `examples/campaign.json` for a complete runnable example. The builder accepts UTF-8 JSON (with or without a BOM). Use Python 3.10+ and the root `requirements.txt`.

## Top-level fields

| Field | Required | Description |
| --- | --- | --- |
| `schema_version` | Yes | `1` |
| `brand` | Yes | Object with `name` and public HTTP(S) `website` |
| `audience` | Yes | Concrete audience description |
| `goals` | Yes | Non-empty array of goal strings |
| `language` | Yes | Publication language tag, such as `en`, `es`, or `pt-BR`; interface stays English |
| `start_date` | Yes | ISO date `YYYY-MM-DD` |
| `duration_days` | Yes | 1–366 calendar days |
| `timezone` | Yes | IANA zone, such as `Asia/Bangkok` or `Europe/Madrid` |
| `utm_campaign` | No | Omit or set empty to leave destination URLs unchanged |
| `research_notes` | Recommended | Evidence, source selection, analytics availability, limitations |
| `strategy` | Yes | `summary`, `measurement`, and `pillars`: each pillar has `name`, `say`, `show` |
| `platforms` | Yes | Map of configurable platform profiles |
| `posts` | Yes | Non-empty list of finished posts |
| `demo` | No | `true` labels the entire catalog as a fictional demonstration |

## Platform profile

Keys use letters, digits, underscores, or hyphens. Add networks freely; there is no fixed four-network restriction.

```json
"linkedin": {
  "label": "LinkedIn",
  "format": "image",
  "caption_limit": 1200,
  "alt_limit": 500,
  "count_mode": "raw",
  "link_mode": "inline",
  "image_ratio": "1:1",
  "max_image_mb": 10,
  "notes": "These are chosen editorial budgets. Recheck the actual post specifications."
}
```

`format` is `image` (default) or `pin`. Pins require `title_limit`, `link_mode: separate`, a `pin_title` per post, and an actual 2:3 image. `link_mode: inline` appends the tracked URL to the body. `separate` keeps the link in its own field, useful for Pins or channels where caption URLs are not clickable. Add accurate publishing instructions for the latter case.

`count_mode` is `raw` (Unicode NFC code points) or `x_conservative` (ASCII one, other code points two, URLs 23). Read `platforms.md` for its limits. `image_ratio` is optional for ordinary images and exact when supplied. `max_image_mb` defaults to 20 MiB. Budgets are explicit configuration, not live platform discovery.

## Post fields

Required: `id`, `platform`, `date`, `time`, `title`, `topic`, `intent`, `body`, `destination_url`, `source_urls`, `alt`, `image`, `visual_note`, and `evidence_note`.

- `id`: unique ignoring case, up to 64 letters/digits/underscores/hyphens; starts with a letter/digit.
- `date` / `time`: local campaign date and `HH:MM`; must fall inside the configured duration.
- `fold`: optional `0` or `1` for an ambiguous DST clock time. Nonexistent times are rejected. UTC includes its own date, so crossing midnight is handled.
- `body`: final copy without the automatically appended destination URL. Inline references may appear, but avoid duplicated destination links.
- `source_urls`: at least one evidence/reference URL. Editorial advice can cite the relevant source project with a candid evidence note.
- `image`: finished PNG/JPEG/WebP relative to the input JSON's directory. Paths cannot escape that directory. Symlinks resolving outside it are rejected.
- `visual_note`: asset provenance and whether the image is a diagram, illustration, or genuine screenshot.
- `evidence_note`: what supports the claim and any material limitation.
- `pin_title` is required for a Pin. `board` is optional.

The builder adds `caption`, `url`, `count`, local/UTC ISO timestamps, image metadata/hash, and relative output paths. These generated fields are recalculated during validation.

## Commands

```sh
python -m pip install -r requirements.txt
python scripts/build_kit.py examples/campaign.json --output output/example
python scripts/validate_kit.py output/example
python scripts/validate_kit.py output/example --check-links
```

The builder does no network access. `--check-links` issues public GET requests with no credentials, cookies, or environment proxy. It checks each redirect and rejects non-public DNS addresses. Some real sites block automated checks; record that limitation and inspect them normally. It does not authenticate, submit forms, or publish.

To regenerate an owned kit, use `--overwrite`. It refreshes files listed in the prior `.kit-manifest.json`, preserves the results tracker and unrelated files, and leaves removed-post folders in place. They are absent from the new catalog. Use a fresh output folder for a clean release or when preserving an accepted version. Regeneration resets the automated QA report; rerun validation and update manual-review evidence.

## Output structure

```text
Social/
  index.html
  START-HERE.md
  content-plan.md
  calendar.md
  calendar.csv
  campaign.json
  results-tracker.csv
  QA_REPORT.md
  validation.json             # after validation
  .kit-manifest.json
  pinterest/2026-10-19_P01/
    image.png
    caption.txt
    title.txt
    description.txt
    alt-text.txt
    destination-link.txt
    source-links.txt
    publish-notes.txt
    post.json
```

Other platforms have the same companion files except Pin-only title/description. CSV uses UTF-8 BOM for spreadsheet compatibility and neutralizes formula-leading cells. The HTML embeds CSS, JavaScript, and campaign data, references local images, and works under `file://` with a manual clipboard fallback.
