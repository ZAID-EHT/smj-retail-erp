"""The commission register: what each team member earned, and on what.

Every figure here is read from the immutable snapshot frozen onto the document
when it was raised. Nothing is recalculated from the Sales Team master, so editing
a team today cannot change what a report said yesterday.

The Sales Invoice is the earning event. A credit note is an invoice with
`is_return`, and ERPNext gives it negative item amounts, so its commission comes
through as a negative figure and reverses the original in proportion without any
special-case arithmetic.
"""

from __future__ import annotations

import csv
import io

import frappe
from frappe import _
from frappe.utils import cint, flt

SNAPSHOT_TABLE = "Retail Sales Team Snapshot"
PARENT_FIELD = "custom_sales_team_members"

# Who may see the whole register rather than only their own lines.
MANAGER_ROLES = ("System Manager", "Sales Manager", "Accounts Manager")
# Who may move a line along the approval track.
APPROVER_ROLES = ("System Manager", "Accounts Manager")

MAX_ROWS = 500

STATUS_ESTIMATED = "Estimated"
STATUS_EARNED = "Earned"
STATUS_REVERSED = "Reversed"
STATUS_CANCELLED = "Cancelled"


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def can_see_everyone() -> bool:
	return bool(set(frappe.get_roles()) & set(MANAGER_ROLES))


def can_approve() -> bool:
	return bool(set(frappe.get_roles()) & set(APPROVER_ROLES))


def sales_persons_for_user(user: str | None = None) -> list[str]:
	"""The Sales Person records that are this user, via their Employee link."""
	user = user or frappe.session.user
	employees = frappe.get_all("Employee", filters={"user_id": user}, pluck="name")
	if not employees:
		return []
	return frappe.get_all(
		"Sales Person", filters={"employee": ["in", employees]}, pluck="name"
	)


def _visible_people() -> list[str] | None:
	"""None means "everything"; a list restricts the register to those people."""
	if can_see_everyone():
		return None
	return sales_persons_for_user()


