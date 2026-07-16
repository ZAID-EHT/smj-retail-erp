# SMJ Retail ERP — Header & Navigation

## Structure

`AppShell.vue` → `AppHeader.vue`, composed of:

- `CompanyBrand.vue` — "SMJ Retail ERP" identity, ERPNext v15 subtitle and
  the company name. The SMJ mark is used when the configured image is the
  generic product placeholder; a real configured company logo still wins.
- `HeaderPageActions.vue` — renders whatever the current page registered via
  `usePageActions()` (see `frontend/src/composables/pageActions.js`). Empty
  by default; no dead buttons.
- `ModuleNavigation.vue` — horizontal module bar, driven entirely by the
  server-permitted navigation payload (`get_permitted_navigation()` in
  `my_store_ui/services/frontend_routes.py`) when authenticated. The desktop
  bar presents the nine reference modules; permitted Smart Sales and POS
  entries are grouped under Sales instead of consuming extra top-level space.
  Dropdowns show seven links first and expose every remaining permitted link
  through an explicit Show all control. Each module renders its
  real SMJ icon (`src/components/icons/moduleIconMap.js` maps the existing
  `meta.icon` string — `home`, `cart`, `sales`, `bag`, `box`, `finance`,
  `settings`, `users`, `chart`, `shield` — to an SMJ icon component; this
  mapping required no route changes).
- `GlobalSearch.vue` — permission-filtered, debounced, keyboard-navigable and
  available with `Ctrl+G`. Results are organised into Pages & Functions,
  Reports and Documents. The server searches only registered routes, approved
  reports and allowlisted DocTypes; friendly terms such as Smart Sales,
  purchase receipt and petty cash resolve to the appropriate permitted page.
- `UserMenu.vue` — live authenticated user (no hardcoded name), initials
  avatar, server-returned primary role, "My Profile", keyboard shortcuts and
  Logout.

On screens narrower than 1370px the module row collapses behind a
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

## Notifications and messages

The reference utility icons are present, but no notification/message count is
invented. Until a permission-aware backend adapter exists they route to the
Retail ERP Feature Unavailable page rather than opening Desk or pretending to
show live data.
