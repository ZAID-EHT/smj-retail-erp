"""Phase 9 — email, templates and notification status (safe, read-focused).

Exposes the standard Frappe email records for administration visibility without
ever returning or logging a credential. Configuring an outgoing Email Account with
real SMTP credentials is an external step (see docs/email/SMJ_EMAIL_SETUP.md); this
surface reports truthfully whether it has been done and lets managers review the
templates and notifications that would be used.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

from my_store_ui.access_management import _email_configuration_status, _require_user_manager

# Notifications relevant to the wholesale workflow, surfaced for review.
RELEVANT_EVENTS = ("Sales Order", "Sales Invoice", "Payment Entry", "Delivery Note",
                   "Purchase Order", "Purchase Receipt")


@frappe.whitelist(methods=["GET"])
def get_email_overview() -> dict:
	"""Delivery status plus template/notification/queue summary. No credentials."""
	_require_user_manager()
	return {
		"delivery": _email_configuration_status(),
		"templates": _templates(),
		"notifications": _notifications(),
		"queue": _queue_status(),
	}


def _templates() -> list[dict]:
	if not frappe.has_permission("Email Template", "read"):
		return []
	return frappe.get_list(
		"Email Template", fields=["name", "subject", "use_html"],
		order_by="name asc", limit_page_length=100,
	)


def _notifications() -> list[dict]:
	if not frappe.has_permission("Notification", "read"):
		return []
	rows = frappe.get_list(
		"Notification",
		fields=["name", "subject", "document_type", "event", "enabled", "channel"],
		order_by="document_type asc", limit_page_length=200,
	)
	# Flag the ones tied to core wholesale documents.
	for row in rows:
		row["wholesale_relevant"] = row.get("document_type") in RELEVANT_EVENTS
	return rows


def _queue_status() -> dict:
	"""Email Queue counts by status over the last 7 days. No recipients, no content."""
	if not frappe.has_permission("Email Queue", "read"):
		return {"available": False}
	since = frappe.utils.add_days(frappe.utils.now_datetime(), -7)
	rows = frappe.db.sql(
		"""SELECT status, COUNT(*) AS count FROM `tabEmail Queue`
		   WHERE creation > %s GROUP BY status""",
		since, as_dict=True,
	)
	by_status = {r["status"]: r["count"] for r in rows}
	return {
		"available": True,
		"since_days": 7,
		"sent": cint(by_status.get("Sent")),
		"not_sent": cint(by_status.get("Not Sent")),
		"error": cint(by_status.get("Error")),
		"by_status": by_status,
	}


@frappe.whitelist(methods=["GET"])
def get_notification_coverage() -> dict:
	"""Which wholesale events have an enabled notification, and which do not."""
	_require_user_manager()
	notifications = _notifications()
	enabled_docs = {n["document_type"] for n in notifications if n.get("enabled")}
	coverage = [
		{"event": event, "has_enabled_notification": event in enabled_docs}
		for event in RELEVANT_EVENTS
	]
	return {"coverage": coverage, "email_can_send": _email_configuration_status()["can_send_welcome_email"]}