@frappe.whitelist(methods=["GET"])
def list_commissions(from_date: str = "", to_date: str = "", company: str = "",
                     team: str = "", sales_person: str = "", customer: str = "",
                     sales_order: str = "", sales_invoice: str = "",
                     payment_status: str = "", status: str = "",
                     limit: int = 200):
	"""The register, filtered and permission-scoped."""
	_require_login()
	if not frappe.has_permission("Sales Invoice", "read"):
		frappe.throw(_("You do not have access to commission reporting."), frappe.PermissionError)

	limit = min(max(cint(limit) or 200, 1), MAX_ROWS)
	people = _visible_people()
	if people is not None and not people:
		# A user with no Sales Person of their own sees an empty, honest register
		# rather than everyone else's earnings.
		return {"rows": [], "totals": _totals([]), "can_see_everyone": False,
		        "can_approve": can_approve(), "restricted_to": [], "truncated": False}

	invoice_filters = {"docstatus": 1, "custom_sales_team": ["is", "set"]}
	if from_date and to_date:
		invoice_filters["posting_date"] = ["between", [from_date, to_date]]
	elif from_date:
		invoice_filters["posting_date"] = [">=", from_date]
	elif to_date:
		invoice_filters["posting_date"] = ["<=", to_date]
	if company:
		invoice_filters["company"] = company
	if customer:
		invoice_filters["customer"] = customer
	if team:
		invoice_filters["custom_sales_team"] = team
	if sales_invoice:
		invoice_filters["name"] = sales_invoice

	# get_list applies permissions and User Permissions; get_all would bypass them.
	invoices = frappe.get_list(
		"Sales Invoice", filters=invoice_filters,
		fields=["name", "posting_date", "customer", "customer_name", "company", "currency",
		        "custom_sales_team", "custom_sales_team_name", "custom_team_commission_rate",
		        "custom_sales_team_source", "custom_sales_team_override_reason",
		        "amount_eligible_for_commission", "total_commission", "is_return",
		        "return_against", "status", "outstanding_amount", "grand_total"],
		order_by="posting_date desc, name desc", limit_page_length=limit,
	)
	if not invoices:
		return {"rows": [], "totals": _totals([]), "can_see_everyone": people is None,
		        "can_approve": can_approve(), "restricted_to": people or [], "truncated": False}

	names = [inv["name"] for inv in invoices]
	rows_by_parent: dict[str, list] = {}
	row_filters = {"parent": ["in", names], "parenttype": "Sales Invoice",
	               "parentfield": PARENT_FIELD}
	if sales_person:
		row_filters["sales_person"] = sales_person
	elif people is not None:
		row_filters["sales_person"] = ["in", people]
	for row in frappe.get_all(
		SNAPSHOT_TABLE, filters=row_filters,
		fields=["parent", "sales_person", "sales_person_name", "team_role",
		        "allocation_percentage", "commission_amount"],
		order_by="parent, idx", limit_page_length=0,
	):
		rows_by_parent.setdefault(row["parent"], []).append(row)

	orders = _orders_for(names)
	txn_ids = _transaction_ids(names)

	out = []
	for invoice in invoices:
		members = rows_by_parent.get(invoice["name"])
		if not members:
			continue
		order = orders.get(invoice["name"], "")
		if sales_order and order != sales_order:
			continue
		pay = _payment_status(invoice)
		if payment_status and pay != payment_status:
			continue
		line_status = _status(invoice)
		if status and line_status != status:
			continue
		for member in members:
			amount = flt(member["commission_amount"])
			reversal = amount if cint(invoice["is_return"]) else 0.0
			gross = 0.0 if cint(invoice["is_return"]) else amount
			out.append({
				"date": str(invoice["posting_date"]),
				"transaction_id": txn_ids.get(invoice["name"], ""),
				"sales_order": order,
				"sales_invoice": invoice["name"],
				"is_return": bool(cint(invoice["is_return"])),
				"return_against": invoice.get("return_against") or "",
				"customer": invoice["customer"],
				"customer_name": invoice.get("customer_name") or invoice["customer"],
				"company": invoice["company"],
				"currency": invoice.get("currency"),
				"team": invoice["custom_sales_team"],
				"team_name": invoice.get("custom_sales_team_name") or invoice["custom_sales_team"],
				"team_source": invoice.get("custom_sales_team_source") or "Customer Default",
				"override_reason": invoice.get("custom_sales_team_override_reason") or "",
				"sales_person": member["sales_person"],
				"sales_person_name": member.get("sales_person_name") or member["sales_person"],
				"role": member.get("team_role"),
				"allocation_percentage": flt(member["allocation_percentage"]),
				"commission_base": flt(invoice.get("amount_eligible_for_commission")),
				"commission_rate": flt(invoice.get("custom_team_commission_rate")),
				"commission_pool": flt(invoice.get("total_commission")),
				"gross_commission": gross,
				"return_reversal": reversal,
				"net_commission": amount,
				"payment_status": pay,
				"commission_status": line_status,
			})

	return {
		"rows": out,
		"totals": _totals(out),
		"can_see_everyone": people is None,
		"can_approve": can_approve(),
		"restricted_to": people or [],
		"truncated": len(invoices) >= limit,
	}


def _orders_for(invoices: list[str]) -> dict[str, str]:
	"""The first Sales Order behind each invoice, for the register's reference column."""
	found: dict[str, str] = {}
	for row in frappe.get_all(
		"Sales Invoice Item", filters={"parent": ["in", invoices], "sales_order": ["is", "set"]},
		fields=["parent", "sales_order"], order_by="parent, idx", limit_page_length=0,
	):
		found.setdefault(row["parent"], row["sales_order"])
	return found


