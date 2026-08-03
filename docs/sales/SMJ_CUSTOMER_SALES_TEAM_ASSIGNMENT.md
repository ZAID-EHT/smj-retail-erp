# SMJ — Assigning a Sales Team to a Customer

## What the assignment means

`Customer.custom_sales_team` is the **default for new transactions only**. It is
mutable, and changing it never touches a document that already exists.

## Where it appears

| Screen | What is shown |
|---|---|
| Customer create / edit | A "Sales Assignment" section with the team picker and a live preview |
| Customer detail | The current team card, recent orders with the team each was raised with, and the reassignment history |
| Customer list | `custom_sales_team` is a standard filter |
| Sales Team form | The customers assigned to that team, and its performance |

## The picker

- Only **active** teams are offered (`search_sales_teams` filters them out).
- A team pinned to another company is never offered.
- Selecting one shows a compact preview: the manager, each representative, their
  percentages and the total.
- The preview values come from the selected team. Nothing is hardcoded — the
  requirement document's 50 / 25 / 25 is the *default shape of a new team*, not a
  constant in the customer form.
- Clearing the field is allowed; the customer simply has no default and new orders
  carry no commission split.

The form shows a compact preview rather than the full member table: the customer
form is the simplified Retail ERP one, and the team's own form is where members are
edited.

## Atomicity

Customer creation stays atomic. The team is assigned **after** the customer is
successfully created, so a rejected assignment can never leave a half-made
Customer, Address or Contact behind. If the assignment fails the customer still
exists, unassigned, and the error says so.

## Permissions

Assigning requires **both** `Retail Sales Team` write (System Manager or Sales
Manager) and `Customer` write. A Sales User can see the assignment and cannot
change it — enforced in `assign_customer_sales_team`, not in the screen.

## Validation

| Rule | Behaviour |
|---|---|
| Team must exist | `ValidationError` |
| Team must be active | `ValidationError`, naming the team |
| Team must not belong to another company | refused, and not offered in the first place |
| Clearing | allowed |

## What assignment also does

The team is projected onto ERPNext's own `Customer.sales_team` child table, so
standard ERPNext sales-person reporting keeps working rather than being replaced.
Percentages are balanced to exactly 100 first, because ERPNext compares against
100.0 exactly.

Editing a team master re-syncs every customer assigned to it. This is the *default*
being kept current — it does not reach any document already raised.

## Reporting on what is missing

`sales_team_migration.export_manual_review` lists every customer without a team,
with an inactive team, or with a team that no longer exists. On staging that is 29
customers. See `docs/data/SMJ_SALES_TEAM_MIGRATION_RESULT.md`.

## The endpoints

| Endpoint | Purpose |
|---|---|
| `get_customer_sales_assignment(customer)` | current team, warnings, and whether the caller may override |
| `assign_customer_sales_team(customer, team)` | set or clear the default |
| `search_sales_teams(query, company, active_only)` | the picker |
| `get_sales_team_snapshot(sales_team, customer)` | what *would* be frozen right now |

Every one of them declares a default for each argument, so a cleared field arriving
as an empty string is a value meaning "all" — never a missing argument and an
HTTP 500.
