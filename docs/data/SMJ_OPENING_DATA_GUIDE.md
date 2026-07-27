# SMJ Opening Data Guide

## Opening stock

Use a standard **Stock Reconciliation** (or Material Receipt Stock Entry) to set
opening quantities and valuation. The difference account **must be a balance-sheet
account** (e.g. Temporary Opening / Opening Balance Equity), **not** the Expense
`Stock Adjustment` account — routing opening stock through an expense account is
exactly the defect corrected in `docs/finance/SMJ_OPENING_STOCK_ROOT_CAUSE.md`.

## Opening balances

Use ERPNext's standard opening-balance tooling (Opening Invoice Creation Tool for
receivables/payables; a dated opening Journal Entry against `Opening Balance Equity`
for other balances). Never write GL Entry directly.

## Via Data Management

Customer/Supplier/Item/Item Price/Warehouse master data can be bulk-loaded through
`/retail-erp/admin/data` before entering opening stock and balances.
