# SMJ Commission — Policy Simulation

`simulate_commission_policy(name, from_date, to_date, limit)`

Runs a policy over **real historical invoices** and shows what it would produce,
without writing anything. Read-only by construction: it reads frozen snapshots and
computes in memory. `persisted: false` is returned explicitly, and
`test_simulation_persists_nothing` asserts the period count is unchanged.

## Why it shares code with the real thing

Simulation and preparation both call `collect_eligible_rows()`. There is no second
implementation to drift out of step, so what the simulation shows is what the period
will contain.

## What it returns

Per row: transaction, commission basis, applied rate, gross pool, member allocation,
returns, withholding, adjustments and net payable — plus the amount **frozen on the
document**, so the two can be compared.

Totals: lines, gross, reversals, withholding, net.

## Comparison with the current calculation

`matches_current_calculation` is true when every row's policy result equals the
figure frozen on the document. A difference is not necessarily wrong — withholding
and a collection-based trigger legitimately change it — but it is always **listed**,
never silent:

```json
{"sales_invoice": "…", "sales_person": "…",
 "frozen_on_document": 1000.0, "policy_result": 900.0,
 "reason": "The collected share of the eligible amount."}
```

## What it flags

Every condition below produces an exception with a severity, an owner and a
recommended action:

| Flag | Severity |
|---|---|
| Missing team snapshot | Blocking |
| Missing commission rate | Blocking |
| Missing team member | Blocking |
| Allocation does not total 100% | Blocking |
| Rate source has no data source | Blocking |
| Commission basis not set | Blocking |
| Withholding rules not configured | Blocking |
| Custom basis not implemented | Blocking |
| No cost recorded (Gross Profit) | Warning |
| Already in another period | Warning |
| Duplicate source | Blocking |

Cancelled invoices never appear: the query filters `docstatus: 1`. Currency and
company are constrained by the period's own validation.

## Measured on staging

A policy of *invoice submission / net total after discount / sales team rate /
no withholding* reproduced the frozen calculation exactly:

```
simulated lines                 9
simulated net                   6000.0
persisted                       False
matches current calculation     True
```

Switching the rate source to `Customer Rate` produced blocking exceptions and a
gross of **0.00** — it did not fall back to the team rate.
