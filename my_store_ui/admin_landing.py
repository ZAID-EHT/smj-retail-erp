"""Phase 3 — permission-aware Administration landing.

Returns the cards the current user may see, each with a status and the route to open.
Every card's visibility is decided server-side from real permissions; nothing
sensitive (infrastructure, financial detail) is returned to a user who lacks the
System Manager gate. Read-only.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint


def _is_manager() -> bool:
	return frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()


def _email_status() -> dict:
	from my_store_ui.access_management import _email_configuration_status
	s = _email_configuration_status()
	return {"ok": s["can_send_welcome_email"],
	        "text": _("Configured") if s["can_send_welcome_email"] else _("Email not configured")}


def _finance_status() -> dict:
	"""Whether the opening-stock correction is applied / pending."""
	company = (frappe.get_all("Company", pluck="name", limit_page_length=1) or [None])[0]
	if not company:
		return {"ok": True, "text": _("No company yet"), "warnings": 0}
	applied = frappe.db.get_value(
		"Journal Entry", {"user_remark": ["like", "%opening-stock reclassification%"], "docstatus": 1}, "name")
	if applied:
		return {"ok": True, "text": _("Correction applied"), "warnings": 0}
	# Is the artifact still present?
	sa = frappe.db.get_value("Company", company, "stock_adjustment_account")
	pending = False
	if sa:
		pending = bool(frappe.db.sql(
			"""SELECT 1 FROM `tabGL Entry` WHERE account=%s AND is_cancelled=0
			   AND voucher_type='Stock Entry' AND posting_date<=%s LIMIT 1""", (sa, "2025-07-01")))
	return {"ok": not pending, "text": _("Accountant approval pending") if pending else _("No correction needed"),
	        "warnings": 1 if pending else 0}


def _company_status() -> dict:
	count = frappe.db.count("Company")
	return {"ok": count > 0, "text": _("{0} company(ies)").format(count) if count else _("Setup required"),
	        "warnings": 0 if count else 1}


def _system_status() -> dict:
	from my_store_ui.system_operations import _scheduler_disabled
	warnings = 0
	if _scheduler_disabled():
		warnings += 1
	return {"ok": warnings == 0, "text": _("Scheduler disabled") if warnings else _("Healthy"), "warnings": warnings}


@frappe.whitelist(methods=["GET"])
def get_admin_landing() -> dict:
	"""Cards the current user is permitted to see, with live status."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	manager = _is_manager()

	cards = []

	def add(key, title, description, route, secondary_route, status, needs_manager=True,
	        needs_perm=None, external=False):
		if needs_manager and not manager:
			return
		if needs_perm and not frappe.has_permission(needs_perm, "read"):
			return
		cards.append({
			"key": key, "title": title, "description": description, "route": route,
			"secondary_route": secondary_route, "status": status.get("text"),
			"status_ok": status.get("ok", True), "warnings": status.get("warnings", 0),
			"external": external,
		})

	add("companies", _("Companies & Setup"), _("Create and configure companies, accounts and warehouses."),
	    "/admin/companies", "/setup", _company_status(), needs_perm="Company")
	add("access", _("Users & Access"), _("Users, roles, role profiles, permissions and effective access."),
	    "/admin/access-control", "/admin/users", {"ok": True, "text": _("Manage access")}, needs_perm="User")
	add("printing", _("Printing & Branding"), _("Letter heads, print formats and secure PDF preview/download."),
	    "/admin/printing", "/admin/print-format", {"ok": True, "text": _("Manage printing")})
	add("email", _("Email & Notifications"), _("Delivery status, templates and notification coverage."),
	    "/admin/email", None, _email_status())
	add("data", _("Data Management"), _("Guided, permission-filtered import and export."),
	    "/admin/data", None, {"ok": True, "text": _("Import / export")})
	add("finance", _("Finance Setup"), _("Chart of accounts, fiscal year, reconciliation and the opening-stock correction."),
	    "/finance/chart-of-accounts", "/admin/readiness", _finance_status())
	add("scheduled", _("Scheduled Reports"), _("Auto-email reports on a schedule (needs SMTP to deliver)."),
	    "/reports/scheduled", None, {"ok": True, "text": _("Manage schedules")})
	add("system", _("System Operations"), _("Read-only health, readiness and backup status."),
	    "/admin/system", None, _system_status())
	add("readiness", _("Launch Readiness"), _("Truthful go-live checklist across code, finance, infra and approvals."),
	    "/admin/readiness", None, {"ok": True, "text": _("View readiness")})

	return {"is_manager": manager, "cards": cards, "card_count": len(cards)}
