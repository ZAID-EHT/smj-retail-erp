# SMJ Retail ERP — Mobile / Responsive Verification

No browser automation ran in this pass (Playwright not installed, and
installing it needs approval per the mission's own constraints — see
`SMJ_VISUAL_REGRESSION.md`). This document records what was verified by
reading `frontend/src/design/responsive.css` and the component templates,
not by rendering screenshots.

## Breakpoints already in place (pre-existing, unchanged structure)

| Breakpoint | Behaviour |
|---|---|
| ≤ 1450px | Brand copy truncates, module button icons hide, search narrows |
| ≤ 1180px | Module row hides behind hamburger → `MobileNavigation` drawer, search takes remaining width |
| ≤ 760px | Header padding tightens, brand subtitle hides, page container padding drops to 12px |
| ≤ 768px (universal engine) | Tables convert to stacked cards (`.rug-table-region`, `.ru-table-wrap`, `.ref-data-table-wrap` all have card-mode media queries), forms collapse to one column |
| ≤ 480px | Detail header collapses to one column, KPI grids drop to 2 columns |
| ≤ 720px (transaction register) | `.rug-table-region` hidden, `.rug-card-list` shown |
| `prefers-reduced-motion: reduce` | All animation/transition durations forced to `.01ms` |

This table-to-card conversion pattern already existed before this pass and
was confirmed still intact after the token rewrite (media queries reference
the same class names, none were renamed).

## What changed for mobile in this pass (2026-07-15)

- Icon buttons and form controls now meet the 44×44px touch-target minimum
  (`--ref-control-height`, `.ref-icon-button` min-width/min-height) at every
  breakpoint, not just desktop.
- `MobileNavigation.vue` now renders real per-module icons instead of a `◆`
  glyph.

## 2026-07-16 browser-verification pass: one real desktop/tablet risk found and fixed

Re-reading the breakpoint math against the *live* navigation payload (not
just the static route file) surfaced a real gap: the server now permits 11
modules (`home, smart-sales, sales, purchases, inventory, finance,
operations, crm, reports, pos, admin`), and the `1181–1450px` range (the
only width where the full module row shows but the `≤1450px`
padding-shrink is also active) had no `overflow-x` handling on
`.ref-module-navigation` at all — if the row's content ever exceeded the
available width in that range, the previous CSS had no fallback (buttons
would either be squeezed or the header would overflow, both of which this
mission explicitly forbids). Fixed by adding `overflow-x: auto` +
`white-space: nowrap` to `.ref-module-navigation`, which is the exact
"horizontal scrolling" fallback the mission's own Section 8 endorses. See
`SMJ_BROWSER_ISSUES_FIXED.md` #3. This could not be visually confirmed
(no browser), only reasoned through the CSS box model — flag it as the
first thing to visually re-check once browser automation is available.

## Not verified

Actual rendering at 1440×900 / 1920×1080 / 768×1024 / 390×844 / 360×800 /
1024×768 — no screenshots were captured, no real viewport was rendered.
This should be the first thing a follow-up session with browser automation
available does. See `SMJ_BROWSER_VERIFICATION.md` for exactly why
Playwright could not be installed even with approval.
