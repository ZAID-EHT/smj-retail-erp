# SMJ Core Wholesale Workflow — Blockers

Truthful list of anything that blocks a requirement. Empty is good.

## Active blockers
- None blocking the core wholesale spine.

## Pre-existing issues found (not introduced by this mission)
- **`test_navigation_search.test_document_level_denial_and_report_denial_omit_results`
  errors on `staging.local`** with `DoesNotExistError: DocType None not found`.
  Traceback is entirely inside `my_store_ui/search.py::_document_results` →
  `frappe.get_meta(...)` while loading a registered search doctype whose Table field
  has a `None` child `options` on staging (a misconfigured/customised doctype in the
  staging dataset). `search.py` is **not** modified by this mission — verified via
  `git status`. Reproducible on the clean tree; staging-data specific. Deferred:
  hardening global search to skip a doctype whose meta fails to load is a small safe
  follow-up but is outside the wholesale-spine scope and would mix unrelated changes.

## Environment notes (not blockers)
- `staging.local` is a lean test site (small dataset). FIFO / pricing / stock
  acceptance tests must create their own controlled staging-only test data
  rather than relying on pre-existing demo volume.
- ERPNext is only importable inside a bench/site context (`bench --site … execute`
  or run-tests), not via bare `python3 -c "import erpnext"`.
