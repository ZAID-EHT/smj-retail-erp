import json
import frappe


def run():
	frappe.set_user("Administrator")
	fp = {
		"site": frappe.local.site,
		"companies": frappe.get_all("Company", pluck="name"),
		"installed_apps": frappe.get_installed_apps(),
		"administrator_modified": str(frappe.db.get_value("User", "Administrator", "modified")),
		"test_pattern_users": frappe.db.count("User", {"email": ["like", "smj-%@example.com"]}),
		"opening_stock_correction_je": frappe.db.count(
			"Journal Entry", {"user_remark": ["like", "%opening-stock reclassification%"]}),
		"latest_gl_posting_date": str(frappe.db.sql("SELECT MAX(posting_date) FROM `tabGL Entry`")[0][0]),
	}
	print("FINGERPRINT:", json.dumps(fp, default=str))
