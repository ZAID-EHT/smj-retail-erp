# SMJ Retail ERP — Accessibility Checklist

Status based on code inspection, not automated audit tooling (none was run
this pass).

| Item | Status | Notes |
|---|---|---|
| Visible keyboard focus | ✅ pre-existing, kept | `:focus-visible { box-shadow: var(--ref-focus-ring) }`, ring colour updated to SMJ `#8BB8FF` |
| Skip-to-content link | ✅ pre-existing | `.ref-skip-link` in `standalone.css` |
| Icon-only buttons have `aria-label` | ✅ | Mobile toggle, search close, user menu, dropdown close all carry `aria-label` |
| Decorative icons hidden from screen readers | ✅ | Every icon usage added this pass passes `decorative` → `aria-hidden="true"` on the underlying `<svg>` |
| Interactive icons get an accessible name | ✅ | `IconBase.vue` renders `<title>` from the `title` prop when not decorative |
| Form labels | ✅ pre-existing | `.ref-form-field` wraps every input in a `<label>`-equivalent structure |
| Escape closes dialogs/menus | ✅ pre-existing | `GlobalSearch`, module dropdowns, `UserMenu` |
| Focus trap in modals | ✅ pre-existing | `v-focus-trap` directive on `MobileNavigation` and confirm dialogs |
| Touch targets ≥ 44×44px | ✅ | `--ref-control-height: 44px` applied to buttons, inputs, icon buttons this pass |
| Colour not the sole status indicator | ⚠️ partial | Status pills/badges rely on colour + text label (label is present), but no icon reinforcement was added to every badge — acceptable per WCAG since text is always present, not upgraded further this pass |
| `prefers-reduced-motion` respected | ✅ pre-existing | `responsive.css` |
| Automated contrast check (axe/Lighthouse) | ❌ not run | No tooling available in this environment this pass |

Semantic colours were chosen to keep contrast reasonable against white
surfaces (`--ref-danger #EF4444` on `color-mix(..., white 94%)` backgrounds,
etc.) but exact contrast ratios were not measured.
