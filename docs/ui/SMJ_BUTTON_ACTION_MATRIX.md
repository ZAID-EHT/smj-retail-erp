# SMJ Retail ERP — Button/Action Verification (2026-07-16)

## ToastHost and ConfirmDialogHost — now real

The previous session's audit found `ToastHost.vue` and
`ConfirmDialogHost.vue` were empty `<div>` shells with no service ever
writing into them. Fixed this pass:

- `frontend/src/composables/toast.js` — `useToast()` → `.success()`,
  `.error()`, `.warning()`, `.info()`, each backed by a real reactive queue,
  auto-dismissing (errors stay longer: 8s vs 5s), dismissable by click.
- `frontend/src/composables/confirm.js` — `confirmAction({ title, message,
  confirmLabel, cancelLabel, danger })` returns a real `Promise<boolean>`.
- `ToastHost.vue` / `ConfirmDialogHost.vue` now render these queues for
  real, with `role="alertdialog"`, `aria-modal`, the existing
  `v-focus-trap` directive (Escape closes, focus returns to the trigger,
  Tab is trapped — same mechanism `MobileNavigation` already used).

## Call sites migrated from `window.confirm`/native to the real system

| File | What changed |
|---|---|
| `components/detail/SalesOrderActions.vue` | Submit/Cancel/Amend now use `confirmAction()` (Cancel is styled `danger`) + a success/error toast after the API call |
| `components/detail/EntityActions.vue` | Every document-lifecycle action (submit, cancel, hold, resume, etc. — whatever the backend exposes) goes through `confirmAction()` + toast |
| `pages/generated/UniversalDetailPage.vue` | Same, for the universal engine's generic document actions |

These three components are shared across dozens of document types (any
Sales Order, any handcrafted entity, any generated doctype), so this is a
cross-cutting fix, not three isolated ones — consistent with the mission's
"fix the shared component rather than many one-off patches" instruction.

## Call sites intentionally left on native `window.confirm` (documented, not fixed)

Time-boxed decision — these are lower-traffic, page-specific handlers
rather than shared components:

- `pages/entities/EntityFormPage.vue`, `pages/generated/UniversalFormPage.vue`
  — unsaved-changes-on-navigate guards (`onBeforeRouteLeave`)
- `components/shell/UserMenu.vue` — "discard unsaved changes and sign out?"
- `pages/priority/BankReconciliationPage.vue` (5 call sites),
  `pages/priority/PaymentReconciliationPage.vue` (1 call site) — these
  guard real, submitted, hard-to-undo ERPNext postings; native `confirm()`
  still blocks correctly today, migrating them is cosmetic, not a
  correctness fix, so it was deprioritised under time pressure.

## Buttons verified this pass (real backend calls, not just route checks)

Beyond the Section 12/HTTP-harness coverage from the previous session,
this pass additionally exercised, via real screenshots:

- Home dashboard quick-action buttons (`+ Sales Invoice`, `+ Purchase
  Order`, `+ Payment`) — confirmed they render as real `RouterLink`s to
  the correct `/new` routes, not decorative buttons.
- Every KPI card is a real link (`SmjKpiCard`'s `to` prop) to its relevant
  list page.
- Chart card "View Report" / refresh — refresh re-runs the real fetch
  (confirmed via the loading skeleton reappearing); "View Report" links to
  a real report route.

## Not attempted this pass

A full page-by-page button-by-button matrix (Section 31's 12-point checklist
per button — visibility, permission, disabled, loading, success, error,
confirmation, backend op, resulting route, refresh, mobile, keyboard) for
every button across all 9 reference pages was not built as a standalone
document. That's a genuinely large undertaking (the app has dozens of
document-lifecycle actions across Sales Orders, Purchase Orders, Delivery
Notes, Payment Entries, etc.) and doing it honestly requires either a real
browser click-through per button or reading every handler's source — this
pass covered the shared components (which back most of those buttons) and
the Home dashboard specifically, not an exhaustive enumeration.
