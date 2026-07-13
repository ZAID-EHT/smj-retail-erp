# Payment Entry lifecycle coverage

Retail ERP now provides Payment Entry list, detail, create, edit, submit, cancel, and amend routes under `/app/retail-erp/finance/payments`.

The server owns the Payment Entry schema and allowlists Payment Type, party, company, accounts, currencies, references, deductions, and amounts. Draft saves call the standard ERPNext `Payment Entry` controller; submissions and cancellations call `doc.submit()` and `doc.cancel()`, so GL, Payment Ledger, outstanding amounts, advances, exchange differences, and linked-document validation remain ERPNext-owned.

Allocation lookup delegates to ERPNext `get_outstanding_reference_documents`. Related references are returned only after read-permission checks and use custom Retail ERP routes when available.

Tested: internal transfer draft creation, submit, cancel, amend, state-aware actions, schema metadata validation, permission-aware API boundaries, and regression suites. Payment Entry submission is not a browser-side ledger implementation; it remains the standard controller operation.

Remaining dependencies: bank reconciliation, Payment Reconciliation, Payment Request workflows, purchase workflows, and outbound email are separate controlled stages.
