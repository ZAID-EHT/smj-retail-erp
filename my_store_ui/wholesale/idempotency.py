"""Database-backed idempotency for document-creating endpoints.

A retried request (double-click, flaky network, client retry) must never dispatch
the same goods or raise the same invoice twice. The key is therefore stored on the
document itself in ``custom_request_id`` and looked up in the database.

The cache is deliberately *not* the source of truth: a Redis restart, eviction, or
an execution context where the cache does not persist would silently re-enable
duplicates. It is used only as a fast path in front of the authoritative query.
"""

from __future__ import annotations

import frappe
from frappe import _

REQUEST_ID_FIELD = "custom_request_id"
MAX_LENGTH = 80


def normalise(request_id: str | None, required: bool = False) -> str:
	value = (request_id or "").strip()
	if not value:
		if required:
			frappe.throw(_("A valid request ID is required."), frappe.ValidationError)
		return ""
	if len(value) > MAX_LENGTH:
		frappe.throw(_("The request ID is too long."), frappe.ValidationError)
	return value


def supported(doctype: str) -> bool:
	return bool(frappe.get_meta(doctype).get_field(REQUEST_ID_FIELD))


def _cache_key(doctype: str, request_id: str) -> str:
	return f"my_store_ui:idem:{doctype}:{frappe.session.user}:{request_id}"


def find_existing(doctype: str, request_id: str) -> str | None:
	"""The document already created for this request id, if any."""
	if not request_id:
		return None
	cached = frappe.cache.get_value(_cache_key(doctype, request_id))
	if cached and frappe.db.exists(doctype, cached):
		return cached
	if not supported(doctype):
		return None
	name = frappe.db.get_value(doctype, {REQUEST_ID_FIELD: request_id}, "name")
	return name or None


def remember(doctype: str, request_id: str, name: str) -> None:
	if not request_id:
		return
	frappe.cache.set_value(_cache_key(doctype, request_id), name, expires_in_sec=3600)


def stamp(doc, request_id: str) -> None:
	"""Write the idempotency key onto the document before it is inserted."""
	if not request_id:
		return
	if supported(doc.doctype):
		doc.set(REQUEST_ID_FIELD, request_id)
