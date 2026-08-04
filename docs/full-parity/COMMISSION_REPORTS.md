# SMJ Commission — Reports

Four reports, all permission-scoped, all reading frozen snapshots.

## 1. Commission Period Summary

Where: the period list on `/retail-erp/sales/commission-periods`.
Source: `list_commission_periods`.

Period · company · policy · from · to · status · gross · reversals · withholding ·
adjustments · net payable · paid · outstanding.

`paid` is always `0.00` and `outstanding` always equals net payable, because no
accounting-backed payout exists.

## 2. Member Commission Detail

Where: the **Rows** tab on a period, and the **Statements** tab per member.
Source: `get_commission_period`, `list_commission_statements`.

Member · role · team · date · customer · Sales Order · Sales Invoice · eligible
basis · rate · allocation % · gross · reversal · withholding · adjustment · net ·
status.

Scoped: a manager sees every member; anyone else sees only their own.

## 3. Exception Report

Where: the **Exceptions** tab on a period.
Source: the period's own `exceptions` table.

Exception · severity · source doctype · source · owner · recommended action ·
resolution status · resolution note · resolved by · resolved on.

Blocking exceptions prevent approval. Waiving one requires a reason, and the
resolution survives re-preparation.

## 4. Historical Review Report

Where: `/retail-erp/sales/commissions/historical-review`.
Source: `list_historical_commission_review`.

Source document · date · customer · total · sales people recorded on the document ·
the customer's team today (labelled *not evidence*) · whether reliable evidence
exists · suggested team · status · reviewer.

## Export, print and PDF

| Surface | Export |
|---|---|
| Commission register | CSV, permission-gated on Sales Invoice **export** |
| Period rows, statements, exceptions | print through the browser; the underlying rows export from the register |
| Historical review | print through the browser |

Wide tables scroll inside their own container, so the page itself never scrolls
sideways — asserted in the browser at all six viewports.

## Dashboards

`get_commission_dashboard` returns three panels, and omits the ones the caller may
not see rather than blanking them:

| Panel | Audience | Content |
|---|---|---|
| `sales` | Sales Manager and above | team gross, reversals, net, unresolved exceptions |
| `accounts` | Accounts User and above | net payable, withholding, payouts prepared, payouts blocked, blocked lines, **`posting_enabled: false`** |
| `own` | anyone with a linked Sales Person | own gross, reversals, adjustments, net, and `paid: 0.0` |

A member gets `sales: null` and `accounts: null` — the data is absent from the
response, not hidden in the browser.
