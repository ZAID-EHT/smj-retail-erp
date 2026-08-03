"""Audit what the commission implementation actually does today.

Written for the payout mission: the behaviours below are the ones a period-closing
workflow has to build on, so each is measured rather than assumed. Savepoint +
rollback; nothing persists.
"""

from __future__ import annotations

import uuid

import frappe
from frappe.utils import add_days, flt, nowdate

SNAPSHOT_DOCTYPES = ("Sales Order", "Delivery Note", "Sales Invoice")
HEAD_FIELDS = (
	"custom_sales_team", "custom_sales_team_name", "custom_sales_manager",
	"custom_team_commission_rate", "custom_customer_sales_team",
	"custom_sales_team_source", "custom_sales_team_override_reason",
	"custom_sales_team_captured_on", "custom_sales_team_captured_by",
	"custom_sales_team_members", "custom_sales_team_snapshot",
)
STANDARD_FIELDS = ("amount_eligible_for_commission", "commission_rate", "total_commission",
                   "sales_team")


def _fields(doctype, names):
	meta = frappe.get_meta(doctype, cached=False)
	for name in names:
		field = meta.get_field(name)
		if not field:
			print(f"   {name:36} MISSING")
		else:
			print(f"   {name:36} {field.fieldtype:12} ro={int(field.read_only or 0)} "
			      f"opts={(field.options or '')[:28]}")


def run():
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")
	frappe.set_user("Administrator")

	print("=== SNAPSHOT FIELDS ===")
	for doctype in SNAPSHOT_DOCTYPES:
		print(f"--- {doctype} ---")
		_fields(doctype, HEAD_FIELDS + STANDARD_FIELDS)

	print("\n=== MASTER FIELDS ===")
	_fields("Retail Sales Team", ("team_name", "sales_manager", "commission_rate",
	                             "restrict_to_company", "is_active", "effective_from",
	                             "effective_to", "members"))
	print("--- Customer ---")
	_fields("Customer", ("custom_sales_team",))

	print("\n=== HOOKS ===")
	for doctype, events in frappe.get_hooks("doc_events").items():
		for event, handlers in (events or {}).items():
			for handler in handlers if isinstance(handlers, list) else [handlers]:
				if "sales_team" in handler or "commission" in handler:
					print(f"   {doctype:16} {event:28} {handler}")

	print("\n=== EXISTING COMMISSION DOCTYPES ===")
	for doctype in ("Retail Commission Policy", "Retail Commission Period",
	                "Retail Commission Period Detail", "Retail Commission Adjustment",
	                "Retail Commission Payout"):
		print(f"   {doctype:34} {'exists' if frappe.db.exists('DocType', doctype) else 'ABSENT'}")

	print("\n=== PAYMENT LINKAGE ===")
	meta = frappe.get_meta("Payment Entry", cached=False)
	print("   Payment Entry has a sales team field:",
	      bool(meta.get_field("custom_sales_team")))
	print("   Payment Entry references:",
	      [f.fieldname for f in frappe.get_meta('Payment Entry Reference').fields][:8])

	print("\n=== CANCELLATION BEHAVIOUR ===")
	sp = f"aud_{uuid.uuid4().hex[:6]}"
	frappe.db.savepoint(sp)
	try:
		from my_store_ui.commission import list_commissions
		from my_store_ui.quick_entry.product import create_product
		from my_store_ui.sales_team import assign_customer_sales_team, save_sales_team
		from my_store_ui.wholesale.delivery import create_delivery_note
		from my_store_ui.wholesale.invoicing import create_sales_invoice

		company = frappe.get_all("Company", pluck="name")[0]
		warehouse = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": company, "disabled": 0},
			pluck="name")[0]
		people = [frappe.get_doc({
			"doctype": "Sales Person", "sales_person_name": f"AU {uuid.uuid4().hex[:8]}",
			"is_group": 0, "parent_sales_person": "",
		}).insert(ignore_permissions=True).name for _ in range(3)]
		team = save_sales_team({
			"team_name": f"AU Team {uuid.uuid4().hex[:6]}", "commission_rate": 2,
			"effective_from": nowdate(), "is_active": True,
			"members": [
				{"sales_person": people[0], "team_role": "Sales Manager",
				 "share_percentage": 50, "is_active": True},
				{"sales_person": people[1], "team_role": "Sales Representative",
				 "share_percentage": 25, "is_active": True},
				{"sales_person": people[2], "team_role": "Sales Representative",
				 "share_percentage": 25, "is_active": True},
			],
		})["name"]
		customer = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"AUCust {uuid.uuid4().hex[:6]}",
			"customer_group": frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0],
			"territory": frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0],
			"default_price_list": "Wholesale Price List",
		}).insert(ignore_permissions=True).name
		assign_customer_sales_team(customer, team)

		item = create_product({
			"product_name": f"AUItem {uuid.uuid4().hex[:5]}",
			"category": frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0],
			"stock_location_1": warehouse, "cost_price": 500,
			"wholesale_price": 1000, "retail_price": 1200,
		})["name"]
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": company,
			"items": [{"item_code": item, "qty": 500, "t_warehouse": warehouse, "basic_rate": 500}],
		})
		se.insert(ignore_permissions=True)
		se.submit()
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": company,
			"delivery_date": add_days(nowdate(), 7),
			"items": [{"item_code": item, "qty": 100, "rate": 1000, "warehouse": warehouse,
			           "delivery_date": add_days(nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		so.submit()
		note = create_delivery_note(so.name, override_reason="Audit", submit=1)
		invoice = frappe.get_doc(
			"Sales Invoice", create_sales_invoice(note["name"], submit=1)["name"])

		rows = [r for r in list_commissions()["rows"] if r["sales_invoice"] == invoice.name]
		print(f"   submitted invoice -> {len(rows)} register lines, "
		      f"net={round(sum(flt(r['net_commission']) for r in rows), 2)}")
		print(f"   outstanding={flt(invoice.outstanding_amount)} "
		      f"payment_status={rows[0]['payment_status'] if rows else 'n/a'}")

		invoice.cancel()
		rows_after = [r for r in list_commissions()["rows"] if r["sales_invoice"] == invoice.name]
		print(f"   cancelled invoice -> {len(rows_after)} register lines "
		      f"(0 means cancellation already removes commission)")
		print(f"   snapshot survives cancellation: "
		      f"{bool(frappe.db.get_value('Sales Invoice', invoice.name, 'custom_sales_team'))}")
	finally:
		frappe.db.rollback(save_point=sp)
		print("=== rolled back ===")

	print("\n=== HISTORICAL MANUAL REVIEW EXPORT ===")
	import os
	path = frappe.get_site_path("private", "files", "sales_team_manual_review.csv")
	if os.path.exists(path):
		with open(path) as handle:
			lines = handle.readlines()
		print(f"   {path}")
		print(f"   rows (excluding header): {len(lines) - 1}")
	else:
		print(f"   ABSENT at {path}")
