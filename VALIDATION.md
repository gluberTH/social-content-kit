# Release validation

Validated on October 17, 2026, using Python 3.12 and Chromium on Windows.

- Skill metadata and structure validator: passed.
- 15 behavioral tests: passed, including custom platforms, Spanish copy with English catalog controls, timezone date rollover, DST ambiguity, text budgets, image constraints, escaping, and safe regeneration.
- Eight-post demo: built successfully; images decoded; companion files and local references checked; configured text and image budgets passed.
- Demo public destination links: passed. These are reserved example.com demonstration URLs, not a real product or conversion flow.
- Catalog checked at 360, 390, 430, and 1440 pixels: no page overflow; all eight images decoded.
- Platform/week/search filters, empty state, reset, restricted-clipboard fallback, calendar navigation/focus, and image download: passed.
- English repository landing checked at 360 and 1440 pixels; preview loaded.
- Browser checks observed no JavaScript errors and no remote requests from the catalog.

The included images are original, explicitly fictional workflow diagrams. The demo is a packaging example, not a recommended publishing cadence or evidence of campaign performance. Platform budgets remain configurable; verify current specifications and factual claims for each real campaign. macOS and Linux have not been directly tested in this release.
