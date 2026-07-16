# SMJ Retail ERP — Accessibility Checklist

Status based on code inspection, not automated audit tooling or a real
browser (neither was available this pass — see `SMJ_BROWSER_VERIFICATION.md`).

| Item | Status | Notes |
|---|---|---|
| Visible keyboard focus | ✅ pre-existing, kept | `:focus-visible { box-shadow: var(--ref-focus-ring) }`, ring colour updated to SMJ `#8BB8FF` |
| Skip-to-content link | ✅ pre-existing, re-verified | Lives in `my_store_ui/www/retail_erp.html` (the server-rendered shell), not a Vue component — a 2026-07-16 re-check nearly flagged this as missing by only grepping `.vue` files; corrected in `SMJ_BROWSER_ISSUES_FIXED.md` |
| Icon-only buttons have `aria-label` | ✅ | Mobile toggle, search close, user menu, dropdown close all carry `aria-label` |
| Decorative icons hidden from screen readers | ✅ | Every icon usage passes `decorative` → `aria-hidden="true"` on the underlying `<svg>` |
| Interactive icons get an accessible name | ✅ | `IconBase.vue` renders `<title>` from the `title` prop when not decorative |
| Form labels | ✅ pre-existing | `.ref-form-field` wraps every input in a `<label>`-equivalent structure |
| Escape closes dialogs/menus | ✅ fixed 2026-07-16 | Was **wrongly marked done** in the previous version of this file. `GlobalSearch` and `MobileNavigation` (via `v-focus-trap`) already had it; `ModuleNavigation` and `UserMenu` did not — fixed this pass, see `SMJ_BROWSER_ISSUES_FIXED.md` #1 |
| Active module indicated (keyboard + visual) | ✅ fixed 2026-07-16 | Desktop module buttons had no active-state at all (only the mobile drawer did, via Vue Router's automatic class). Added `aria-current="page"` + `.is-active` styling, see `SMJ_BROWSER_ISSUES_FIXED.md` #2 |
| Arrow-key navigation within module/user dropdown menus | ❌ not implemented | `GlobalSearch` has it (arrow up/down between results); the module and user dropdowns rely on Tab order only. Not fixed this pass — noted here rather than silently left off the list |
| Focus trap in modals | ✅ pre-existing | `v-focus-trap` directive on `MobileNavigation`; `ToastHost`/`ConfirmDialogHost` are unwired empty shells (see `SMJ_BROWSER_ISSUES_FIXED.md`) so this doesn't apply to them yet |
| Touch targets ≥ 44×44px | ✅ | `--ref-control-height: 44px` applied to buttons, inputs, icon buttons |
| Colour not the sole status indicator | ⚠️ partial | Status pills/badges rely on colour + text label (label is present), but no icon reinforcement was added to every badge — acceptable per WCAG since text is always present, not upgraded further this pass |
| `prefers-reduced-motion` respected | ✅ pre-existing | `responsive.css` |
| Automated contrast check (axe/Lighthouse) | ❌ not run | No tooling available in this environment |

Semantic colours were chosen to keep contrast reasonable against white
surfaces (`--ref-danger #EF4444` on `color-mix(..., white 94%)` backgrounds,
etc.) but exact contrast ratios were not measured.

**This is not a WCAG certification.** It's an honest per-item status list.
