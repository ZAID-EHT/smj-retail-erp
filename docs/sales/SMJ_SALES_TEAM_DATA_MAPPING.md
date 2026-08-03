# SMJ Sales Team — Data Mapping

Audited against the live `staging.local` schema on 2026-08-03 with
`my_store_ui/dev_scripts/audit_sales_team_model.py` and
`my_store_ui/dev_scripts/audit_commission_model.py`. Nothing here is assumed.

---

## 1. The five distinct quantities

The single most important thing to keep straight. These are **not**
interchangeable, and the requirement document's "50 / 25 / 25" refers only to the
fourth one.

| # | Quantity | Meaning | Where it lives |
|---|---|---|---|
| 1 | **Commission base** | The money the commission is worked out on | `amount_eligible_for_commission` (standard, read-only) |
| 2 | **Commission rate** | The team's percentage of that base | `Retail Sales Team.commission_rate` → document `commission_rate` |
| 3 | **Commission pool** | base × rate ÷ 100 — the whole team's earnings | `total_commission` (standard) |
| 4 | **Member allocation %** | How the *pool* is split between members (50/25/25) | snapshot row `allocation_percentage` |
| 5 | **Member commission amount** | pool × allocation ÷ 100 — one person's money | snapshot row `commission_amount` |

A sixth quantity exists in standard ERPNext and is deliberately **not** reused as
a commission figure:

| Quantity | Meaning | Field |
|---|---|---|
| Sales contribution amount | base × allocation ÷ 100 — the share of the *sale* credited to a person, not their pay | `Sales Team.allocated_amount` (standard, read-only) |

Worked example, matching the requirement document:

```
Commission base   (net of discount, before tax)   LKR 100,000
Team rate                                                  2%
Commission pool   100,000 x 2%                     LKR   2,000

Sales Manager        50% of pool                   LKR   1,000
Representative 1     25% of pool                   LKR     500
Representative 2     25% of pool                   LKR     500
                    ----                           -----------
                    100%                           LKR   2,000
```

The manager is **not** paid 50% of LKR 100,000. The allocation percentage divides
the pool, never the sale.

---

## 2. What ERPNext v15 already provides

`erpnext/controllers/selling_controller.py` (`calculate_commission`,
`calculate_contribution`) already computes items 1, 3 and the contribution amount
on Sales Order, Delivery Note and Sales Invoice:

```python
self.amount_eligible_for_commission = sum(
    item.base_net_amount for item in self.items if item.grant_commission
)
self.total_commission = flt(self.amount_eligible_for_commission * self.commission_rate / 100.0, ...)
...
sales_person.allocated_amount = flt(
    flt(self.amount_eligible_for_commission) * sales_person.allocated_percentage / 100.0, ...
)
```

So the design **reuses this** rather than writing parallel money maths. We supply
two inputs and let ERPNext derive the rest:

- document `commission_rate` ← the team's `commission_rate`
- `sales_team[].allocated_percentage` ← the snapshot allocation percentages

`Item.grant_commission` defaults to `1`, and all 249 existing Sales Order Items on
staging have it set, so the base is the net total of the order in practice.

### Two standard-field traps that shaped the design

1. **`Sales Team.commission_rate` is `Data`, `read_only`, and
   `fetch_from: sales_person.commission_rate`.** It is the *sales person's own*
   rate pulled from their master record — it cannot be used to carry the team
   rate. Writing to it is silently overwritten on save. The pre-existing
   `_apply_team_rows()` did exactly this; it is corrected in this mission.
2. **`Sales Team.incentives` means `allocated_amount × the sales person's own
   rate`.** That is a different formula from "share of the team pool", so
   populating it with the member's commission amount would be misusing the field.
   The member's commission amount is therefore kept in the retail-owned snapshot
   row, and `incentives` is left to ERPNext.

`calculate_contribution` also throws if the `sales_team` rows do not total 100.
Our teams always total exactly 100 across *active* members, so this is consistent
rather than an obstacle — it gives us a second, standard enforcement of the rule.

---

## 3. Master: Retail Sales Team

Custom doctype, `STM-.#####`, 2 records on staging, both active.

| Label | Field | Type | Std/Custom | Reqd | Validation | Historical behaviour |
|---|---|---|---|---|---|---|
| Team Name | `team_name` | Data | custom | yes | unique | mutable; snapshots keep the old name |
| Team Code | `name` | autoname | custom | auto | `STM-.#####` | permanent identity |
| Sales Manager | `sales_manager` | Link → Sales Person | custom | derived | set from the member row marked Sales Manager; read-only | snapshot keeps the manager of the day |
| Team Commission Rate | `commission_rate` | Percent | custom | no | 0–100 | snapshot freezes the rate |
| Company | `company` | Link → Company | custom **(added)** | no | blank = every company | enforced against the transaction company |
| Effective From | `effective_from` | Date | custom | yes | ≤ Effective To | |
| Effective To | `effective_to` | Date | custom | no | ≥ Effective From | |
| Active | `is_active` | Check | custom | no | | inactive blocks *new* use only |
| Members | `members` | Table → Retail Sales Team Member | custom | yes | ≥ 1 row | |
| Notes | `notes` | Small Text | custom | no | | |

### Retail Sales Team Member (child)

