# SMJ Retail ERP — Browser/UI Issues Found and Fixed (2026-07-16)

Found by deep code review of the application shell (no browser was
available — see `SMJ_BROWSER_VERIFICATION.md`). All four are real,
reproducible-by-reading-the-code defects, not speculative.

## Fixed

### 1. Module navigation dropdown and user menu did not close on Escape

**Files:** `frontend/src/components/shell/ModuleNavigation.vue`,
`frontend/src/components/shell/UserMenu.vue`

Both dropdowns only closed on an outside click. `GlobalSearch.vue` and
`MobileNavigation.vue` (via the shared `v-focus-trap` directive) both
already handle `Escape` correctly — these two were the only shell elements
that didn't, which is a direct violation of Section 16's "Escape closes
dialogs and menus" and, worse, directly contradicted the UserMenu's own new
"Keyboard shortcuts" panel, which claims `Esc` closes menus. Fixed both to
listen for `Escape`, close, and return focus to the button that opened them
(matching the pattern `focusTrap.js` already uses elsewhere).

### 2. No visual indication of the active module on desktop

**File:** `frontend/src/components/shell/ModuleNavigation.vue`,
`frontend/src/design/base.css`

The mobile drawer highlights the active module via Vue Router's automatic
`router-link-active` class, but the desktop module buttons are plain
`<button>` elements (they open a dropdown, they aren't links), so Vue
Router's automatic class never applied to them — there was no way to tell
which module you were in from the header. Added `isActiveModule()` (route
path prefix match against `module.path`), wired to `aria-current="page"`
and an `.is-active` class with a visible bottom-border indicator.

### 3. Module navigation had no overflow safety net

**File:** `frontend/src/design/base.css`

With the current 11 permitted modules (`home, smart-sales, sales,
purchases, inventory, finance, operations, crm, reports, pos, admin` — the
navigation payload confirmed via the HTTP harness has grown since the
original desktop breakpoint math was written) and the existing `≤1450px`
breakpoint only shrinking padding/hiding icons, the 1181–1450px range was a
real risk of the module row overflowing the header rather than the mission's
required "horizontal scrolling" or "colourful more mega-menu" fallback.
Added `overflow-x: auto` + `white-space: nowrap` on the module row as a
safety net — the mission explicitly endorses this pattern ("Use horizontal
scrolling... do not wrap modules into three messy rows"). This could not be
visually confirmed (no browser), but it is strictly safer than the previous
CSS, which had no overflow handling at all.

## Investigated, found to be a false alarm — corrected

### Skip-to-content link

Initially flagged as missing because a grep across `**/*.vue` found no
`<a>` element with `href="#retail-erp-main"`. It exists — in
`my_store_ui/www/retail_erp.html`, the server-rendered HTML shell that
wraps the Vue mount point, not in any Vue component. A grep scoped to only
`.vue`/`.js` files missed it. A skip link was briefly added to
`AppShell.vue` and then reverted once the real one was found, to avoid
shipping a duplicate. **Net change: none.** This also means the previous
session's `SMJ_ACCESSIBILITY_CHECKLIST.md` claim ("Skip-to-content link:
pre-existing, kept") was actually correct — it just wasn't re-verified
carefully enough this time before being flagged. Recorded here for honesty
about the false start.

## Found, documented as a real gap, not fixed this pass

### `ToastHost.vue` and `ConfirmDialogHost.vue` are empty, unwired shells

**Files:** `frontend/src/components/feedback/ToastHost.vue`,
`frontend/src/components/feedback/ConfirmDialogHost.vue`

Both are rendered in `AppShell.vue` and both are literally a single empty
`<div>` with an `aria-live` attribute — there is no service, composable, or
store anywhere in the codebase (`grep -rn toast src/services src/stores` and
`src/composables` both return nothing) that ever puts content into them.
Destructive-action confirmation currently goes through the native
`window.confirm()` (see `UserMenu.vue`'s logout handler and
`SmartSalesPage.vue`'s cart-remove handler) instead of the custom dialog
host. This predates this UI pass — it isn't something introduced by the
design-system rebuild.

**Why not fixed now:** building a real toast/confirm system and rewiring
every success/error/destructive-action call site across the app to use it
is a genuine feature addition, not a "correction" — it fails the
proportionality test against the rest of this mission's fixes, and doing it
hastily risks silently swallowing errors that currently at least reach
`window.alert`/`window.confirm` or the page's own inline error state.
Documented here per the mission's own instruction to record legitimate
blockers rather than leave them silently unaddressed. Recommended follow-up:
a small `useToast()` / `useConfirm()` composable, then migrate call sites
incrementally.

## Not investigated this pass

Deeper per-page interaction bugs (cart math edge cases, form validation
edge cases, etc.) were not audited — this pass focused on the shared
application shell, which is the highest-leverage place to find and fix
cross-cutting defects, consistent with Section 17's instruction to "fix the
shared component rather than applying many one-off patches" when the same
class of problem could appear across pages.
