# SMJ RC4 Wholesale Frontend Audit

Classification: **V** verified · **U** universal engine · **D** dedicated page ·
**Xcfg** implemented, needs external config · **Xuat** needs UAT · **Opt** optional ·
**N** not required.

| Area | Class | Notes |
|------|:----:|-------|
| First-time setup | V/D | /setup |
| Companies / Company Setup | V/D | landing + generated CRUD + wizard |
| Fiscal Years / CoA / Cost Centers | U | /finance/* |
| Warehouses | U | + default warehouse on Product form |
| Taxes / Price Lists | U/V | templates via CRUD; price lists ensured by setup |
| Customer / Supplier / Product | V/D | curated forms |
| Smart Sales / SO / Reservations | V/D | customer-first + concurrency + lifecycle |
| Delivery / Sales Invoice / Payment | V/D | curated + mapped flows |
| Purchasing / PR / PI / Landed Costs / Returns | V | test_purchase_workflow; returns in lifecycle |
| Credit / Debit Notes | V | is_return variants; printable |
| Stock Entries / Reconciliation / FIFO | V | verified |
| Reports / Reconciliation | V/D | drill-downs + adapters |
| Printing / PDF | V/D | landing + preview + secure download |
| Email | Xcfg | admin + status; SMTP external |
| Scheduled Reports | V/D (Xcfg delivery) | management done; delivery needs SMTP |
| Users / Roles / Role Profiles / User Permissions / Effective Access | V/D | Access Control + generated CRUD |
| Two-company separation | V | test_two_company_separation |
| Import / Export | V/D | allowlisted |
| System health / Backups / Error logs | V/D | System Operations |
| Administration landing / navigation | V/D | /admin |
| Launch Readiness | V/D | truthful dashboard |

## Launch-critical frontend gaps: NONE
Remaining items are external (SMTP, MariaDB root, accountant, Hetzner/DNS, UAT) or
post-launch (1.1+). No public storefront / mobile app / marketplace was built (out of
scope, per instructions).
