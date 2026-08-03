"""Drive a whole commission closing end to end and print every number.

Policy -> period -> prepare -> review -> approve -> payout -> accounting preview,
then confirm posting refuses. Savepoint + rollback; nothing persists.
"""

from __future__ import annotations

import uuid

import frappe
from frappe.utils import add_days, flt, nowdate


def _print(label, value):
	print(f"   {label:38} {value}")


def run():
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")
	frappe.set_user("Administrator")
	sp = f"vcc_{uuid.uuid4().hex[:6]}"
	frappe.db.savepoint(sp)
	try:
		from my_store_ui.commission_payout import (
			get_commission_statement, post_commission_payout, prepare_commission_payout,
			validate_commission_payout,
		)
		from my_store_ui.commission_period import (
			approve_commission_period, create_commission_period, get_period_approval_checks,
			prepare_commission_period, review_commission_period, submit_period_for_review,
		)
		from my_store_ui.commission_policy import (
			approve_commission_policy, save_commission_policy, simulate_commission_policy,
			validate_commission_policy,
		)
		from my_store_ui.quick_entry.product import create_product
		from my_store_ui.sales_team import assign_customer_sales_team, save_sales_team
		from my_store_ui.wholesale.delivery import create_delivery_note
		from my_store_ui.wholesale.invoicing import create_sales_invoice

		company = frappe.get_all("Company", pluck="name")[0]
		warehouse = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": company, "disabled": 0},
			pluck="name")[0]

		print("=== 1. POLICY ===")
		policy_name = f"VCC Policy {uuid.uuid4().hex[:6]}"
		policy = save_commission_policy({
			"policy_name": policy_name, "company": company, "effective_from": nowdate(),
			"enabled": 1,
		})
		_print("status with nothing chosen", policy["policy"]["status"])
		_print("missing for calculation", policy["policy"]["missing_for_calculation"])

		policy = save_commission_policy({
			"earning_trigger": "Sales Invoice Submission",
			"commission_basis": "Net Total After Discount",
			"rate_source": "Sales Team Rate",
			"payout_cycle": "Monthly",
			"withholding_mode": "No Withholding",
			"returns_rule": "Reverse Before Payout",
		}, name=policy["name"])
		_print("status once complete", policy["policy"]["status"])
		_print("may post (must be False)", policy["policy"]["may_post"])

		policy = approve_commission_policy(policy["name"])
		_print("status after approval", policy["policy"]["status"])
		_print("complete for posting", policy["policy"]["complete_for_posting"])
		validation = validate_commission_policy(policy["name"])
		_print("blocking issues", len(validation["blocking"]))

		print("\n=== 2. A REAL INVOICE ===")
		people = [frappe.get_doc({
			"doctype": "Sales Person", "sales_person_name": f"VCC {uuid.uuid4().hex[:8]}",
			"is_group": 0, "parent_sales_person": "",
		}).insert(ignore_permissions=True).name for _ in range(3)]
		team = save_sales_team({
			"team_name": f"VCC Team {uuid.uuid4().hex[:6]}", "commission_rate": 2,
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
			"doctype": "Customer", "customer_name": f"VCCCust {uuid.uuid4().hex[:6]}",
			"customer_group": frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0],
			"territory": frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0],
			"default_price_list": "Wholesale Price List",
		}).insert(ignore_permissions=True).name
		assign_customer_sales_team(customer, team)

		item = create_product({
			"product_name": f"VCCItem {uuid.uuid4().hex[:5]}",
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
		note = create_delivery_note(so.name, override_reason="Closing check", submit=1)
		invoice = create_sales_invoice(note["name"], submit=1)
		_print("invoice", invoice["name"])

		print("\n=== 3. SIMULATION (writes nothing) ===")
		sim = simulate_commission_policy(policy["name"])
		_print("simulated lines", sim["totals"]["lines"])
		_print("simulated net", sim["totals"]["net_commission"])
		_print("persisted", sim["persisted"])
		_print("matches current calculation", sim["matches_current_calculation"])

		print("\n=== 4. PERIOD ===")
		period = create_commission_period(
			company=company, policy=policy["name"],
			from_date=add_days(nowdate(), -30), to_date=add_days(nowdate(), 1))
		_print("period id", period["name"])
		prepared = prepare_commission_period(period["name"])
		_print("prepared rows", prepared["prepared_rows"])
		_print("exceptions", prepared["exceptions"])
		_print("gross", prepared["period"]["gross_commission"])
		_print("net payable", prepared["period"]["net_payable"])

		again = prepare_commission_period(period["name"])
		_print("rows after preparing twice", again["prepared_rows"])

		print("\n=== 5. REVIEW AND APPROVAL ===")
		submit_period_for_review(period["name"])
		review_commission_period(period["name"], comment="Checked")
		checks = get_period_approval_checks(period["name"])
		_print("approval checks", f"{len(checks['checks'])} total, {len(checks['failed'])} failed")
		for failed in checks["failed"]:
			_print("   FAILED", f"{failed['check']} {failed['detail']}")
		approved = approve_commission_period(period["name"], comment="Approved")
		_print("period status", approved["period"]["status"])

		print("\n=== 6. STATEMENTS ===")
		statement = get_commission_statement(period["name"], sales_person=people[0])
		entry = statement["statements"][0]
		_print("member", entry["sales_person_name"])
		_print("gross / withholding / net",
		       f"{entry['gross_commission']} / {entry['withholding']} / {entry['net_payable']}")
		_print("transactions", len(entry["transactions"]))

		print("\n=== 7. PAYOUT PREPARATION ===")
		payout = prepare_commission_payout(period["name"])
		_print("payout", payout["name"])
		_print("status", payout["payout"]["status"])
		_print("total net payable", payout["payout"]["total_net_payable"])
		for line in payout["payout"]["lines"]:
			_print(f"   {line['sales_person_name']}",
			       f"net={line['net_payable']} {line['validation_status']}: "
			       f"{line['validation_note'][:60]}")
		validated = validate_commission_payout(payout["name"])
		_print("status after validation", validated["payout"]["status"])
		_print("blocked lines", validated["blocked_lines"])

		print("\n=== 8. ACCOUNTING PREVIEW ===")
		preview = validated["payout"]["accounting_preview"]
		_print("proposed document", preview.get("proposed_document_type"))
		_print("entry count", preview.get("entry_count"))
		_print("would post", preview.get("would_post"))

		print("\n=== 9. POSTING MUST REFUSE ===")
		try:
			post_commission_payout(payout["name"], confirmation="yes")
			print("   *** DEFECT: posting did not refuse ***")
		except frappe.ValidationError as caught:
			_print("refused with", str(caught)[:110])

		print("\n=== 10. GL UNTOUCHED ===")
		_print("GL entries for this period",
		       frappe.db.count("GL Entry", {"voucher_no": period["name"]}))
	except Exception:
		print("\n*** FAILED ***")
		print(frappe.get_traceback())
	finally:
		frappe.db.rollback(save_point=sp)
		print("\n=== rolled back; nothing persisted ===")
