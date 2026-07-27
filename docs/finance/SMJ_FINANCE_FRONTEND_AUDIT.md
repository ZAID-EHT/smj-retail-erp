# SMJ Finance Frontend Audit

Verified 2026-07-27 by resolving each route through the server-side registry.

## Coverage

| Capability | Route | Status |
|-----------|-------|--------|
| Chart of Accounts | `/finance/chart-of-accounts` | ✅ tree view (generated) |
| Fiscal Year | `/finance/fiscal-year` | ✅ list (generated) |
| Cost Center | `/finance/cost-centers` | ✅ tree (generated) |
| Company management | `/admin/companies` | ✅ list (generated) + setup wizard create |
| Payment Reconciliation | `/generated/payment-reconciliation` | ✅ dedicated adapter (prior mission, `wholesale/payment_reconciliation_api.py`) |
| Bank Reconciliation Tool | `/generated/bank-reconciliation-tool` | ✅ dedicated adapter (`wholesale/bank_reconciliation_api.py`) |
| Bank Clearance | `/…` | ✅ `wholesale/bank_clearance_api.py` |
| Journal Entry | via generated engine | ✅ generated CRUD |
| Taxes & Charges Templates | via generated engine | ✅ generated CRUD |
| Tax Category / Tax Rule | via generated engine | ✅ generated CRUD |
| Payment Terms Template | via generated engine | ✅ generated CRUD |
| Currency Exchange | via generated engine | ✅ generated CRUD |
| GL / Trial Balance / P&L / Balance Sheet / Cash Flow | report routes | ✅ (BLOCKERS.md pass 5: drill-downs done, 3 real bugs fixed) |

## Conclusion

The launch-critical finance frontend is **already present** — Payment and Bank
Reconciliation have dedicated adapters built in prior missions, and the remaining
setup/config DocTypes are served by the System-Manager-gated generated engine. This
phase required **audit and verification**, not new construction. No launch-critical
finance gap remains; the one finance *data* issue (opening-stock P&L) is handled in
`SMJ_OPENING_STOCK_*` / `SMJ_FINANCIAL_RECONCILIATION.md`.

## Standard-controller guarantee

All reconciliation uses standard ERPNext controllers (verified in prior missions'
`test_single_finance_tools`, `test_accounts_action_parity`): no direct outstanding
manipulation, correct allocation, company/account permission enforced.