def _transaction_ids(invoices: list[str]) -> dict[str, str]:
	if not frappe.get_meta("Sales Invoice").get_field("custom_wholesale_transaction_id"):
		return {}
	return {
		row["name"]: row.get("custom_wholesale_transaction_id") or ""
		for row in frappe.get_all(
			"Sales Invoice", filters={"name": ["in", invoices]},
			fields=["name", "custom_wholesale_transaction_id"], limit_page_length=0)
	}


def _payment_status(invoice: dict) -> str:
	if cint(invoice.get("is_return")):
		return "Credit Note"
	outstanding = flt(invoice.get("outstanding_amount"))
	if outstanding <= 0:
		return "Paid"
	if outstanding < flt(invoice.get("grand_total")):
		return "Part Paid"
	return "Unpaid"


def _status(invoice: dict) -> str:
	"""What the figure means. Never "Paid" -- no payout process exists yet.

	See docs/sales/SMJ_COMMISSION_PAYOUT_BOUNDARY.md.
	"""
	if cint(invoice.get("is_return")):
		return STATUS_REVERSED
	return STATUS_EARNED


def _totals(rows: list[dict]) -> dict:
	return {
		"lines": len(rows),
		"gross_commission": round(sum(flt(r["gross_commission"]) for r in rows), 2),
		"return_reversal": round(sum(flt(r["return_reversal"]) for r in rows), 2),
		"net_commission": round(sum(flt(r["net_commission"]) for r in rows), 2),
	}


EXPORT_COLUMNS = (
	("date", "Date"), ("transaction_id", "Transaction ID"), ("sales_order", "Sales Order"),
	("sales_invoice", "Sales Invoice"), ("customer_name", "Customer"), ("team_name", "Team"),
	("team_source", "Team Source"), ("sales_person_name", "Team Member"), ("role", "Role"),
	("allocation_percentage", "Allocation %"), ("commission_base", "Commission Base"),
	("commission_rate", "Commission Rate"), ("commission_pool", "Commission Pool"),
	("gross_commission", "Gross Commission"), ("return_reversal", "Return Reversal"),
	("net_commission", "Net Commission"), ("payment_status", "Payment Status"),
	("commission_status", "Commission Status"),
)


@frappe.whitelist(methods=["GET"])
def export_commissions(**filters):
	"""The same rows the register shows, as CSV. Same filters, same permissions."""
	_require_login()
	if not frappe.has_permission("Sales Invoice", "export"):
		frappe.throw(_("You do not have permission to export commission data."),
		             frappe.PermissionError)
	filters.pop("cmd", None)
	filters["limit"] = MAX_ROWS
	data = list_commissions(**filters)

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow([label for _key, label in EXPORT_COLUMNS])
	for row in data["rows"]:
		writer.writerow([row.get(key, "") for key, _label in EXPORT_COLUMNS])

	frappe.local.response.filename = "commission-register.csv"
	frappe.local.response.filecontent = buffer.getvalue()
	frappe.local.response.type = "download"


