"""Every Delivery Note passes the credit gate, whatever created it.

`wholesale.delivery.create_delivery_note` checks a customer's payment and credit
position before goods leave the warehouse, and demands a manager's override with
a written reason when they are short. That check lived in that one endpoint.

It was not the only way to make a Delivery Note. `form_api.save_entity_form`
builds one from the `delivery_notes` schema and `document_actions` submits it,
and neither consults the gate -- so a cashier could dispatch to a Non-Credit
customer who had paid nothing simply by using the generic form instead of the
wholesale screen. The guard written for exactly this, `create_via_mapping_only`,
is read in two places in form_api.py and set on no schema, so it never fired.

Setting that flag would close the generic form. It would not close the REST API,
the ERPNext desk, or a data import. A `before_submit` hook closes all of them at
once, because submitting is what moves the stock.

A manager's override is honoured rather than re-litigated: create_delivery_note
records one in the comment trail, so a note approved by a manager can still be
submitted later by the warehouse clerk who actually loads the van.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt

from my_store_ui.wholesale.credit import (
	MANAGER_ROLES,
	evaluate_delivery_gate,
	evaluate_sales_order_delivery_gate,
)

OVERRIDE_MARKER = "Credit/payment override by"


def _caller_is_manager() -> bool:
	roles = set(frappe.get_roles(frappe.session.user))
	return bool(roles & set(MANAGER_ROLES)) or "System Manager" in roles


def _has_recorded_override(doc) -> bool:
	"""True when a manager already approved this dispatch on the record."""
	if not doc.get("name"):
		return False
	return bool(
		frappe.get_all(
			"Comment",
			filters={
				"reference_doctype": "Delivery Note",
				"reference_name": doc.name,
				"comment_type": "Info",
				"content": ["like", f"{OVERRIDE_MARKER}%"],
			},
			pluck="name",
			limit_page_length=1,
		)
	)


def _audit(doc, gate: dict, sales_order: str | None) -> None:
	frappe.get_doc({
		"doctype": "Comment", "comment_type": "Info", "reference_doctype": "Delivery Note",
		"reference_name": doc.name,
		"content": _("{0} {1}: {2} (order {3}, unpaid {4}). Approved on submit.").format(
			OVERRIDE_MARKER, frappe.session.user, gate.get("reason"),
			sales_order or _("none"), gate.get("unpaid_amount"),
		),
	}).insert(ignore_permissions=True)


def _enforce(doc, gate: dict, sales_order: str | None) -> None:
	"""Block the dispatch, or let an authorised manager through on the record."""
	if gate.get("allowed"):
		return

	# An unclassified customer is a gap in the data, not a credit judgement, and
	# on this site it is the norm rather than the exception: 28 of 29 customers
	# have no credit type set. Enforcing it here would stop nearly every dispatch
	# by anyone below manager -- breaking the business to close a hole. The
	# wholesale screen still asks a manager to classify the customer; this hook
	# only enforces decisions the data actually supports.
	if not (gate.get("status") or {}).get("credit_type"):
		return

	if not gate.get("requires_manager_approval"):
		frappe.throw(gate.get("reason") or _("This delivery is not permitted."), frappe.ValidationError)
	if not _caller_is_manager():
		frappe.throw(
			_("{0} Only an authorised manager can release this delivery.").format(gate.get("reason") or ""),
			frappe.PermissionError,
		)
	_audit(doc, gate, sales_order)


def enforce_delivery_gate(doc, method=None) -> None:
	"""Refuse to submit a dispatch the customer's credit position does not allow."""
	# A return brings goods back in. No credit is being extended, and the
	# original dispatch was already gated when it went out.
	if cint(doc.get("is_return")):
		return
	if _has_recorded_override(doc):
		return

	orders = sorted({
		row.get("against_sales_order")
		for row in doc.get("items") or []
		if row.get("against_sales_order")
	})

	if orders:
		# The order carries the real payment position: what it is worth, and what
		# has actually been received against it or its invoices.
		for sales_order in orders:
			_enforce(doc, evaluate_sales_order_delivery_gate(sales_order), sales_order)
		return

	# A direct dispatch with no order behind it still extends credit, so it is
	# judged on the note's own value against the customer's standing.
	_enforce(
		doc,
		evaluate_delivery_gate(
			customer=doc.get("customer"),
			company=doc.get("company"),
			incremental_amount=flt(doc.get("grand_total")),
		),
		None,
	)
