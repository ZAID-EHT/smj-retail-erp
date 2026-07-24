# SMJ Core Wholesale Workflow — Blockers

Truthful list of anything that blocks a requirement. Empty is good.

## Active blockers
- None at mission start.

## Environment notes (not blockers)
- `staging.local` is a lean test site (small dataset). FIFO / pricing / stock
  acceptance tests must create their own controlled staging-only test data
  rather than relying on pre-existing demo volume.
- ERPNext is only importable inside a bench/site context (`bench --site … execute`
  or run-tests), not via bare `python3 -c "import erpnext"`.
