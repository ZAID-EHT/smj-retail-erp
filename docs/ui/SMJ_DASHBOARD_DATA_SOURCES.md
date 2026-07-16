# SMJ Retail ERP — Home Dashboard Data Sources

All endpoints live in `apps/my_store_ui/my_store_ui/dashboard_analytics.py`,
are `@frappe.whitelist(methods=["GET"])`, require login
(`_require_login()`), and check `frappe.has_permission(doctype, "read")`
before querying — a section returns zeros/empty rather than raising when
the user lacks permission, so the dashboard degrades per-widget instead of
failing outright. No `ignore_permissions=True`, no raw SQL, no arbitrary
method execution. Company scoping uses
`frappe.defaults.get_user_default("Company")`, same pattern as the rest of
the app.

| Endpoint | Real ERPNext source | Notes |
|---|---|---|
| `get_home_kpis` | `Sales Invoice` (`base_grand_total`, `outstanding_amount`), `Bin` (`actual_qty × valuation_rate`, `reserved_stock × valuation_rate`), `Sales Order` count, and ERPNext's own **Gross Profit** query report (reused via `frappe.desk.query_report.run`, not reimplemented) | Trend % is `(this month − last month) / abs(last month) × 100` |
| `get_sales_trend` | `Sales Invoice.base_grand_total` grouped by month, this year and the same months last year | |
| `get_payment_collection` | `Sales Invoice.base_grand_total` / `outstanding_amount`, split into collected / pending / overdue (`due_date < today`) | |
| `get_top_categories` | `Sales Invoice Item.base_net_amount` grouped by `item_group` | Uses `frappe.get_all()` for the child-table rows — see the `get_list` vs `get_all` note below |
| `get_top_parties` | Customers: `Sales Invoice` grouped by `customer`. Products: `Sales Invoice Item` grouped by `item_code` | |
| `get_stock_overview` | `Bin` aggregate (`actual_qty`, `reserved_stock`, both × `valuation_rate`), `Item`/`Warehouse` counts | |
| `get_low_stock_alerts` | `Bin.actual_qty`/`reserved_stock` vs `Item Reorder.warehouse_reorder_level` (falls back to an available-quantity ≤ 10 heuristic when no reorder level is configured) | |
| `get_recent_transactions` | `Sales Invoice`, `Purchase Order`, `Delivery Note`, most recently modified first | |

## A real bug found and fixed while building this

`get_top_categories` and the products branch of `get_top_parties`
initially returned empty results even though `Sales Invoice Item` rows
demonstrably existed (`frappe.db.count` reported 10 rows). Root cause,
confirmed via `bench execute` on a throwaway debug script: **`frappe.get_list()`
on a child doctype applies row-level permission filtering that silently
excludes child rows**, while `frappe.get_all()` does not — and child tables
don't carry independent permissions in Frappe, they inherit from the
parent, which had already been permission-checked. Fixed by switching those
two queries to `get_all()`. Documented here because it's a genuine,
non-obvious Frappe behaviour that's easy to hit again.

## Known data caveats (not bugs)

- This demo dataset has several invoices dated in the future relative to
  the system's current date, so "this month" KPIs (Total Sales MTD, Gross
  Profit MTD) are frequently `0` — a true reflection of the query, not a
  broken calculation. Confirmed by cross-checking against
  `get_recent_transactions` and `get_payment_collection`, which show the
  same invoices with real non-zero totals under their own (not
  month-scoped) aggregations.
- Gross Profit MTD wraps the report execution in a `try/except` with
  `frappe.log_error` — if the standard "Gross Profit" report changes shape
  in a future ERPNext version, the KPI degrades to `0` instead of crashing
  the whole dashboard; check the error log if it looks wrong.
