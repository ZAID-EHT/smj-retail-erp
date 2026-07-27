"""Phase 5 — permission-safe scheduled (auto-email) report management.

Wraps the standard Frappe `Auto Email Report` doctype. Every operation re-checks
that the caller may access the chosen report, and refuses to schedule a report the
caller cannot run — so a schedule can never email data its creator could not see.
When no outgoing email is configured, schedules can be listed/created but the surface
reports truthfully that delivery will not happen.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

from my_store_ui.access_management import _email_configuration_status, _require_user_manager

FREQUENCIES = ("Daily", "Weekly", "Monthly")
FORMATS = ("HTML", "XLSX", "CSV")


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _may_use_report(report: str) -> None:
	"""Refuse a report the caller cannot access."""
	report = str(report or "").strip()
	if not report or not frappe.db.exists("Report", report):
		frappe.throw(_("Report not found."), frappe.DoesNotExistError)
	# frappe.has_permission on Report + the report's ref doctype.
	if not frappe.has_permission("Report", "read", doc=report):
		frappe.throw(_("You do not have access to this report."), frappe.PermissionError)
	ref_dt = frappe.db.get_value("Report", report, "ref_doctype")
	if ref_dt and not frappe.has_permission(ref_dt, "read"):
		frappe.throw(_("You do not have access to the data behind this report."), frappe.PermissionError)


@frappe.whitelist(methods=["GET"])
def get_scheduled_reports_overview(search: str = "", status: str = "") -> dict:
	"""List schedules the caller may see, plus SMTP readiness."""
	_require_login()
	if not frappe.has_permission("Auto Email Report", "read"):
		frappe.throw(_("You do not have permission to view scheduled reports."), frappe.PermissionError)
	filters: dict = {}
	if status == "enabled":
		filters["enabled"] = 1
	elif status == "disabled":
		filters["enabled"] = 0
	or_filters = {"name": ["like", f"%{search[:60]}%"], "report": ["like", f"%{search[:60]}%"]} if search else None
	rows = frappe.get_list(
		"Auto Email Report", filters=filters, or_filters=or_filters,
		fields=["name", "report", "enabled", "frequency", "format", "day_of_week", "user"],
		order_by="modified desc", limit_page_length=200,
	)
	return {
		"schedules": rows,
		"email": _email_configuration_status(),
		"frequencies": list(FREQUENCIES),
		"formats": list(FORMATS),
	}


@frappe.whitelist(methods=["GET"])
def get_schedulable_reports(search: str = "") -> dict:
	"""Reports the caller may actually schedule."""
	_require_login()
	filters = {"disabled": 0}
	if search:
		filters["name"] = ["like", f"%{str(search)[:60]}%"]
	candidates = frappe.get_list("Report", filters=filters, fields=["name", "ref_doctype", "report_type"],
	                             order_by="name asc", limit_page_length=100)
	allowed = []
	for row in candidates:
		if not frappe.has_permission("Report", "read", doc=row["name"]):
			continue
		if row.get("ref_doctype") and not frappe.has_permission(row["ref_doctype"], "read"):
			continue
		allowed.append(row)
	return {"reports": allowed}


@frappe.whitelist(methods=["POST"])
def create_scheduled_report(
	report: str, frequency: str = "Weekly", output_format: str = "HTML",
	email_to: str = "", day_of_week: str = "Monday", filters: dict | str | None = None,
) -> dict:
	"""Create an Auto Email Report the caller is entitled to run.

	Requires the report permission; if email is not configured the schedule is created
	DISABLED so nothing silently claims to send.
	"""
	_require_login()
	if not frappe.has_permission("Auto Email Report", "create"):
		frappe.throw(_("You do not have permission to create scheduled reports."), frappe.PermissionError)
	_may_use_report(report)
	if frequency not in FREQUENCIES:
		frappe.throw(_("Unsupported frequency."), frappe.ValidationError)
	if output_format not in FORMATS:
		frappe.throw(_("Unsupported format."), frappe.ValidationError)

	recipients = [addr.strip() for addr in str(email_to or "").replace(",", "\n").splitlines() if addr.strip()]
	if not recipients:
		frappe.throw(_("At least one recipient email is required."), frappe.ValidationError)

	email_ok = _email_configuration_status()["can_send_welcome_email"]
	ref_dt = frappe.db.get_value("Report", report, "ref_doctype")
	report_type = frappe.db.get_value("Report", report, "report_type")

	doc = frappe.get_doc({
		"doctype": "Auto Email Report",
		"report": report,
		"report_type": report_type,
		"reference_report": report,
		"user": frappe.session.user,
		"enabled": 1 if email_ok else 0,  # created disabled when email cannot deliver
		"frequency": frequency,
		"day_of_week": day_of_week,
		"format": output_format,
		"email_to": "\n".join(recipients),
		"filters": frappe.as_json(filters) if isinstance(filters, dict) else (filters or "{}"),
		"ref_doctype": ref_dt,
		"no_of_rows": 100,
		"send_if_data": 1,
	})
	doc.insert()
	return {
		"name": doc.name, "enabled": bool(doc.enabled),
		"email_configured": email_ok,
		"message": None if email_ok else _(
			"Email delivery is not configured, so this schedule was created DISABLED. "
			"Configure an outgoing Email Account, then enable it."),
	}


@frappe.whitelist(methods=["POST"])
def set_schedule_enabled(name: str, enabled: int | str) -> dict:
	"""Enable/disable a schedule the caller owns or manages."""
	_require_login()
	name = str(name or "").strip()
	if not frappe.db.exists("Auto Email Report", name):
		frappe.throw(_("Schedule not found."), frappe.DoesNotExistError)
	if not frappe.has_permission("Auto Email Report", "write", doc=name):
		frappe.throw(_("You do not have permission to change this schedule."), frappe.PermissionError)
	want = bool(cint(enabled))
	if want and not _email_configuration_status()["can_send_welcome_email"]:
		frappe.throw(_("Email delivery is not configured; cannot enable a schedule that cannot send."),
		             frappe.ValidationError)
	# Enabling requires the caller still has access to the report.
	if want:
		_may_use_report(frappe.db.get_value("Auto Email Report", name, "report"))
	frappe.db.set_value("Auto Email Report", name, "enabled", 1 if want else 0)
	return {"name": name, "enabled": want}
