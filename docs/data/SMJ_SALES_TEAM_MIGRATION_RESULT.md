# SMJ Sales Team — Existing Data Migration

Tool: `my_store_ui/sales_team_migration.py`.
Tests: `my_store_ui/tests/test_sales_team_migration.py` (15 tests).

```
bench --site staging.local execute my_store_ui.sales_team_migration.inspect
bench --site staging.local execute my_store_ui.sales_team_migration.dry_run
bench --site staging.local execute my_store_ui.sales_team_migration.apply_safe
bench --site staging.local execute my_store_ui.sales_team_migration.verify
bench --site staging.local execute my_store_ui.sales_team_migration.export_manual_review
```

## Guardrails

| Guardrail | Behaviour | Proven by |
|---|---|---|
| Protected site | `site1.local` is refused **for being protected**, before any other check | `test_a_protected_site_is_refused_for_being_protected` |
| Unknown site | Any site not explicitly listed as disposable is refused | `test_an_unknown_site_is_refused` |
| Backup age | A write needs a database backup under 24 h old | `test_a_stale_backup_blocks_writing` |
| Read-only modes | `inspect` / `dry_run` / `verify` never need a backup and never write | `test_read_only_modes_never_need_a_backup`, `test_dry_run_writes_nothing` |
| Idempotency | A second `apply_safe` changes nothing | `test_applying_twice_changes_nothing_the_second_time` |
| No invented assignment | A customer with no team stays without one | `test_a_customer_with_no_team_is_never_guessed_at` |
| No submitted rewrites | Submitted documents are never touched | `test_a_submitted_document_is_never_rewritten` |
| Export location | The review CSV goes to site private files, never the repository | `test_the_export_never_lands_in_the_repository` |
| Unknown mode | Refused | `test_an_unknown_mode_is_refused` |

Each document is settled inside its own savepoint, so one bad record is skipped
without discarding the ones already done and without disturbing an outer
transaction.

## What it will and will not change

**Will:** fill the snapshot on a **draft** Sales Order whose customer has exactly
one team that exists, is active, and is not pinned to a different company. It does
so by calling `doc.save()`, which runs the same `freeze_team` hook a brand-new
order uses — there is no second write path that could drift.

**Will never:** invent a team for a customer that has none; guess the team a
submitted document was raised with; rewrite a submitted document; or change any
accounting, stock, total or status value.

## Measured position on `staging.local` (2026-08-03)

```
Customers                     30
  with a sales team            1
  without a sales team        29
  invalid team assignment      0
  inactive team assignment     0

Retail Sales Teams             2  (both active)
  problems: STM-00014 has a commission rate of 0
            -> allocation is recorded, amounts pending configuration

Sales Order    103 total, 0 draft, 103 submitted,   0 with a snapshot
Delivery Note  101 total, 0 draft, 100 submitted, 1 cancelled, 0 with a snapshot
Sales Invoice  100 total, 0 draft, 100 submitted,   0 with a snapshot

Settleable draft orders        0
Needing manual review        303
```

## Result

`apply_safe` had **nothing to do** on staging, and that is the correct outcome:
every one of the 303 existing documents is already submitted and predates the
feature, so none of them holds evidence of the team it was raised with.

Backfilling them would mean picking a team out of the air and attaching real
commission figures to it. That would look authoritative and be fabricated. They are
exported for a human instead.

Verified afterwards with `verify`: no document has a team set without matching
snapshot rows, and no allocation fails to total 100.

## Manual review export

`export_manual_review` wrote **333 rows** to
`sites/staging.local/private/files/sales_team_manual_review.csv`:

| Kind | Rows | Reason |
|---|---|---|
| Document | 303 | submitted before the feature existed; no historical team evidence |
| Customer | 29 | no sales team assigned |
| Team | 1 | commission rate is 0; amounts pending configuration |

Columns: `kind, doctype, name, customer, company, team, reason`.

The file lives in the site's private files, outside the repository, and is not
committed.

## What a human needs to decide

1. **The 29 customers with no team.** Assign one on the customer form. New orders
   pick it up immediately; nothing historical changes.
2. **`STM-00014`'s commission rate.** Until it is set, that team's orders record the
   split but no money.
3. **The 303 submitted documents.** Either accept that commission reporting begins
   from the feature's start date — the recommendation — or, if a genuine historical
   record exists outside the system, have someone assign teams deliberately with
   that evidence in hand.

## Running it on a new site

Add the site to `WRITABLE_SITES` in `sales_team_migration.py` only when losing its
data would be acceptable, take a fresh backup, then run `inspect` → `dry_run` →
`apply_safe` → `verify`.
