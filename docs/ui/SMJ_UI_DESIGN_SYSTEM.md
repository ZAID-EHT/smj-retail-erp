# SMJ Retail ERP — Design System

Source of truth: `SMJ_Retail_ERP_UI_Design_Pack/03_design_specs/COLOR_PALETTE.json`
and `DESIGN_TOKENS.css`, applied on top of the existing `frontend/src/design/`
token architecture (kept the `--ref-*` variable names so every current
template kept working unmodified; `--smj-*` aliases were added for
documentation traceability).

## Where the tokens live

`frontend/src/design/tokens.css` — single source of truth, scoped to
`.ref-app-shell`. Every other stylesheet in `frontend/src/design/`
(`base.css`, `universal.css`, `generated-ux.css`, `priority-pages.css`,
`standalone.css`, `responsive.css`) consumes these variables instead of
hardcoded colours, which is what makes the theme apply everywhere at once —
handcrafted pages, the universal DocType engine, and both parallel list/
detail/form implementations (`src/pages/entities/*` and
`src/pages/generated/*`) share the same CSS files.

## Colours

| Token | Value | Usage |
|---|---|---|
| `--ref-header-start` / `--ref-header-end` | `#07369D` → `#071B72` | Header gradient, `90deg` |
| `--ref-primary-blue` | `#0B63F6` | Brand blue, primary buttons, links |
| `--ref-dark-blue` | `#0644C4` | Primary button hover |
| `--ref-focus-colour` | `#8BB8FF` | Focus ring |

Module colours are exposed both as the new named tokens
(`--ref-module-home` … `--ref-module-admin`) **and** remapped onto the
existing legacy accent keys (`blue`, `dark-blue`, `purple`, `pink`, `green`,
`orange`, `turquoise`) that every route's `meta.accent` already uses. This
means routes did not need to change — the same accent name now resolves to
the exact SMJ hex value:

| Legacy accent key | Resolves to | SMJ family |
|---|---|---|
| `blue` | `#0B63F6` | Home / brand |
| `dark-blue` | `#2F6FED` | Reports |
| `green` | `#18B66B` | Sales |
| `orange` | `#FF7A1A` | Inventory |
| `purple` | `#7B4BE8` | Purchases / Admin |
| `pink` | `#F0447D` | CRM |
| `turquoise` | `#0DB6B2` | Operations |

Semantic colours (`--ref-success #18A96B`, `--ref-warning #F59E0B`,
`--ref-danger #EF4444`, `--ref-info #3B82F6`) replaced every ad-hoc hardcoded
error/warning hex value found across `base.css`, `universal.css`,
`generated-ux.css`, `priority-pages.css` and `standalone.css`.

## Typography

`Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
(no font files downloaded or committed). Scale tokens: `--ref-text-page-title`
(700 28px), `--ref-text-section-title` (700 17px), `--ref-text-body` (400
14px), `--ref-text-table` (400 13px), `--ref-text-kpi` (700 26px).

## Spacing, radius, sizing

4px-based spacing scale (`--ref-space-1` … `--ref-space-10`), card radius
16px (`--ref-card-radius`), panel radius 20px, button/input radius 10px.
Controls (`--ref-control-height`) are 44px, meeting the 44×44px touch-target
minimum on both desktop and mobile. Table rows are 48-53px depending on
table type (data table vs child table).

## Shadows

`--ref-card-shadow`: `0 1px 2px rgba(17,34,68,.04), 0 8px 24px rgba(32,54,92,.06)`
— restrained, no heavy glassmorphism.

## Known simplification

The header is a single 64px row (brand + page actions + module nav + search
+ user menu) rather than the two-row layout sketched in the reference —
every functional requirement (no sidebar, all navigation in the header,
working search, working user menu) is met without the extra row, and this
was judged the lower-risk path given the size of the rest of the mission.
