# SMJ Commission Periods

`Retail Commission Period` — one closing cycle, for one company, under one policy.
Screen: `/retail-erp/sales/commission-periods`. Identifier: `COM-PER-YYYY-######`.

## Statuses

`Draft` → `Prepared` → `Under Review` → `Approved` → `Payment Prepared` →
`Partially Paid` → `Paid`, plus `Reopened` and `Cancelled`.

**`Partially Paid` and `Paid` are unreachable in this build.** Only an
accounting-backed payout can move `paid_amount`, and no accounting document is
created. `outstanding` therefore always equals `net_payable`.

## Validation

| Rule | Where |
|---|---|
| To Date not before From Date | controller |
| Policy must belong to the same company | controller |
| Currency must match the policy | controller |
| No overlapping live period for the same company **and** policy | controller |
| Only an active, approved policy may open or prepare | API |
| An approved period cannot be re-prepared | `assert_editable()` |

## Preparation

`prepare_commission_period(name)` — deterministic and idempotent.

1. Load eligible invoices per the policy's earning trigger
2. Load the immutable team snapshot from each invoice
3. Resolve the basis per the policy
4. Resolve the rate per the policy
5. Compute the gross pool
6. Split it by each member's frozen allocation
7. Apply returns (a credit note carries negative amounts through naturally)
8. Apply approved adjustments
9. Apply withholding
10. Compute net
11. Record every exception found
12. Write the detail rows
13. Keep the source links
14. **Produce no accounting entry**

Rows are rebuilt from source rather than appended to, so preparing twice yields the
same period. Each row carries a `source_key` (`invoice::sales_person`) which makes a
duplicate *detectable* rather than merely unlikely, and a row already recorded in
another live period is excluded with a warning rather than claimed twice.

Every figure comes from the frozen snapshot, never from the Sales Team master.

## Detail rows

Sales Invoice · Sales Order · Payment Entry (collection policies) · Customer · Sales
Team · member · role · eligible basis · rate · gross pool · allocation % · gross
commission · return reversal · withholding · adjustment · net commission ·
eligibility date · status.

## Review and approval

```
Prepared → (send for review) → Under Review → (review) → (approve) → Approved
```

**Segregation of duties**, enforced server-side: the person who prepared a period
cannot review it, and cannot approve it. Only a System Manager may override, and
only an Accounts Manager may approve at all.

### The eleven approval checks

Policy active · policy complete for calculation · no unresolved blocking exceptions ·
the period has rows · totals balance against the rows · no duplicate source rows ·
every row traceable to an invoice · allocations total 100% on every invoice · no
adjustment awaiting approval · withholding treatment defined · returns rule defined.

None can be waived at the approval step. `get_period_approval_checks` reports them
without approving, so the screen shows what is standing in the way.

## Reopening and cancelling

Both need a reason. Reopening clears the approval and is **refused** once any of the
period has been paid — the accounting would contradict it. The decision log keeps
every transition: decision, comment, user, timestamp, previous and new status.

## Measured on staging

```
period id              COM-PER-2026-000001
prepared rows          9
exceptions             0
gross                  6000.00
net payable            6000.00
rows after preparing twice   9
approval checks        11 total, 0 failed
period status          Approved
```
