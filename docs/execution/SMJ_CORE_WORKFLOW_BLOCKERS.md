# SMJ Core Wholesale Workflow — Blockers

Truthful list of anything that blocks a requirement. Empty is good.

## Active blockers
- None blocking the core wholesale spine.

## Confirmed defect — item pricing stored only in custom fields (needs business decision)
- `form_api._apply_item_pricing` writes computed retail/wholesale prices to
  `custom_retail_price` / `custom_wholesale_price` only — it does **not** create
  standard `Item Price` records, so those prices are invisible to ERPNext's pricing
  engine (and therefore to Smart Sales customer pricing). The fix (upsert Item Price
  on the retail/wholesale price lists) needs a **price-list mapping decision**:
  staging has `Retail Price List` + `Preferred Customer Price List` but no
  `Wholesale Price List`. Not auto-fixed to avoid guessing the mapping. See
  `docs/ui/SMJ_SIMPLIFIED_ENTRY_FORMS.md` for the recommended implementation.

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
