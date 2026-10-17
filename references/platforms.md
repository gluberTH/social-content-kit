# Platform checks

Recheck official documentation for the actual account and post type when producing a campaign. Limits and format support change. Store the checked date and source in the campaign's research notes.

| Network / format | Useful starting check |
| --- | --- |
| Standard X post | 280 weighted characters. URLs normally count as 23. Use [official character guidance](https://docs.x.com/fundamentals/counting-characters) and twitter-text for exact complex Unicode. |
| Pinterest image Pin | Separate title, description, link, alt. Compose a 2:3 portrait image. Check [Pin specifications](https://help.pinterest.com/en/article/review-pin-specs) and [creative guidance](https://business.pinterest.com/creative-best-practices/). |
| Standard Threads post | Check the current standard-post limit; do not silently depend on long-text attachments. [Meta product information](https://about.fb.com/news/2023/07/introducing-threads-new-app-text-sharing/). |
| Facebook feed image | A short readable caption is often preferable to the technical maximum. Configure an editorial budget and current upload limits for the chosen format. |
| Instagram | A caption URL is generally not a clickable feed link. Write an accurate bio-link instruction only if the link is configured; otherwise record the required manual step. Confirm current format and caption limits. |
| LinkedIn | Match the actual post type and audience; separate professional insight from empty business jargon. Verify image/caption specifications. |
| Other networks | Add a platform profile to the JSON. The helper is platform-agnostic; the author still has to verify network-specific limits and publication behavior. |

Example budgets: X 280, Threads 500, Facebook 1500 editorial, Pinterest title 100 and description 500 editorial. Pinterest's published description limit was 800 when the source workflow was checked on 2026-10-17; the smaller example budget is intentional. These are configurable examples, not guarantees that every composer accepts every format forever.

The helper counts Unicode code points for raw budgets. Its `x_conservative` mode normalizes NFC, weights URLs at 23, counts ASCII as one and other code points as two. This is exact for ASCII-only captions but may overcount accented text, joined emoji, and other sequences. Use official twitter-text to resolve a conservative failure rather than weakening the limit.

Image review covers the actual uploaded pixels, not only metadata: orientation, text, contrast, crop, readability, and honest representation. Check the client-specific alt field at publication time. Never append hashtags or shorten links after validation without recounting the final copy.
