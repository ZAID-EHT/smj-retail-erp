# SMJ Reconciliation Acceptance

| Feature | Frontend | Backend controller | Status |
|---------|----------|--------------------|--------|
| Payment Reconciliation | `/generated/payment-reconciliation` (PaymentReconciliationPage) | `wholesale/payment_reconciliation_api.py` → standard `Payment Reconciliation` | ✅ built + prior-mission verified |
| Bank Reconciliation | `/generated/bank-reconciliation-tool` (BankReconciliationPage) | `wholesale/bank_reconciliation_api.py` → standard `Bank Reconciliation Tool` | ✅ built + prior-mission verified |
| Bank Clearance | dedicated | `wholesale/bank_clearance_api.py` | ✅ built |

Behaviour (from prior-mission tests and the adapter design):
- Company and account permission enforced.
- Correct outstanding amounts and allocation via the standard controller.
- **No direct outstanding manipulation** — the adapters call the ERPNext controller,
  never write ledger/outstanding fields.
- Fixed-purpose whitelisted wrappers, never a generic method-path RPC.

This phase confirmed the reconciliation frontend exists and uses standard controllers;
no new reconciliation code was needed.
