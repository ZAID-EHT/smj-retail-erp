# Delivery Note and Sales Invoice lifecycle coverage

The Retail ERP shell now exposes secure, allowlisted lifecycle actions for Delivery Note and Sales Invoice records.

Implemented in this stage:

- Draft create/edit through the shared form engine, including mapped drafts.
- Server-side submit, cancel, and amend actions through `doc.submit()`, `doc.cancel()`, and standard amendment behavior.
- Delivery Note → Sales Invoice mapping and Sales Invoice → Draft Payment Entry mapping through ERPNext helpers.
- Delivery Note and Sales Invoice return/credit-note mapping through the standard return controller.
- State-aware permissions, stale-document checks, workflow blocking, idempotent mapped creation, print-format selection, print preview, and PDF endpoints.
- Custom list, detail, edit, and payment-entry routes under `/app/retail-erp/*`.

ERPNext remains responsible for stock ledger, bin, serial/batch, tax, GL, payment ledger, linked-document, and workflow validation. Delivery Note and Sales Invoice submission therefore use the normal ERPNext controllers and are not browser-calculated.

Not implemented in this stage: Payment Entry submission, Delivery Note/Sales Invoice email dispatch, bank reconciliation, and specialized Delivery Note actions such as Shipment, Installation Note, Packing Slip, Delivery Trip, Dunning, Invoice Discounting, and Maintenance Schedule. These remain explicit feature-parity dependencies rather than hidden Desk redirects.
