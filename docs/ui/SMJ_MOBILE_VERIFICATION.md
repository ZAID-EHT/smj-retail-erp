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

## What changed for mobile in this pass

- Icon buttons and form controls now meet the 44×44px touch-target minimum
  (`--ref-control-height`, `.ref-icon-button` min-width/min-height) at every
  breakpoint, not just desktop.
- `MobileNavigation.vue` now renders real per-module icons instead of a `◆`
  glyph.

## Not verified

Actual rendering at 1440×900 / 1920×1080 / 768×1024 / 390×844 / 360×800 —
no screenshots were captured. This should be the first thing a follow-up
session with browser automation available does.
