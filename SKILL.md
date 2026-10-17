---
name: social-content-kit
description: Prepare a tailored social content campaign from a website or project, with a calendar, ready-to-publish copy, images, alt text, checked links, and an offline HTML catalog. Use for reusable multi-platform content kits; publishing and scheduling require a separate user request.
---

# Social Content Kit

Turn a real project into a useful, locally saved publication kit. Adapt the content to the audience and the job each platform should do. The deliverable is finished material, not just topic suggestions.

## Understand the brief

Use the user's website, audience, business goal, publication language, start date, duration, timezone, platforms, cadence, destination folder, and any supplied examples. Read [brief.md](references/brief.md) for optional settings and sensible defaults. Ask only for consequential missing information that cannot be inferred; otherwise state your assumptions and proceed.

Distinguish paid-product subscriptions, newsletter subscriptions, trials, and social follows. Do not silently substitute one goal for another. Dates and times need an explicit timezone. Do not copy the example campaign's brand, dates, audience, claims, or posting frequency into a new project.

All skill documentation and the bundled catalog interface are English. Publication copy and alt text follow the requested publication language. A user can ask for a translated catalog separately.

## Research before writing

Read the public homepage, relevant product/pricing/FAQ pages, and candidate articles. For a local project, read its agent instructions and current approved product state. Separate shipped capabilities from plans. Verify conflicting marketing statements against stronger current evidence and record unresolved discrepancies.

Review the user's selected reference kit for structure, visual quality, and tone. Extract the useful pattern; do not transplant its facts or unrelated personal stories.

Select material by practical value, audience fit, and relevance to the intended action. Use available authorized analytics when useful, recording period and metric definitions. If analytics are unavailable, say so; do not invent popularity rankings. A thin blog is not a reason to invent articles: develop original posts around the product's concept, workflows, use cases, limitations, and questions, linking to the actual homepage or relevant existing pages.

Save a concise source shortlist and dated claim/evidence notes in the output folder. Read [editorial.md](references/editorial.md) before drafting claims or adapting content across platforms.

## Design the campaign

Choose a realistic cadence for each requested platform. Balance practical advice, examples, product explanation, and a clear conversion invitation. Rest/review days are valid. Explain what to say and what to show for each content pillar.

Use platform-specific copy: one useful idea for X, a complete short story or explanation for Facebook, a conversation-opening observation for Threads, and a searchable, save-worthy title plus description for Pinterest. Apply the same principle to other requested networks rather than forcing them into those four formats.

Keep a complete caption per post, including its final link where appropriate. Pinterest title, description, destination URL, and alt text are separate fields. Trackable URLs may use per-post UTM parameters, but do not claim attribution exists merely because tags exist. Never place personal data in tracking parameters.

## Produce the visual assets

Provide an actual finished image for every image-based post. Choose imagery or information design that makes the post useful; a generic repeated slogan is not enough. Use a consistent brand palette and typography without making every platform's creative identical.

- For photographic/editorial/illustrated creative, use the environment's available image-generation capability or user-owned/authorized assets. If there is an imagegen skill, follow it. Do not require a particular provider or API key when a built-in tool is available.
- For exact calendars, checklists, comparisons, or explanatory diagrams, deterministic HTML/CSS, SVG, or plotting tools can be appropriate. Export to PNG/JPEG for publication.
- Pinterest needs separately composed 2:3 portrait images, such as 1000×1500 or 1024×1536. Do not crop away essential text to reuse a square asset.
- Label fictional data and conceptual interface illustrations. Do not present generated scenes as actual customers, product screenshots, property photos, or results.
- Inspect the finished pixels. Check typography, safe margins, contrast, content accuracy, and whether the image agrees with its caption and alt text. Keep useful editable sources and generation prompts.

The included demo images are deliberately simple workflow diagrams for documentation. They are not a universal creative style or a substitute for campaign-specific assets.

## Assemble the kit

Use [data-contract.md](references/data-contract.md) for the portable JSON format and helper commands. The scripts handle packaging and deterministic checks, not research, writing, or image generation. Adapt their output if the user needs a different structure.

```sh
python scripts/build_kit.py path/to/campaign.json --output path/to/Social
python scripts/validate_kit.py path/to/Social
```

The builder creates an English offline `index.html`, local assets, platform/post folders, `calendar.csv`, `calendar.md`, `content-plan.md`, `campaign.json`, `results-tracker.csv`, and `START-HERE.md`. Each post folder has copy, image, alt text, link, sources, and publishing notes; Pinterest also has separate title/description files. Read existing output before using `--overwrite`; the builder preserves an existing results tracker.

Keep all deliverables local unless the user authorizes another destination. Preparing a kit does not authorize posting, scheduling, creating ad campaigns, or changing the source website.

## Validate and deliver

Read [platforms.md](references/platforms.md) and verify current official platform limits for the chosen post types. The example configuration contains conservative editorial budgets, not a permanent platform specification database.

Run the local validator, then check public destination URLs with `--check-links` when network access is appropriate. The network check rejects non-public addresses and credentials in URLs. Authentication-dependent or unreachable destinations need manual follow-up and honest reporting; a 200 response alone does not prove that content is correct.

Review images and all final captions. Verify image sizes, file decoding, title/caption/alt limits, date/time conversions, and links. The built-in X count is deliberately conservative for non-ASCII text; use the official twitter-text implementation when exact Unicode weighting is needed. Recount after every copy edit.

Open `index.html` locally and check filters, copy fallback, downloads, all image references, keyboard access, and narrow/mobile layouts. A practical baseline is 360, 390, 430, and desktop widths. Avoid external fonts, CDNs, analytics, or API calls in the catalog.

Report the output folder, catalog link, count by platform, date range/timezone, checks performed, and any real limitations. Keep expected performance separate from measured results. Leave a blank results tracker for later factual entries. Never label the kit fully ready if required images, links, or essential checks are still missing.