| Label | Field | Type | Reqd | Validation |
|---|---|---|---|---|
| Sales Person | `sales_person` | Link → Sales Person | yes | no duplicate within a team |
| Role in Team | `team_role` | Select | yes | `Sales Manager` \| `Sales Representative`; exactly one active manager |
| Share % | `share_percentage` | Percent | no | ≥ 0; active rows total 100 ± 0.01 |
| User | `user` | Data (read-only) | no | fetched from `sales_person.employee` |
| Active | `is_active` | Check | no | inactive rows excluded from the total |
| Effective From / To | Date | | no | To ≥ From |

**Member identity is ERPNext's `Sales Person`, not `Employee`.** Sales Person is
the standard selling-side person master, is already linked to Employee, and is
what the standard `sales_team` child table requires. This avoids both a duplicate
person master and exposing HR data. 10 Sales Person records exist on staging; no
new ones are created implicitly.

---

## 4. Customer

| Label | Field | Type | Std/Custom | Notes |
|---|---|---|---|---|
| Assigned Sales Team | `custom_sales_team` | Link → Retail Sales Team | custom | the default for **new** transactions only |
| (standard) | `sales_team` | Table → Sales Team | standard | projected from the master so standard ERPNext reporting keeps working |

Customer is not company-scoped in ERPNext, so the company check happens at the
transaction, where a company actually exists.

---

## 5. Transactions — Sales Order, Delivery Note, Sales Invoice

Everything below is written **once**, when the document is first raised, and is
never re-read from the master afterwards.

| Label | Field | Type | Status |
|---|---|---|---|
| Sales Team | `custom_sales_team` | Link → Retail Sales Team (read-only) | existing |
| Sales Team Name | `custom_sales_team_name` | Data (read-only) | existing |
| Sales Manager | `custom_sales_manager` | Link → Sales Person (read-only) | existing |
| Team Commission Rate | `custom_team_commission_rate` | Percent (read-only) | existing |
| Sales Team Snapshot | `custom_sales_team_snapshot` | Long Text (read-only, print-hidden) | existing — audit copy |
| **Team Members** | `custom_sales_team_members` | Table → Retail Sales Team Snapshot | **added** |
| **Customer Default Team** | `custom_customer_sales_team` | Link → Retail Sales Team (read-only) | **added** |
| **Team Source** | `custom_sales_team_source` | Select: `Customer Default` \| `Overridden` | **added** |
| **Override Reason** | `custom_sales_team_override_reason` | Small Text (read-only) | **added** |
| **Snapshot Taken On** | `custom_sales_team_captured_on` | Datetime (read-only) | **added** |
| **Snapshot Taken By** | `custom_sales_team_captured_by` | Link → User (read-only) | **added** |
| (standard) | `sales_team` | Table → Sales Team | populated from the snapshot |
| (standard) | `commission_rate` | Float | set from the snapshot team rate |
| (standard) | `amount_eligible_for_commission` | Currency (read-only) | ERPNext computes |
| (standard) | `total_commission` | Currency | ERPNext computes |

### Retail Sales Team Snapshot (child) — the immutable row

| Label | Field | Type | Notes |
|---|---|---|---|
| Sales Person | `sales_person` | Link → Sales Person (read-only) | identity at the time |
| Name | `sales_person_name` | Data (read-only) | the display name of the day |
| Role in Team | `team_role` | Data (read-only) | **not** a Select — a later master change to the option list must not invalidate history |
| Allocation % | `allocation_percentage` | Percent (read-only) | share of the pool |
| Commission Amount | `commission_amount` | Currency (read-only) | pool × allocation ÷ 100 |

### Why a dedicated snapshot table rather than only `sales_team`

The standard `Sales Team` row cannot carry four things this workflow needs:

1. **Team role** — there is no role field; manager and representative are
   indistinguishable.
2. **Team master reference** — no link back to which team this came from.
3. **Override source and reason** — nowhere to record them.
4. **Immutable identity** — `commission_rate` is re-fetched from the Sales Person
   master, so the row is not frozen in time.

The standard table is still populated, so standard ERPNext sales-person reporting
continues to work. The snapshot table is additive, not a replacement, and there is
no separate sales document, ledger or accounting structure.

### Why both a JSON blob and rows

They are generated from one payload by one function, so they cannot diverge. The
rows are the queryable, printable, reportable surface; the blob is a complete
tamper-evident audit copy including fields with no column of their own. The blob
is `print_hide`, so it never reaches a customer-facing document.

---

## 6. Immutability rules

| Event | Effect on an existing document |
|---|---|
| Team master renamed | none — the snapshot keeps the old name |
| Member added or removed | none |
| Percentages changed | none |
| Commission rate changed | none |
| Team deactivated | none; the document stays readable |
| Sales person renamed | none — the snapshot keeps `sales_person_name` of the day |
| Customer reassigned to another team | none |
| Document submitted | the snapshot is frozen; changes are rejected server-side |

New documents pick up the current master. Historical ones never do.

---

## 7. Downstream mapping

```
Customer.custom_sales_team          (the default, mutable)
        |
        v  copied once, at creation
Sales Order  snapshot + rows + standard sales_team + commission_rate
        |
        +--> Delivery Note   inherits the Sales Order snapshot
        |
        +--> Sales Invoice   inherits the Sales Order snapshot
                 |
                 +--> Credit Note  inherits, and reverses commission in proportion
```

Delivery Notes and Invoices resolve their snapshot from the source Sales Order via
`against_sales_order` / `sales_order` on the item rows. They never re-read the
customer or the master. A document raised standalone, with no source order, falls
back to the customer's team at that moment — and records that it did.
