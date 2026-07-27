# SMJ Product/Customer Acceptance

All backend-verified on staging.local (savepoint/rollback; no residue).

## Product (test_product_quick_entry 13, test_quick_entry_security 7)
| Requirement | Status |
|-------------|--------|
| Product ID auto P100001 | ✅ |
| SKU auto 5001 | ✅ |
| IDs unique across creations | ✅ |
| Product Name required | ✅ |
| Category validated | ✅ |
| Negative values rejected | ✅ |
| Duplicate stock location rejected | ✅ |
| Cross-company warehouse denied | ✅ |
| 3 stock locations + reorder saved | ✅ |
| Cost→Standard Buying Item Price | ✅ |
| Wholesale/Retail/Department Item Price (selling only) | ✅ |
| No duplicate Item Price | ✅ |
| Edit keeps ID/SKU, updates price atomically | ✅ |
| New stock product batch-managed | ✅ |
| Atomic rollback on failure | ✅ (internal savepoint) |
| Cost price hidden from Sales user | ✅ |
| Sales User cannot create; Item Manager refused atomically | ✅ |
| Arbitrary field/payload rejected; Guest rejected | ✅ |

## Batch & FIFO (test_batch_fifo 1)
| Requirement | Status |
|-------------|--------|
| Receipt creates batches | ✅ (2 batches) |
| FIFO 10@1000 + 10@1200, issue 12 → outgoing 12,400 | ✅ |
| Remaining 8 @ 1200 = 9,600 | ✅ |
| Read from standard Stock Ledger, no direct writes | ✅ |

## Customer (test_customer_quick_entry 15)
| Requirement | Status |
|-------------|--------|
| Customer required | ✅ |
| Address + Contact created & linked | ✅ |
| No duplicate address/contact on edit | ✅ |
| WhatsApp "same as contact" | ✅ |
| Default Price Category = Retail | ✅ |
| Wholesale/Department categories | ✅ |
| Buying price list rejected | ✅ |
| Non-Credit defaults 0 | ✅ |
| Credit requires limit; stores limit+days | ✅ |
| All business fields persist | ✅ |
| Created Date present/read-only | ✅ |
| Duplicate-name warning | ✅ |
| Arbitrary field rejected; atomic rollback | ✅ |

## Business Nature
Shown **once** on the form (spreadsheet duplicate treated as accidental).

## Existing data
Dry-run on staging (docs/data/SMJ_EXISTING_PRODUCT_CUSTOMER_MIGRATION.md): 40 SKU + 2
price-category safe defaults; 40 batch-tracking + missing contacts/addresses flagged
MANUAL. Not auto-applied.
