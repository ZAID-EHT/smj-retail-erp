"""What does Email Account actually expose for 'can this site send mail'?"""

import frappe


def run():
	frappe.set_user("Administrator")
	meta = frappe.get_meta("Email Account")
	print("=== Email Account candidate fields ===")
	for fieldname in (
		"enable_outgoing", "enable_incoming", "disabled", "default_outgoing",
		"default_incoming", "email_id", "smtp_server", "awaiting_password", "service",
	):
		field = meta.get_field(fieldname)
		print(f"  {fieldname:20} {'PRESENT ' + field.fieldtype if field else 'ABSENT'}")

	print("\n=== all Email Account Check fields ===")
	print("  ", sorted(f.fieldname for f in meta.fields if f.fieldtype == "Check"))

	print("\n=== existing Email Accounts ===")
	rows = frappe.get_all(
		"Email Account",
		fields=["name", "email_id", "enable_outgoing", "default_outgoing", "awaiting_password"],
	)
	print("  ", rows or "(none)")