@frappe.whitelist(methods=["GET"])
def get_team_performance(team: str, from_date: str = "", to_date: str = ""):
	"""Operational figures for one team, all read from transaction snapshots."""
	_require_login()
	if not frappe.has_permission("Retail Sales Team", "read", doc=team):
		frappe.throw(_("You do not have access to this sales team."), frappe.PermissionError)

	customers = frappe.get_all(
		"Customer", filters={"custom_sales_team": team},
		fields=["name", "customer_name", "disabled"], limit_page_length=0)

	def _sum(doctype, extra=None, field="total_commission", date_field="posting_date"):
		filters = {"docstatus": 1, "custom_sales_team": team}
		filters.update(extra or {})
		if from_date and to_date:
			filters[date_field] = ["between", [from_date, to_date]]
		rows = frappe.get_list(doctype, filters=filters, fields=[f"sum({field}) as total"],
		                       limit_page_length=0)
		return flt(rows[0]["total"]) if rows and rows[0].get("total") else 0.0

	def _count(doctype, extra=None, date_field="posting_date"):
		filters = {"docstatus": 1, "custom_sales_team": team}
		filters.update(extra or {})
		if from_date and to_date:
			filters[date_field] = ["between", [from_date, to_date]]
		return len(frappe.get_list(doctype, filters=filters, fields=["name"],
		                           limit_page_length=0))

	invoiced = _sum("Sales Invoice", {"is_return": 0}, field="base_net_total")
	returned = _sum("Sales Invoice", {"is_return": 1}, field="base_net_total")
	earned = _sum("Sales Invoice", {"is_return": 0})
	reversed_ = _sum("Sales Invoice", {"is_return": 1})

	return {
		"team": team,
		"assigned_customers": len(customers),
		"active_customers": len([c for c in customers if not c.get("disabled")]),
		"orders": _count("Sales Order", date_field="transaction_date"),
		"estimated_commission": _sum("Sales Order", field="total_commission",
		                             date_field="transaction_date"),
		"invoiced_sales": invoiced,
		"returned_sales": returned,
		"earned_commission": earned,
		"reversed_commission": reversed_,
		"net_commission": round(earned + reversed_, 2),
		"period": {"from_date": from_date or None, "to_date": to_date or None},
		"customers": customers[:50],
	}


@frappe.whitelist(methods=["GET"])
def get_customer_commission_history(customer: str, limit: int = 20):
	"""What this customer's orders paid out, and which team they were raised with."""
	_require_login()
	if not frappe.has_permission("Customer", "read", doc=customer):
		frappe.throw(_("You do not have access to this customer."), frappe.PermissionError)
	limit = min(max(cint(limit) or 20, 1), 100)

	if not frappe.has_permission("Sales Order", "read"):
		return {"customer": customer, "transactions": [], "assignment_history": []}

	orders = frappe.get_list(
		"Sales Order",
		filters={"customer": customer, "docstatus": ["<", 2], "custom_sales_team": ["is", "set"]},
		fields=["name", "transaction_date", "status", "grand_total", "currency",
		        "custom_sales_team", "custom_sales_team_name", "custom_sales_team_source",
		        "custom_sales_team_override_reason", "custom_team_commission_rate",
		        "amount_eligible_for_commission", "total_commission", "docstatus"],
		order_by="transaction_date desc, name desc", limit_page_length=limit,
	)
	return {
		"customer": customer,
		"transactions": [
			{
				"sales_order": row["name"],
				"date": str(row["transaction_date"]),
				"status": row["status"],
				"order_total": flt(row["grand_total"]),
				"currency": row.get("currency"),
				"team": row["custom_sales_team"],
				"team_name": row.get("custom_sales_team_name") or row["custom_sales_team"],
				"team_source": row.get("custom_sales_team_source") or "Customer Default",
				"override_reason": row.get("custom_sales_team_override_reason") or "",
				"commission_base": flt(row.get("amount_eligible_for_commission")),
				"commission_rate": flt(row.get("custom_team_commission_rate")),
				"commission_pool": flt(row.get("total_commission")),
				"is_draft": cint(row["docstatus"]) == 0,
			}
			for row in orders
		],
		"assignment_history": _assignment_history(customer),
	}


def _assignment_history(customer: str) -> list[dict]:
	"""Team reassignments, read from Frappe's own Version trail.

	Customer has track_changes, so this is the existing audit record rather than a
	second one invented for this feature.
	"""
	history = []
	for version in frappe.get_all(
		"Version", filters={"ref_doctype": "Customer", "docname": customer},
		fields=["name", "owner", "creation", "data"], order_by="creation desc",
		limit_page_length=50,
	):
		try:
			changed = frappe.parse_json(version["data"]).get("changed") or []
		except Exception:
			continue
		for field, before, after in changed:
			if field != "custom_sales_team":
				continue
			history.append({
				"changed_on": str(version["creation"]),
				"changed_by": version["owner"],
				"previous_team": before or None,
				"new_team": after or None,
			})
	return history
