# SMJ Core Wholesale Workflow — Blockers

Truthful list of anything that blocks a requirement. Empty is good.

## Active blockers
- **None.** Nothing in this repository is blocked.

## External setup required (not a code defect, cannot be fixed from this repo)
- **No outgoing `Email Account` on `staging.local`.** 0 accounts with
  `enable_outgoing=1`, no default outgoing account, no site-config SMTP fallback.
  Welcome and password-reset emails therefore cannot be delivered, and onboarding
  uses an administrator-set password instead. The Access Control screen reports this
  truthfully rather than implying mail was sent. Detail and the fix procedure:
  `docs/security/SMJ_EMAIL_ONBOARDING_STATUS.md`.

## Resolved — Access Control was a dead route (found in a real browser)
- **Fixed 2026-07-26.** The new `/admin/access-control` screen rendered nothing but
  "Page not found" at all six viewports. The SPA runs every navigation through the
  server-side `authorize_frontend_route` guard, and the route was absent from
  `ROUTE_REGISTRY`, so a fully working page resolved to not-found. Registered it,
  System Manager gated like the rest of `/admin`; the endpoints behind it still
  re-check that server-side.
- Registering it exposed a second, **pre-existing latent** defect: an optional regex
  group that does not participate yields `None`, and `unquote(None)` raises — so
  `/admin/access-control` returned **HTTP 500** while `/admin/access-control/access`
  worked. `resolve_frontend_route` now treats a non-participating group as an absent
  parameter. This would have hit any future optional route group.
- Neither defect was reachable by the existing test suites; both were found by the
  six-viewport browser matrix. Regression coverage:
  `test_standalone_frontend.test_access_control_resolves_with_and_without_a_tab`.

## Resolved — item pricing now creates standard `Item Price` records
- **Fixed 2026-07-25, verified and corrected 2026-07-26.** `save_entity_form` now
  calls `form_api._sync_item_prices()` after saving an Item, upserting standard
  `Item Price` documents for purchase, wholesale and retail. Measured severity of the
  original defect: site-wide `Item Price` count was **0**, so no product created
  through the form had a price the pricing engine could see.
- The earlier claim that staging has **no** `Wholesale Price List` was **wrong** — it
  exists. The mapping was settled from data, not guessed: retail → `Retail Price List`
  (23 of 26 customers default to it), wholesale → `Wholesale Price List`, purchase →
  Buying Settings `buying_price_list` (`Standard Buying`).
- Two configuration corrections were required on `Wholesale Price List`:
  `selling` 0 → 1 (2026-07-25), then `buying` 1 → 0 (2026-07-26). The earlier session
  deliberately left `buying=1`; that was wrong, because ERPNext stamps the list flags
  onto each `Item Price` row, so the marked-up wholesale rate was selectable as a
  **purchase cost**. Both changes were made only after verifying 0 Item Prices, 0
  customers, 0 suppliers, 0 customer groups and 0 purchasing documents referenced the
  list. Applied by `dev_scripts/fix_wholesale_price_list_selling_only.py`, which
  re-checks all of those and refuses to act if any is non-zero.
- Proof it actually works: `test_synced_price_is_visible_to_the_pricing_engine`
  asserts `get_item_details` returns the synced retail rate. Full detail in
  `docs/ui/SMJ_SIMPLIFIED_ENTRY_FORMS.md`.

## Resolved — the price sync would have broken product creation for `Item Manager`
- Found 2026-07-26 while verifying the previous session's uncommitted code. **The
  test suite could not have caught this**: it runs as Administrator, which bypasses
  permission checks.
- `Item Price` is master data in stock ERPNext v15 — `item_price.json` grants it to
  `Sales Master Manager` and `Purchase Master Manager` only (confirmed against the
  `apps/erpnext` source and the live site; no `Custom DocPerm` overrides exist).
  `Item Manager` is the only non-Administrator role on this site that can create an
  `Item`, and it has **no** `Item Price` permission at all.
- Effect of the unfixed code: saving any priced product as an Item Manager raised a
  bare `PermissionError` from inside the `Item Price` insert — product creation was
  broken for that role entirely.
- **Fixed** by planning all price changes first and gating on the exact permissions
  the plan requires, throwing one actionable message that names the roles. No
  `ignore_permissions` was added. An unpriced product still saves fine, and the
  refusal is atomic (no partially created product). Guarded by three tests.

## Resolved — navigation search failure (root cause corrected)
- **`test_navigation_search.test_document_level_denial_and_report_denial_omit_results`**
  errored with `DoesNotExistError: DocType None not found`. **Fixed.**
- The earlier diagnosis in this file was **wrong**. It was *not* staging data and
  *not* a misconfigured registry entry with a `None` child `options`. Verified
  empirically: every `SEARCH_REGISTRY` doctype loads cleanly on staging, no
  `ENTITY_ROUTES`/`SEARCH_REGISTRY` entry has a missing or empty doctype (202
  entity routes checked), and `Custom DocPerm(parent="Customer")` count is `0`.
- **Actual root cause — a test-layer defect.** `my_store_ui.search.frappe` *is* the
  frappe module, so `patch("my_store_ui.search.frappe.get_list", return_value=[…])`
  replaced `frappe.get_list` **process-wide**. `frappe.get_all` delegates to
  `get_list`, and `Meta.process()` → `set_custom_permissions()` calls
  `frappe.get_all("Custom DocPerm", …)` while loading metadata. With a cold meta
  cache (this test sorts first in the module) the mock returned a fake *Customer*
  row that has no `doctype` key, so `Document(d)` left `self.doctype = None` and
  `BaseDocument.__init__` → `self.meta` → `frappe.get_meta(None)` threw. Warm cache
  hid it, which is why it looked data/order dependent.
- **Fixes applied (two layers):**
  1. *Test*: the `get_list` stub now only answers for the searched doctype and
     delegates all other doctypes to the real implementation, so frappe internals
     no longer receive fake rows.
  2. *Product hardening*: new `search._searchable_meta()` skips a registry entry
     whose DocType is missing/renamed/`None` instead of failing the whole request,
     clears the queued `throw` message so it cannot leak into an unrelated search
     response, and logs a warning. Only `DoesNotExistError` is absorbed — any other
     metadata error still propagates. No DocType substitution, no permission
     widening: skipped entries return nothing and every surviving entry is still
     `has_permission`-checked.
- Regression coverage: `test_unusable_registry_doctype_is_skipped_without_breaking_search`
  (removed / `None` / empty doctype, mixed valid+stale registry, end-to-end
  `global_search`) and `test_unusable_registry_entry_does_not_bypass_permissions`.
  Module now **11 tests green** (was 9 + 1 error).

## Environment notes (not blockers)
- `staging.local` is a lean test site (small dataset). FIFO / pricing / stock
  acceptance tests must create their own controlled staging-only test data
  rather than relying on pre-existing demo volume.
- ERPNext is only importable inside a bench/site context (`bench --site … execute`
  or run-tests), not via bare `python3 -c "import erpnext"`.
