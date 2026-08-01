# SMJ Wholesale Operations — Mission State

## Phase 0 preflight (2026-08-01)

- Branch: `full-feature-parity`
- Start commit: `4ea098e` (worktree had verified-but-uncommitted work, committed as `8311990`)
- Mission base commit: `8311990`
- Recovery tag: `pre-smj-wholesale-operations-20260801-1121`
- Backup: `sites/staging.local/private/backups/20260801_112204-staging_local-*`
  (database.sql.gz 1.7 MiB, files.tar, private-files.tar, site_config_backup.json)
- Test site: `staging.local`. Protected: `site1.local`.

### site1.local integrity fingerprint (read-only, re-verified at mission end)

```
{"Batch": 0, "Customer": 3, "Delivery Note": 0, "GL Entry": 44, "Item": 11,
 "Payment Entry": 5, "Purchase Invoice": 6, "Purchase Order": 10,
 "Purchase Receipt": 0, "Sales Invoice": 7, "Sales Order": 7,
 "Stock Ledger Entry": 17, "User": 3}
SHA256 f51fedb5a9ac68e27b1515daee5cdf2f90490a22c07925960dd0acb4d123d9c3
```

## Previous-mission verification (rc7 claim)

**`v1.0.0-rc7` was never created.** Latest release tag is `v1.0.0-rc6` at `62dd59f`.
Two feature commits landed after it without a release. Previous-mission item status:

| Previous-mission item | Status at Phase 0 | Evidence |
|---|---|---|
| Real Product image uploads | Complete | `4ea098e` ImageUpload.vue → `/api/method/upload_file` |
| Product image display | To verify | list/detail column presence unconfirmed |
| Carton UOM | **Incomplete** | only `custom_carton_qty` Float on Item; no real UOM + conversion factor |
| Preferred Warehouses | Complete | `custom_stock_location_1/2/3`, company-scoped |
| FIFO Delivery allocation | **Incomplete** | FIFO *valuation* proven only; no delivery-time batch allocation API |
| Customer pricing + credit | Complete | `test_customer_category_pricing` (3), `wholesale/credit.py` |
| Existing-data safe migration | To verify | `quick_entry/existing_data.py` present, dry-run only |
| Replenishment workflow | **Incomplete** | only `restock_qty` → Item Reorder on the product form |
| Release tag v1.0.0-rc7 | **Not created** | tag list |

## Existing wholesale infrastructure found (do not duplicate)

| Module | Provides |
|---|---|
| `wholesale/transaction_id.py` | TRX id generation + propagation hooks |
| `wholesale/register.py` | `get_wholesale_transactions`, `get_transaction_timeline` |
| `wholesale/reservation.py` | availability, reserve/unreserve, bin locking, expiry |
| `wholesale/credit.py` | credit status, delivery gate decision, manager gate |
| `api.py` | `get_bootstrap`, `get_cart_pricing`, `create_draft_sales_order` |
| `payment_api.py`, `sales_order_actions.py`, `document_actions.py` | document actions |
| Frontend | `SmartSalesPage`, `WholesaleTransactionsPage`, `HomeDashboardPage` |

## Phase status

Phase 0 preflight: done.
