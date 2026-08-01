"""Temporary probe: why does the delivery request_id dedup not short-circuit?"""

from __future__ import annotations

import uuid

import frappe


def run():
	frappe.set_user("Administrator")
	sp = "dbg_dedup"
	frappe.db.savepoint(sp)
	try:
		rid = uuid.uuid4().hex
		key = f"my_store_ui:delivery_note:{frappe.session.user}:{rid}"
		print("SESSION_USER", frappe.session.user)
		print("BEFORE_GET", frappe.cache.get_value(key))
		frappe.cache.set_value(key, "MAT-DN-TEST", expires_in_sec=3600)
		print("AFTER_GET", frappe.cache.get_value(key))
		name = frappe.get_all("Delivery Note", limit=1, pluck="name")
		if name:
			print("EXISTS_CHECK", bool(frappe.db.exists("Delivery Note", name[0])), name[0])
		frappe.cache.delete_value(key)
	finally:
		frappe.db.rollback(save_point=sp)
