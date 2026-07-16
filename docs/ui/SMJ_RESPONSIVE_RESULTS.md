# SMJ Retail ERP — Responsive Results (2026-07-16)

## Method

Real headless Chrome screenshots this pass (see
`SMJ_BROWSER_VERIFICATION.md` for how authentication was handled). Tested
the rebuilt Home dashboard at 1440×1300 (desktop) and 390×844 / 390×1800 /
390×2200 (mobile, several heights to see the full page).

## Desktop (1440×900+) — verified, looks correct

Confirmed via screenshot: header, KPI row, 3-column chart row, 3-column
lower row, 2-column bottom row all render as intended, matching the
reference structure. No visible defects.

## Mobile (390px) — partially fixed, one residual issue not fully resolved

### Found and fixed (confirmed via before/after screenshots)

The first mobile screenshot of the new Home dashboard showed real,
significant horizontal overflow: the KPI grid's `minmax(190px, 1fr)`
columns didn't collapse at narrow widths, and — the actual root cause,
found by adding temporary coloured debug outlines (`outline: 3px solid
...`) to each container level and screenshotting again — `.rug-page`'s
`display: grid` children default to CSS's `min-width: auto` (not `0`),
which lets a child's content-based intrinsic width force the whole grid
row wider than the viewport. Fixed by:

- Collapsing `.smj-home-kpis` to 2 then 1 column at `≤760px`/`≤520px`
- `.rug-page > * { min-width: 0; }` — the general-purpose fix for the
  grid-item sizing default, applied once for every page using this shared
  `.rug-page` pattern, not just Home
- Wrapping the Recent Transactions table in a scrollable container
  (`.smj-home-transactions { overflow-x: auto }`) instead of letting its
  `white-space: nowrap` cells force page width — the same pattern the rest
  of the app already uses for tables, which this new page had missed
- `max-width: 100%` + `min-width: 0` on `SmjKpiCard` and `SmjChartCard`'s
  own root elements

After these fixes, the hero quick-action buttons and all 6 KPI cards
render correctly within the viewport, confirmed by screenshot comparison
(the "before" screenshot showed cards cut off mid-text; "after" does not).

### Not fully resolved

Two small text elements — the "View Report" link in the Sales Trend chart
card header, and the percentage/amount values in the Payment Collection
donut's legend — still appear clipped at the right edge in mobile
screenshots, despite several further rounds of fixes applying the same
`min-width: 0` pattern one level deeper (`.smj-chart-card__header`,
`.smj-donut__legend li`) plus explicit `flex-direction: column` stacking
at `≤480px`. Each fix was confirmed present and correctly compiled in the
built CSS (`grep`-verified against the actual served bundle, with the
exact asset hash cross-checked against what the browser loads), yet the
screenshots before and after several of these specific changes were
pixel-identical — which is not the expected result for a real, working
CSS fix. This inconsistency (code correctly changed and confirmed loaded,
but zero visible difference across multiple targeted fixes) suggests
something about how this specific pass captured mobile screenshots may
not be fully reliable, rather than the CSS being definitively wrong — but
that could not be confirmed either way without live DevTools access
(headless screenshot + `dump-dom` was all that was available; there is no
way to inspect computed styles or actually interact with the page).

**Honest status: source-level fixes applied and believed correct
(standard, textbook CSS patterns for this exact class of bug), but not
conclusively visually verified.** Flagged here explicitly rather than
either claiming it's fixed or silently leaving it undocumented. The
concrete next step for a follow-up session: reproduce with real DevTools
(Chrome's own inspector, not headless automation) and check the computed
width of `.smj-chart-card__actions` and `.smj-donut__legend` at 390px.

## Not tested this pass

1920×1080, 1024×768, 360×800 were not screenshotted (time-constrained —
390px and 1440px were prioritised as the two ends of the range most likely
to surface problems). Other pages (Smart Sales, Sales Orders, etc.) were
not re-tested at mobile width this pass; their responsive behaviour is
whatever the previous session's audit found, unchanged here.
