# SMJ Retail ERP — Chart & KPI Framework

## Why hand-rolled SVG, not a chart library

`npm install` cannot reach the registry from this environment — confirmed
in a previous session (`UNABLE_TO_VERIFY_LEAF_SIGNATURE` even with
`--use-system-ca`, plain HTTP gets `403`; see
`SMJ_VISUAL_REGRESSION.md`) and unchanged this session. No chart library
was already installed (`frontend/package.json` only lists `vue` and
`vue-router`). Per the mission's own instruction ("use the existing
project chart library... do not add another unless the existing project
has no suitable option") a new dependency would be justified — but it's
literally impossible to install one here, so the components are hand-rolled
SVG instead. This also keeps the performance requirements (no giant chart
library, lightweight SVG) trivially satisfied.

## Components (`frontend/src/components/charts/`)

| Component | Purpose |
|---|---|
| `SmjSparkline.vue` | Tiny inline trend line for KPI cards |
| `SmjKpiCard.vue` | Label + icon + value + trend% + sparkline, module-accent coloured |
| `SmjLineChart.vue` | Multi-series line chart, gridlines, hover tooltip, legend |
| `SmjDonutChart.vue` | Segment breakdown with centre value/label and a legend |
| `SmjBarChart.vue` | Horizontal bar comparison |
| `SmjChartCard.vue` | Shared card shell: title, subtitle, last-refreshed, refresh button, "View Report" link, loading skeleton, error state, empty state |

All values are formatted through a caller-supplied `valueFormatter` (the
Home dashboard passes real currency formatting) — no chart hardcodes a
number format.

## What each state actually does

- **Loading**: `SmjChartCard` renders a shimmer skeleton (`loading` prop),
  driven by the real in-flight fetch promise, not a fixed timeout.
- **Empty**: each Home dashboard fetch computes a real "is there anything
  to show" check (e.g. `!trend?.series?.some((s) => s.values.some((v) => v))`)
  and `SmjChartCard`'s `empty` prop shows a genuine message — not shown
  merely because the array happens to be short.
- **Error**: any fetch rejection is caught and the message (from the
  backend's real exception, not a generic string) is shown in the card.
- **Refresh**: every chart card's refresh button calls the same `loadAll()`
  the page uses on mount — it re-fetches, it does not fake a spinner.

## Data sources

See `SMJ_DASHBOARD_DATA_SOURCES.md` for exactly which ERPNext doctypes and
aggregate queries feed each chart.

## Known gaps

- No drill-down click-through from chart segments/bars to filtered report
  views yet (the KPI cards and "View Report" links do link out; the charts
  themselves are display-only). Noted as remaining work, not attempted.
- Tooltip on `SmjLineChart` is mouse-hover only — no touch/tap equivalent
  for mobile users yet.
- Accessible text summaries (Section 25's "chart text summaries"
  requirement) were not added — each chart card's data is also shown in
  its legend/table form alongside the chart, which gives a text
  alternative in practice, but no explicit `aria-describedby` summary was
  wired up.
