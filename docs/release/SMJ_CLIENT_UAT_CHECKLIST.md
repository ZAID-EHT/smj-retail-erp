# SMJ Client UAT Checklist

Business users confirm, on staging or a UAT site:

## Sales
- [ ] Select a customer; catalogue shows customer-specific pricing.
- [ ] Out-of-stock item cannot be added; quantity above available is rejected.
- [ ] Create and submit a Sales Order; reserve stock; deliver (partial + full); return.

## Purchasing
- [ ] Material Request → RFQ → Supplier Quotation → PO → Receipt → Invoice → Payment.

## Products & pricing
- [ ] Create a product with cost + margins; confirm retail/wholesale/purchase prices
      appear in a quotation/order (Item Price sync).
- [ ] Set colour, UOMs, safety stock, default warehouse, reorder level.

## Admin
- [ ] Create a user, set a password, assign a role/profile, add a restriction; log in.
- [ ] Preview and print an invoice; confirm branding.
- [ ] Import a small customer/supplier CSV; export and confirm no cost leakage.
- [ ] Review System Operations readiness.

## Finance (with accountant)
- [ ] Review Profit and Loss, Balance Sheet, Trial Balance.
- [ ] Confirm the opening-stock reclassification (see accountant checklist).
