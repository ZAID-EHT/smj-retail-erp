"""Why is the commission base zero on an order raised through the Smart Sales cart?

Compares an order built directly with one built by create_draft_sales_order, which
is the path the counter actually uses. Savepoint + rollback.
"""

from __future__ import annotations

import uuid

import frappe
from frappe.utils import add_days, flt, nowdate


def _report(label, order):
	print(f"--- {label} ---")
	print(f"   net_total                        {flt(order.net_total)}")
	print(f"   amount_eligible_for_commission   {flt(order.amount_eligible_for_commission)}")
	print(f"   commission_rate                  {flt(order.commission_rate)}")
	print(f"   total_commission                 {flt(order.total_commission)}")
	for row in order.items:
		print(f"   item {row.item_code}: grant_commission={row.grant_commission} "
		      f"base_net_amount={flt(row.base_net_amount)}")


def run():
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")
	frappe.set_user("Administrator")
	sp = f"cb_{uuid.uuid4().hex[:6]}"
	frappe.db.savepoint(sp)
	try:
		from my_store_ui.api import create_draft_sales_order
		from my_store_ui.quick_entry.product import create_product
		from my_store_ui.sales_team import assign_customer_sales_team, save_sales_team

		company = frappe.get_all("Company", pluck="name")[0]
		warehouse = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": company, "disabled": 0},
			pluck="name")[0]
		item = create_product({
			"product_name": f"CB {uuid.uuid4().hex[:5]}",
			"category": frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0],
			"stock_location_1": warehouse, "cost_price": 500,
			"wholesale_price": 1000, "retail_price": 1200,
		})["name"]
		print("Item.grant_commission:", frappe.db.get_value("Item", item, "grant_commission"))

		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": company,
			"items": [{"item_code": item, "qty": 500, "t_warehouse": warehouse, "basic_rate": 500}],
		})
		se.insert(ignore_permissions=True)
		se.submit()

		people = []
		for _ in range(3):
			people.append(frappe.get_doc({
				"doctype": "Sales Person", "sales_person_name": f"CB {uuid.uuid4().hex[:8]}",
				"is_group": 0, "parent_sales_person": "",
			}).insert(ignore_permissions=True).name)
		team = save_sales_team({
			"team_name": f"CB Team {uuid.uuid4().hex[:6]}", "commission_rate": 4,
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
			"doctype": "Customer", "customer_name": f"CBCust {uuid.uuid4().hex[:6]}",
			"customer_group": frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0],
			"territory": frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0],
		}).insert(ignore_permissions=True).name
		assign_customer_sales_team(customer, team)

		direct = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": company,
			"delivery_date": add_days(nowdate(), 7),
			"items": [{"item_code": item, "qty": 100, "rate": 1000, "warehouse": warehouse,
			           "delivery_date": add_days(nowdate(), 7)}],
		})
		direct.insert(ignore_permissions=True)
		_report("built directly, rate supplied", direct)

		no_rate = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": company,
			"delivery_date": add_days(nowdate(), 7),
			"items": [{"item_code": item, "qty": 100, "warehouse": warehouse,
			           "delivery_date": add_days(nowdate(), 7)}],
		})
		no_rate.insert(ignore_permissions=True)
		_report("built directly, no rate", no_rate)

		cart = frappe.get_doc("Sales Order", create_draft_sales_order({
			"request_id": uuid.uuid4().hex, "customer": customer, "company": company,
			"warehouse": warehouse, "items": [{"item_code": item, "qty": 100}],
		})["name"])
		_report("built by the Smart Sales cart", cart)
	finally:
		frappe.db.rollback(save_point=sp)
		print("=== rolled back ===")
