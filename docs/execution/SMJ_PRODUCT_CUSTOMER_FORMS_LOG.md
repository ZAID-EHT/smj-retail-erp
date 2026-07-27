# SMJ Product/Customer Forms — Batch Log
## Phase 0-1 (2026-07-27)
- Verified rc4 baseline clean. Tag pre-smj-product-customer-forms-20260727-2014.
- Backup 20260727_201426-*. Audited data model; mapped requested fields to existing/new.

## Phases 2-13 (2026-07-27)
- Custom fields + Department Price List installed (fixtures).
- Product quick-entry (auto P100001 ID / 5001 SKU, batch, 3 locations, 4 prices incl Department, atomic) — 13 tests.
- Customer quick-entry (address/contact linked, credit via credit_limits + custom_credit_days, Payment Type) — 15 tests.
- Batch/FIFO proven: 12,400 outgoing / 9,600 remaining — 1 test.
- Security (cost hidden, cross-company denied, atomic) — 7 tests.
- Two-company separation still green — 8 tests.
- Existing-data dry-run: 40 SKU + 2 price-category safe; 40 batch + contacts/addresses manual (not applied).
- Frontend forms (exact field order) + list columns; build clean.
- Full regression 405 tests, 0 failures. Browser 108/108 six viewports. site1 untouched.
