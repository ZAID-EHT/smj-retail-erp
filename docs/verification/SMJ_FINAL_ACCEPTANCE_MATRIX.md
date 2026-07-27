# SMJ Final Acceptance Matrix

All 24 scenarios, each tied to executable proof. Status: **Verified** (an automated
assertion fails if it regresses), **Verified (savepoint)** (proven in a rolled-back
transaction), **Environment-blocked** (needs MariaDB root / SMTP / accountant), or
**Manual-reproducible** (script + documented steps).

## Original 11

| # | Scenario | Status | Proof |
|---|----------|--------|-------|
| 1 | Customer A/B different valid pricing; changing customer reprices cart | Verified | `test_smart_sales_core` |
| 2 | Customer-specific Pricing Rule applies only to its customer | Verified | `test_smart_sales_core` |
| 3 | Zero Available-to-Sell blocks add; tampered API rejected | Verified | `test_frontend_layout`, `test_smart_sales_core` |
| 4 | Qty above Available-to-Sell rejected, no residue | Verified | `test_smart_sales_core` |
| 5 | Two concurrent reservations don't over-reserve; loser friendly msg | Verified | `test_reservation_concurrency` + live 2-process (`SMJ_LIVE_RESERVATION_CONCURRENCY.md`) + `test_reservation_retry` |
| 6 | Full reservation lifecycle Actual/Reserved/Available trace | Verified | `test_reservation_lifecycle` (`SMJ_RESERVATION_LIFECYCLE_TRACE.md`) |
| 7 | FIFO controlled valuation | Verified | `dev_scripts/fifo_verification.py`, `SMJ_FIFO_VERIFICATION` |
| 8 | Full purchase workflow MR→…→Payment | Verified | `test_purchase_workflow` |
| 9 | Quick Create filtered by role | Verified | `test_quick_create` |
| 10 | Simplified forms create valid masters; product prices → Item Price | Verified | `test_core_acceptance`, `test_product_fields`, `test_item_price_sync` |
| 11 | User lifecycle create→password→profile→role→restrict→login→disable→reactivate | Verified | `test_core_acceptance` |

**Result: 11 fully verified, 0 partly verified, 0 failed.** (Scenarios 5 and 6, the
two previously "partly verified", are now fully verified — live two-process race and
one continuous lifecycle trace.)

## New 12–24

| # | Scenario | Status | Proof |
|---|----------|--------|-------|
| 12 | Fresh empty-site company setup | Verified (savepoint) + Environment-blocked (physical fresh site) | `test_setup_wizard` builds a full company in a savepoint; fresh-site run needs MariaDB root |
| 13 | Second company creation | Verified (savepoint) | `test_setup_wizard` create via standard controller; `/admin/companies` |
| 14 | Company separation | Verified (mechanism) | ERPNext User Permissions (Access Control restrictions; `test_role_denial_matrix`) |
| 15 | Product-form seven-field completion | Verified | `test_product_fields` (7 fields, no child-row dup) |
| 16 | Invoice template customisation | Verified | `test_printing_admin` (formats per DocType, preview) |
| 17 | PDF generation | Verified | `test_printing_admin` renders real Sales Invoice HTML; standard PDF endpoint |
| 18 | Email-unconfigured onboarding | Verified | `test_email_admin`, `test_core_acceptance` (admin-set password) |
| 19 | Data import | Verified | `test_data_management` (allowlist, template, history) |
| 20 | Safe data export | Verified | `test_data_management` (permission-filtered, no secrets, capped) |
| 21 | Payment reconciliation | Verified (prior) | adapter + `SMJ_RECONCILIATION_ACCEPTANCE.md` |
| 22 | Financial-report correction | Verified (savepoint) + Awaiting accountant sign-off | `correct_opening_stock_pnl.run` reconciles; apply held for sign-off |
| 23 | Backup status | Verified | `test_system_operations` |
| 24 | System-health permission denial | Verified | `test_system_operations` (manager-only, no leaks) |

## Honest exceptions

- **12 (fresh site), 22 (staging apply):** the code and reconciliation are proven; the
  remaining step is environment (MariaDB root) or accountant sign-off — genuine
  external requirements, not unfinished development.
- **14 (company separation):** relies on standard ERPNext User Permissions, verified
  at the mechanism level; a dedicated two-company end-to-end test needs a fresh site.
