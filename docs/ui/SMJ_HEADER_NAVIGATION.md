# SMJ Retail ERP — Header & Navigation

## Structure

`AppShell.vue` → `AppHeader.vue`, composed of:

- `CompanyBrand.vue` — logo mark (SmjHomeBuilding icon fallback when no
  `retailBranding.logo` is injected) + live company name from session/Frappe
  defaults + "SMJ Retail ERP · ERPNext v15" subtitle.
- `HeaderPageActions.vue` — renders whatever the current page registered via
  `usePageActions()` (see `frontend/src/composables/pageActions.js`). Empty
  by default; no dead buttons.
- `ModuleNavigation.vue` — horizontal module bar, driven entirely by the
  server-permitted navigation payload (`get_permitted_navigation()` in
  `my_store_ui/services/frontend_routes.py`) when authenticated, or the
  static `navigationModules` fallback otherwise. Each module now renders its
  real SMJ icon (`src/components/icons/moduleIconMap.js` maps the existing
  `meta.icon` string — `home`, `cart`, `sales`, `bag`, `box`, `finance`,
  `settings`, `users`, `chart`, `shield` — to an SMJ icon component; this
  mapping required no route changes).
- `GlobalSearch.vue` — unchanged behaviour (permission-filtered, debounced,
  keyboard-navigable, `Ctrl+G` shortcut, grouped results), now with a real
  `SmjSearch` icon instead of a `⌕` glyph.
- `UserMenu.vue` — live authenticated user (no hardcoded name), initials
  avatar, "My Profile" (opens the real Frappe `/app/user-profile` page —
  intentionally not a fake link), a functional "Keyboard shortcuts" panel,
  and Logout.

On screens narrower than 1180px the module row collapses behind a
`SmjMenu` hamburger button that opens `MobileNavigation.vue`, a full-screen
drawer listing every permitted module and its links with real icons.

## No permanent sidebar

Confirmed by inspection before starting (`grep -ri sidebar` returned no
matches) and preserved throughout — `AppShell.vue` has no side-navigation
element in any breakpoint.

## Page actions in the header — current state

The `usePageActions()` composable and `HeaderPageActions.vue` component are
in place as the shared mechanism for pages to push New/Import/Export/Print/
Refresh into the header's left side. **No page has been wired to call it
yet** — every existing page (universal and handcrafted) still renders its
own action buttons in its own page banner, directly under the header, where
they are already permission-aware and already tested. Relocating dozens of
pages' actions into the header was judged too large a change to do safely
inside this pass; the infrastructure exists so a follow-up can wire it in
page by page without further shell changes. This is the single biggest gap
against the original spec and is called out again in the final report.

## Notifications

The spec calls for a header notification icon. No notification backend
exists anywhere in this codebase (`grep -ri notification` found only the
icon component itself). Adding one would mean inventing a new feature,
which the mission explicitly forbids ("do not create a fake
implementation"). The icon was deliberately **not** added to avoid a dead
button; `SmjNotification.vue` exists in the icon pack for when a real
backend is built.
