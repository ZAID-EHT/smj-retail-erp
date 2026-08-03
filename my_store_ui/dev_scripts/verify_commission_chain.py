"""Prove the commission chain end to end on a real Sales Order.

Builds a team, a customer and an order, prints every number in the chain, then
rolls everything back. Staging only; nothing persists.
"""

from __future__ import annotations

import json
import uuid

import frappe
from frappe.utils import add_days, flt, nowdate

from my_store_ui.sales_team import assign_customer_sales_team, save_sales_team


def _person():
	doc = frappe.get_doc({
		"doctype": "Sales Person", "sales_person_name": f"VC {uuid.uuid4().hex[:8]}",
		"is_group": 0, "parent_sales_person": "",
	})
	doc.insert(ignore_permissions=True)
	return doc.name


def run():
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")
	frappe.set_user("Administrator")
	sp = f"vc_{uuid.uuid4().hex[:6]}"
	frappe.db.savepoint(sp)
	try:
		company = frappe.get_all("Company", pluck="name")[0]
		people = [_person() for _ in range(3)]
		team = save_sales_team({
			"team_name": f"VC Team {uuid.uuid4().hex[:6]}",
			"commission_rate": 2,
			"effective_from": nowdate(),
			"is_active": True,
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
			"doctype": "Customer", "customer_name": f"VCCust {uuid.uuid4().hex[:6]}",
			"customer_group": frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0],
			"territory": frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0],
		}).insert(ignore_permissions=True).name
		assign_customer_sales_team(customer, team)

		from my_store_ui.quick_entry.product import create_product
		warehouse = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": company, "disabled": 0}, pluck="name")[0]
		item = create_product({
			"product_name": f"VCItem {uuid.uuid4().hex[:5]}",
			"category": frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0],
			"stock_location_1": warehouse, "cost_price": 500,
			"wholesale_price": 1000, "retail_price": 1200,
		})["name"]

		# 100 x 1000 = LKR 100,000 net, matching the worked example in the docs.
		order = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": company,
			"delivery_date": add_days(nowdate(), 7),
			"items": [{"item_code": item, "qty": 100, "rate": 1000, "warehouse": warehouse,
			           "delivery_date": add_days(nowdate(), 7)}],
		})
		order.insert(ignore_permissions=True)

		print("=== HEAD ===")
		for field in ("custom_sales_team", "custom_sales_team_name", "custom_sales_manager",
		              "custom_team_commission_rate", "custom_customer_sales_team",
		              "custom_sales_team_source", "custom_sales_team_captured_on",
		              "custom_sales_team_captured_by"):
			print(f"   {field:34} {order.get(field)}")

		print("=== ERPNEXT-DERIVED ===")
		print(f"   net_total                          {flt(order.net_total)}")
		print(f"   amount_eligible_for_commission     {flt(order.amount_eligible_for_commission)}")
		print(f"   commission_rate                    {flt(order.commission_rate)}")
		print(f"   total_commission (POOL)            {flt(order.total_commission)}")

		print("=== SNAPSHOT ROWS ===")
		total_amount = 0.0
		total_share = 0.0
		for row in order.get("custom_sales_team_members") or []:
			total_amount += flt(row.commission_amount)
			total_share += flt(row.allocation_percentage)
			print(f"   {row.team_role:22} {row.sales_person_name:24} "
			      f"{flt(row.allocation_percentage):6}%  {flt(row.commission_amount):12}")
		print(f"   {'TOTAL':22} {'':24} {round(total_share, 4):6}%  {round(total_amount, 4):12}")
		print(f"   pool reconciles: {abs(total_amount - flt(order.total_commission)) < 0.01}")

		print("=== STANDARD ERPNEXT sales_team ROWS ===")
		for row in order.get("sales_team") or []:
			print(f"   {row.sales_person:28} alloc%={flt(row.allocated_percentage):6} "
			      f"alloc_amt={flt(row.allocated_amount):12} incentives={flt(row.incentives)}")

		print("=== AUDIT BLOB KEYS ===")
		print("  ", sorted(json.loads(order.custom_sales_team_snapshot).keys()))
	finally:
		frappe.db.rollback(save_point=sp)
		print("=== rolled back; nothing persisted ===")
