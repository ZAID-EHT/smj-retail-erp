"""Does Frappe's Version trail record a change to Customer.custom_sales_team?

The customer assignment history is meant to reuse the standard audit record rather
than invent a second one. This proves whether that record actually exists.
Savepoint + rollback; nothing persists.
"""

from __future__ import annotations

import uuid

import frappe


def run():
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")
	frappe.set_user("Administrator")
	sp = f"ver_{uuid.uuid4().hex[:6]}"
	frappe.db.savepoint(sp)
	try:
		meta = frappe.get_meta("Customer")
		print("Customer track_changes:", meta.track_changes)
		field = meta.get_field("custom_sales_team")
		print("custom_sales_team present:", bool(field))
		if field:
			print("   no_copy:", field.no_copy, " hidden:", field.hidden,
			      " read_only:", field.read_only)

		team = frappe.get_all("Retail Sales Team", limit=1, pluck="name")
		if not team:
			print("no teams on this site; cannot probe")
			return
		customer = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"VerProbe {uuid.uuid4().hex[:6]}",
			"customer_group": frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0],
			"territory": frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0],
		}).insert(ignore_permissions=True)

		doc = frappe.get_doc("Customer", customer.name)
		doc.custom_sales_team = team[0]
		doc.save(ignore_permissions=True)

		versions = frappe.get_all(
			"Version", filters={"ref_doctype": "Customer", "docname": customer.name},
			fields=["name", "data"], limit_page_length=0)
		print("versions found:", len(versions))
		for version in versions:
			changed = frappe.parse_json(version["data"]).get("changed") or []
			print("   changed:", changed)
	finally:
		frappe.db.rollback(save_point=sp)
		print("=== rolled back ===")
