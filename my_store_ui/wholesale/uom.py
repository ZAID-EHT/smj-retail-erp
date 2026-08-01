"""Carton/Unit UOM resolution for wholesale selling and buying.

A wholesale line is entered either in the item's stock UOM ("Unit") or in Cartons.
Cartons are a real standard ERPNext UOM conversion -- a ``UOM Conversion Detail``
row on the Item -- not a display-only number, so every downstream document (Sales
Order, Delivery Note, Sales Invoice, Purchase Order, Purchase Receipt, Purchase
Invoice) converts to stock qty through ERPNext's own controllers.

The single source of truth for the factor is ``Item.uoms``. ``custom_carton_qty``
is the input on the Product form; :func:`sync_carton_uom` mirrors it into the
conversion table so the two can never disagree.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

CARTON_UOM = "Carton"


def ensure_carton_uom() -> str:
	"""Make sure the Carton UOM record exists. Idempotent."""
	if not frappe.db.exists("UOM", CARTON_UOM):
		doc = frappe.new_doc("UOM")
		doc.uom_name = CARTON_UOM
		# A carton is a discrete physical box -- partial cartons are sold as loose units.
		doc.must_be_whole_number = 1
		doc.insert(ignore_permissions=True)
	return CARTON_UOM


def sync_carton_uom(doc, carton_qty: float) -> None:
	"""Mirror Carton Qty onto the Item's UOM conversion table.

	``carton_qty`` is how many stock units are in one carton. A value of 0 (or 1,
	which would make Carton meaningless) removes the Carton conversion. The stock
	UOM row is never touched -- ERPNext requires it at factor 1.
	"""
	carton_qty = flt(carton_qty)
	rows = [r for r in (doc.get("uoms") or []) if r.uom != CARTON_UOM]
	if carton_qty > 1:
		ensure_carton_uom()
		doc.set("uoms", rows)
		doc.append("uoms", {"uom": CARTON_UOM, "conversion_factor": carton_qty})
	else:
		doc.set("uoms", rows)
	# ERPNext validates that the stock UOM is present at factor 1.
	if not any(r.uom == doc.stock_uom for r in (doc.get("uoms") or [])):
		doc.append("uoms", {"uom": doc.stock_uom, "conversion_factor": 1.0})


def conversion_factor(item_code: str, uom: str | None) -> float:
	"""Validated stock-units-per-``uom`` for an item.

	Only UOMs actually declared on the Item are accepted, so a caller cannot invent
	a factor and inflate or deflate the stock movement.
	"""
	item_code = (item_code or "").strip()
	stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
	if not stock_uom:
		frappe.throw(_("Invalid Item: {0}").format(item_code))
	uom = (uom or "").strip() or stock_uom
	if uom == stock_uom:
		return 1.0
	factor = frappe.db.get_value(
		"UOM Conversion Detail", {"parent": item_code, "parenttype": "Item", "uom": uom}, "conversion_factor"
	)
	if not factor or flt(factor) <= 0:
		frappe.throw(
			_("{0} is not a valid unit for {1}. Allowed: {2}.").format(
				uom, item_code, ", ".join(allowed_uoms(item_code))
			),
			frappe.ValidationError,
		)
	return flt(factor)


def allowed_uoms(item_code: str) -> list[str]:
	stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
	names = frappe.get_all(
		"UOM Conversion Detail", filters={"parent": item_code, "parenttype": "Item"}, pluck="uom"
	)
	if stock_uom and stock_uom not in names:
		names.append(stock_uom)
	return sorted(set(names))


def to_stock_qty(item_code: str, qty: float, uom: str | None) -> float:
	"""Convert an entered quantity into stock units."""
	return flt(qty) * conversion_factor(item_code, uom)


@frappe.whitelist(methods=["GET"])
def get_item_uoms(item_code: str):
	"""UOM choices for one item, for the Unit/Carton selector."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please sign in."), frappe.PermissionError)
	item_code = (item_code or "").strip()
	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Invalid Item: {0}").format(item_code))
	if not frappe.has_permission("Item", "read", doc=item_code):
		frappe.throw(_("You do not have permission to read this product."), frappe.PermissionError)
	stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
	out = []
	for uom in allowed_uoms(item_code):
		out.append({
			"uom": uom,
			"conversion_factor": conversion_factor(item_code, uom),
			"is_stock_uom": uom == stock_uom,
		})
	return {"item_code": item_code, "stock_uom": stock_uom, "uoms": out}
