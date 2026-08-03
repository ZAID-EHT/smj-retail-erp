# SMJ Commission Payout — Mission State

## Repository position at start

| Item | Value |
|---|---|
| Bench | `/home/zaidh/frappe-bench` |
| App | `apps/my_store_ui` |
| Branch | `full-feature-parity` |
| Starting commit | `d19a0273c53cee558075d5ec54b80edbd68c24f7` |
| Starting release tag | `v1.0.0-rc9` — verified to point **exactly** at `d19a027` |
| Recovery tag | `pre-smj-commission-payout-20260804-0018` (new; no existing tag overwritten) |
| Worktree at start | clean; `git diff --check` and `git diff --cached --check` both silent |
| Test site | `staging.local` |
| Protected site | `site1.local` |

## Backup

```
sites/staging.local/private/backups/20260804_001837-staging_local-database.sql.gz      2.6 MiB
sites/staging.local/private/backups/20260804_001837-staging_local-files.tar           10.0 KiB
sites/staging.local/private/backups/20260804_001837-staging_local-private-files.tar   50.0 KiB
sites/staging.local/private/backups/20260804_001837-staging_local-site_config_backup.json
```

Backups live under `sites/`, outside the app repository. Nothing from them is
committed.

## site1.local fingerprint (read-only, taken before any change)

```
{"Batch": 0, "Customer": 3, "Delivery Note": 0, "GL Entry": 44, "Item": 11,
 "Payment Entry": 5, "Purchase Invoice": 6, "Purchase Order": 10,
 "Purchase Receipt": 0, "Sales Invoice": 7, "Sales Order": 7,
 "Stock Ledger Entry": 17, "User": 3}
SHA f51fedb5a9ac68e27b1515daee5cdf2f90490a22c07925960dd0acb4d123d9c3
MATCHES_BASELINE True
```

To be repeated at the end of the mission.

## The line this mission does not cross

Commission **preparation** is built in full. Commission **posting** is not.

No accounting document is submitted, no GL Entry or Payment Ledger Entry is
written, no invoice outstanding is touched, and there is no way to reach a `Paid`
status without verifiable accounting evidence — because none can exist until the
accountant decisions in `SMJ_COMMISSION_PAYOUT_BLOCKERS.md` are made.

The eleven quantities the workflow keeps strictly separate:

| # | Quantity | Where |
|---|---|---|
| 1 | Eligible sales base | frozen on the invoice |
| 2 | Team commission rate | frozen on the invoice |
| 3 | Gross commission pool | frozen on the invoice |
| 4 | Member allocation % | frozen snapshot row |
| 5 | Gross member commission | frozen snapshot row |
| 6 | Return / cancellation reversal | period detail row |
| 7 | Withholding | period detail row, from policy |
| 8 | Approved manual adjustment | adjustment record |
| 9 | Net payable commission | period detail row |
| 10 | Paid amount | **unreachable this mission** |
| 11 | Outstanding commission | period total |
