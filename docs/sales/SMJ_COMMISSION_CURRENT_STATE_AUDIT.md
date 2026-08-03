# SMJ Commission — Current State Audit

Measured on `staging.local` with
`my_store_ui/dev_scripts/audit_commission_state.py` on 2026-08-04, before any
change in this mission. Nothing below is assumed.

## 1. What exists today

| Layer | State |
|---|---|
| `Retail Sales Team` master (manager, reps, split, rate, company) | complete |
| `Customer.custom_sales_team` default assignment | complete |
| Immutable snapshot on Sales Order / Delivery Note / Sales Invoice | complete |
| Commission calculation (base, rate, pool, allocation, member amount) | complete |
| Credit-note reversal | complete, proportional |
| Commission register + CSV export | complete |
| Guarded backfill | complete |
| **Commission policy configuration** | **absent** |
| **Commission periods / closing** | **absent** |
| **Exceptions, adjustments, statements, approval** | **absent** |
| **Payout preparation and accounting boundary** | **absent** |

Confirmed absent as doctypes: `Retail Commission Policy`,
`Retail Commission Period`, `Retail Commission Period Detail`,
`Retail Commission Adjustment`, `Retail Commission Payout`.

## 2. Hooks in force

```
Sales Order    before_validate             sales_team.freeze_team
Sales Order    validate                    sales_team.price_commission
Sales Order    before_update_after_submit  sales_team.guard_snapshot_after_submit
Delivery Note  (the same three)
Sales Invoice  (the same three)
```

`freeze_team` settles the team once and never again; `price_commission` splits the
pool ERPNext has just computed; `guard_snapshot_after_submit` refuses an in-place
edit of a submitted document.

## 3. Every quantity, and what it is made of

| # | Quantity | Source doc | Source field | Timing | Mutable | Historical | Accounting-backed | External block |
|---|---|---|---|---|---|---|---|---|
| 1 | Eligible sales base | Sales Invoice | `amount_eligible_for_commission` (ERPNext) | on validate | draft only | yes, once submitted | no | no |
| 2 | Team commission rate | Sales Invoice | `custom_team_commission_rate` | frozen at creation | no | yes | no | no |
| 3 | Gross commission pool | Sales Invoice | `total_commission` (ERPNext) | on validate | draft only | yes | no | no |
| 4 | Member allocation % | snapshot row | `allocation_percentage` | frozen at creation | no | yes | no | no |
| 5 | Gross member commission | snapshot row | `commission_amount` | on validate | draft only | yes | no | no |
| 6 | Return / cancellation reversal | credit note | negative `commission_amount` | on the credit note | no | yes | no | no |
| 7 | **Withholding** | — | — | — | — | — | — | **blocked: rate unapproved** |
| 8 | **Approved adjustment** | — | — | — | — | — | — | needs the workflow built |
| 9 | **Net payable** | — | — | — | — | — | — | derived once 6–8 exist |
| 10 | **Paid amount** | — | — | — | — | — | **would be** | **blocked: no approved posting** |
| 11 | **Outstanding** | — | — | — | — | — | — | derived from 9 − 10 |

Quantities 1–6 exist and are frozen. Quantities 7–11 are what this mission builds,
with 10 deliberately unreachable.

## 4. Verified behaviours

### The master cannot retroactively change a calculation
`freeze_team` writes `custom_sales_team_captured_on` as a sentinel and returns
early on every later save. Asserted by
`test_editing_the_team_master_does_not_change_the_old_order` and by a real browser
check. Re-confirmed in this audit: the snapshot fields on all three doctypes are
`read_only`, and `guard_snapshot_after_submit` refuses a submitted-document edit.

### Cancellation already removes commission — and keeps the evidence
Measured: a submitted invoice produced **3 register lines totalling 2,000**; after
`invoice.cancel()` it produced **0 lines**, because the register filters
`docstatus: 1`. The snapshot itself **survives** cancellation
(`custom_sales_team` still set), so the evidence is intact for audit while the
money is correctly excluded.

This matters for period closing: a period prepared before a cancellation and
approved afterwards would hold a row whose source no longer qualifies. That is
handled as a **clawback**, not by rewriting the approved period.

### Payment behaviour: nothing today
Commission is invoice-based only. Measured: **`Payment Entry` has no sales team
field**, and `Payment Entry Reference` links back through
`reference_doctype` / `reference_name`. So collection-based eligibility must be
derived by joining Payment Entry Reference → Sales Invoice, not by stamping the
payment. The register reports `payment_status` (`Paid` / `Part Paid` / `Unpaid` /
`Credit Note`) from the invoice's own outstanding amount, but **eligibility does
not currently depend on it**.

That is precisely one of the accountant decisions: invoicing or collection.

## 5. Statuses that exist today

Register only, and deliberately minimal:

| Status | Meaning |
|---|---|
| `Draft` | on an unsubmitted document |
| `Estimated` | submitted Sales Order |
| `Earned` | submitted Sales Invoice |
| `Reversed` | credit note |
| `Cancelled` | excluded from the register entirely |

There is **no `Paid`**, by design. Nothing in the system can verify money left the
business.

## 6. Permissions today

| Capability | Who |
|---|---|
| View / create / edit teams | System Manager, Sales Manager |
| Assign a team to a customer | System Manager, Sales Manager (+ Customer write) |
| Override a team for one order | System Manager, Sales Manager, with a reason |
| Commission register — all lines | System Manager, Sales Manager, Accounts Manager |
| Commission register — own lines | anyone else **with Sales Invoice read** |
| Commission register — refused | anyone without Sales Invoice read (which is Sales User alone, in ERPNext v15) |

User → person resolution is `User → Employee.user_id → Sales Person.employee`.

## 7. Historical manual review

The previous mission exported the documents with no reliable team evidence.
**Measured now: 331 rows**, not the 333 reported — the earlier figure included a
team-level problem row that has since changed. The count is read from the file, not
carried forward.

```
sites/staging.local/private/files/sales_team_manual_review.csv
```

Composition at the time of writing: 303 submitted documents with no historical team
evidence, 27 customers with no team, 1 team with a zero commission rate.

## 8. Standard ERPNext fields relied upon

| Field | Doctype | Why |
|---|---|---|
| `amount_eligible_for_commission` | selling documents | the commission base, ERPNext's own definition |
| `commission_rate` | selling documents | the document-level rate we set from the team |
| `total_commission` | selling documents | the pool ERPNext derives |
| `sales_team` | selling documents | standard sales-person reporting, kept populated |
| `Sales Team.allocated_percentage` | child | drives ERPNext's own contribution maths |
| `Sales Team.allocated_amount` | child | the share of the **sale**, not pay — never used as commission |
| `Sales Person.employee` | master | the user → person link |
| `Version` | framework | the customer reassignment trail |

## 9. What the payout workflow must therefore add

1. A **policy** that states the earning trigger, basis, rate source, accounting
   accounts, payout cycle, withholding and returns rule — and that refuses to
   become Active while any required field is missing.
2. A **period** that freezes a set of eligible rows, is idempotent to prepare, and
   cannot overlap another for the same company and policy.
3. **Exceptions** that block approval rather than being silently skipped.
4. **Adjustments** with segregation of duties.
5. **Statements** filtered to the reader.
6. An **approval** trail.
7. **Payout preparation** with a dry-run accounting preview and no submit.
