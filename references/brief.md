# Campaign brief

Start from the user's instructions. These fields help when the brief is incomplete:

| Field | Meaning / default when reasonable |
| --- | --- |
| Website / project | Required source identity. A repository can supplement the public site. |
| Audience | Specific people, scale, context, recurring problems, buying stage. |
| Goal | Visits, trial signup, paid subscription, lead, purchase, newsletter, or follows. |
| Publication language | User's requested language; do not infer it from the chat language alone. |
| Catalog language | English by default in this package. |
| Start / duration | Explicit ISO date and number of calendar days; two weeks when requested. |
| Timezone | An IANA timezone. Do not silently treat local dates as UTC. |
| Platforms / format | Requested networks and post types. Do not add accounts or formats without a reason. |
| Cadence | Adapt to available material and production capacity; one daily post everywhere is not mandatory. |
| Brand | Voice, colors, typography, logo/asset permissions, prohibited claims. |
| Sources | Public pages, provided analytics, local product docs, selected reference kit. |
| Links | Homepage/product/article preference; optional campaign UTM identifier. |
| Output | A new local folder, normally `Social`; preserve an existing accepted kit. |

If the user supplies a complete brief, do not ask them to fill another form. If only optional decisions remain, state a reasonable assumption and keep working.

Example natural-language invocation:

> Use $social-content-kit for https://example.com. Our audience is independent language teachers. We want product visits and trial signups. Prepare two weeks starting 2027-03-08 for LinkedIn, Instagram, and Pinterest. Posts in Spanish; catalog and documentation in English. Use Europe/Madrid time, a warm practical voice, and save everything to Social. Do not publish.

For an existing campaign, read the current files before changing copy or dates. Preserve manual edits and recorded results. Generate a new version folder when broad changes would make overwrite unsafe.
