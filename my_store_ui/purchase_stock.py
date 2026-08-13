"""Every Purchase Invoice moves stock.

SMJ receives the goods and the supplier's bill together: the shipment lands and
the invoice is entered. ERPNext, though, treats a Purchase Invoice as a bill
only -- unless `update_stock` is ticked it records the money and touches no
stock at all, and the cost strands itself in "Stock Received But Not Billed"
waiting for a Purchase Receipt that this business never raises. An invoice
saved that way looks completely correct while the shelf stays empty, which is
exactly how ACC-PINV-2026-00055 billed LKR 448,000 for 2,000 units that never
appeared in stock.

Defaulting the checkbox to ticked was not enough: it can still be unticked, and
a stale browser tab or a desk user would not see the default at all. This runs
as a `validate` hook, so it holds on every path into the document -- the Retail
ERP UI, the ERPNext desk, the REST API and data import alike.

The one case that must NOT be forced is an invoice whose goods already arrived
on a Purchase Receipt. That receipt has moved the stock; updating stock again
here would count the same carton twice.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint


def _already_received(doc) -> bool:
	"""True when a Purchase Receipt has already brought these goods into stock."""
	return any(row.get("purchase_receipt") for row in doc.get("items") or [])


def _default_warehouse(doc, row) -> str | None:
	"""Warehouse for a row that has none, mirroring ERPNext's own precedence."""
	if doc.get("set_warehouse"):
		return doc.set_warehouse
	if row.get("item_code"):
		default = frappe.db.get_value(
			"Item Default",
			{"parent": row.item_code, "company": doc.company},
			"default_warehouse",
		)
		if default:
			return default
	return frappe.db.get_value("Stock Settings", None, "default_warehouse") or None


def force_update_stock(doc, method=None) -> None:
	"""Make the invoice post stock unless a Purchase Receipt already did."""
	if _already_received(doc):
		return

	# A debit note reverses whatever its original invoice did. Forcing stock
	# movement on a return whose original never moved any would drive the item
	# negative for a receipt that never happened.
	if cint(doc.get("is_return")) and doc.get("return_against"):
		original = frappe.db.get_value("Purchase Invoice", doc.return_against, "update_stock")
		doc.update_stock = cint(original)
		return

	doc.update_stock = 1

	# update_stock makes the row warehouse mandatory. Filling it from the
	# document, then the Item's own default, keeps the common case silent
	# instead of failing on a field the form no longer asks about.
	missing = []
	for row in doc.get("items") or []:
		if row.get("warehouse"):
			continue
		row.warehouse = _default_warehouse(doc, row)
		if not row.warehouse:
			missing.append(row.item_code or _("Row {0}").format(row.idx))
	if missing:
		frappe.throw(
			_("Set a warehouse for: {0}. Every purchase invoice brings stock in, so each line needs somewhere to put it.")
			.format(", ".join(str(item) for item in missing)),
			frappe.ValidationError,
		)
