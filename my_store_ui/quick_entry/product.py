"""Exact Product quick-create/edit workflow.

Atomic: a single whitelisted method that generates identifiers, creates the Item
through the standard controller, configures batch tracking, saves preferred stock
locations + reorder, and synchronises buying/selling Item Prices. Any failure rolls
the whole thing back. Stock quantity is NEVER stored on the Item — actual stock stays
in Bin/Stock Ledger via standard transactions.

Field order (business layout): Product ID, Image 1, Image 2, SKU, Product Name, Size,
Category, Material, Carton Qty, Stock Location 1-3, Re-Stock Qty, Cost Price, Margin,
Wholesale Price, Retail Price, Department Price.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils import cint, flt

# Product ID series (P100001, P100002, …) and SKU series (5001, 5002, …).
# make_autoname uses dots as format separators; literal chars stay, hashes become a
# zero-padded counter. "P1.#####" -> P100001; "5.###" -> 5001.
PRODUCT_ID_SERIES = "P1.#####"
SKU_SERIES = "5.###"
BATCH_SERIES = "BAT-.YYYY.-.######"

# Selling/buying prices synced to standard Item Price. Department added here.
PRICE_MAP = (
	{"field": "cost_price", "price_list": "Standard Buying", "flag": "buying", "site_default": True},
	{"field": "wholesale_price", "price_list": "Wholesale Price List", "flag": "selling"},
	{"field": "retail_price", "price_list": "Retail Price List", "flag": "selling"},
	{"field": "department_price", "price_list": "Department Price List", "flag": "selling"},
)

# Only these input keys are accepted (explicit allowlist — no arbitrary field mutation).
ALLOWED_KEYS = {
	"product_id", "image", "image_2", "product_name", "size", "category", "material",
	"carton_qty", "stock_location_1", "stock_location_2", "stock_location_3",
	"restock_qty", "cost_price", "margin", "wholesale_price", "retail_price", "department_price",
	"is_stock_item",
}


def _require_manager_for_cost() -> bool:
	return frappe.session.user == "Administrator" or bool(
		set(frappe.get_roles()) & {"Sales Master Manager", "Purchase Master Manager", "Item Manager", "System Manager"})


def _clean(values) -> dict:
	data = frappe.parse_json(values) if isinstance(values, str) else values
	if not isinstance(data, dict):
		frappe.throw(_("Invalid product details."), frappe.ValidationError)
	unknown = set(data) - ALLOWED_KEYS
	if unknown:
		frappe.throw(_("Unsupported field: {0}").format(", ".join(sorted(unknown))), frappe.ValidationError)
	return data


def _validate_warehouse(name: str, company: str, seen: set) -> None:
	if not name:
		return
	if name in seen:
		frappe.throw(_("Each stock location must be different."), frappe.ValidationError)
	seen.add(name)
	row = frappe.db.get_value("Warehouse", name, ["company", "disabled", "is_group"], as_dict=True)
	if not row:
		frappe.throw(_("Warehouse {0} does not exist.").format(name), frappe.ValidationError)
	if row.disabled or row.is_group:
		frappe.throw(_("Warehouse {0} cannot be used.").format(name), frappe.ValidationError)
	if company and row.company != company:
		frappe.throw(_("Warehouse {0} belongs to another company.").format(name), frappe.PermissionError)


@frappe.whitelist(methods=["POST"])
def create_product(values: dict | str, name: str | None = None):
	"""Create or edit a Product atomically. name set = edit."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	data = _clean(values)
	company = frappe.defaults.get_global_default("company") or (
		frappe.get_all("Company", pluck="name", limit_page_length=1) or [None])[0]

	editing = bool(name)
	if editing:
		if not frappe.db.exists("Item", name):
			frappe.throw(_("Product not found."), frappe.DoesNotExistError)
		doc = frappe.get_doc("Item", name)
		if not frappe.has_permission("Item", "write", doc=doc):
			frappe.throw(_("You cannot edit this product."), frappe.PermissionError)
	else:
		if not frappe.has_permission("Item", "create"):
			frappe.throw(_("You cannot create products."), frappe.PermissionError)
		doc = frappe.new_doc("Item")

	# --- required + validation ---
	product_name = str(data.get("product_name") or "").strip()
	if not product_name:
		frappe.throw(_("Product Name is required."), frappe.ValidationError)
	category = str(data.get("category") or "").strip()
	if not category or not frappe.db.exists("Item Group", {"name": category, "is_group": 0}):
		frappe.throw(_("A valid Category is required."), frappe.ValidationError)
	if flt(data.get("carton_qty")) < 0:
		frappe.throw(_("Carton Qty cannot be negative."), frappe.ValidationError)
	if flt(data.get("restock_qty")) < 0:
		frappe.throw(_("Re-Stock Qty cannot be negative."), frappe.ValidationError)
	for key in ("cost_price", "wholesale_price", "retail_price", "department_price", "margin"):
		if flt(data.get(key)) < 0:
			frappe.throw(_("{0} cannot be negative.").format(key), frappe.ValidationError)

	seen: set = set()
	locations = [data.get("stock_location_1"), data.get("stock_location_2"), data.get("stock_location_3")]
	for loc in locations:
		_validate_warehouse(str(loc).strip() if loc else "", company, seen)

	is_stock_item = cint(data.get("is_stock_item", 1))

	# --- identifiers (server-side, concurrency-safe) ---
	if not editing:
		doc.item_code = make_autoname(PRODUCT_ID_SERIES)
		doc.custom_sku = make_autoname(SKU_SERIES)
		doc.stock_uom = "Nos"
		doc.item_group = category
		# New stock products are batch-managed.
		if is_stock_item:
			doc.has_batch_no = 1
			doc.create_new_batch = 1
			doc.batch_number_series = BATCH_SERIES
	# item_code / custom_sku are immutable on edit (never regenerated).

	doc.item_name = product_name
	doc.is_stock_item = is_stock_item
	doc.item_group = category
	doc.image = str(data.get("image") or "").strip() or None
	doc.custom_image_2 = str(data.get("image_2") or "").strip() or None
	doc.custom_product_size = str(data.get("size") or "").strip() or None
	doc.custom_product_material = str(data.get("material") or "").strip() or None
	doc.custom_carton_qty = flt(data.get("carton_qty"))
	doc.custom_margin = flt(data.get("margin"))
	doc.custom_stock_location_1 = locations[0] or None
	doc.custom_stock_location_2 = locations[1] or None
	doc.custom_stock_location_3 = locations[2] or None
	# Computed pricing fields kept for the form + downstream sync.
	doc.custom_purchase_price = flt(data.get("cost_price"))
	doc.custom_wholesale_price = flt(data.get("wholesale_price"))
	doc.custom_retail_price = flt(data.get("retail_price"))
	doc.custom_department_price = flt(data.get("department_price"))

	# Location 1 → the standard company default warehouse (item_defaults).
	if locations[0] and company:
		rows = [r for r in doc.get("item_defaults", []) if r.company == company]
		target = rows[0] if rows else doc.append("item_defaults", {"company": company})
		target.default_warehouse = locations[0]

	# Re-Stock Qty → standard Item Reorder row on location 1.
	if locations[0] and flt(data.get("restock_qty")) > 0:
		existing = [r for r in doc.get("reorder_levels", []) if r.warehouse == locations[0]]
		row = existing[0] if existing else doc.append("reorder_levels", {"warehouse": locations[0]})
		row.warehouse_reorder_qty = flt(data.get("restock_qty"))
		if not row.get("warehouse_reorder_level"):
			row.warehouse_reorder_level = flt(data.get("restock_qty"))
		if not row.get("material_request_type"):
			row.material_request_type = "Purchase"

	if editing:
		doc.save()
	else:
		doc.insert()

	_sync_item_prices(doc, data)

	return {
		"name": doc.name, "product_id": doc.item_code, "sku": doc.custom_sku,
		"route": f"/inventory/products/{doc.name}",
	}


def _price_list_ok(price_list: str, flag: str) -> str | None:
	row = frappe.db.get_value("Price List", {"name": price_list, "enabled": 1}, ["name", flag], as_dict=True)
	if not row or not row.get(flag):
		return None
	return row["name"]


def _sync_item_prices(doc, data: dict) -> None:
	"""Upsert one standard Item Price per configured list; no duplicates; atomic."""
	# Writing Item Price needs the master-manager permission; gate before the first write.
	actions = set()
	plan = []
	stock_uom = doc.stock_uom
	for spec in PRICE_MAP:
		price_list = spec["price_list"]
		if spec.get("site_default"):
			price_list = frappe.db.get_single_value("Buying Settings", "buying_price_list") or price_list
		usable = _price_list_ok(price_list, spec["flag"])
		if not usable:
			continue
		rate = flt(data.get(spec["field"]))
		owned = [
			row for row in frappe.get_all(
				"Item Price", filters={"item_code": doc.name, "price_list": usable},
				fields=["name", "price_list_rate", "uom", "customer", "supplier", "batch_no"], order_by="creation asc")
			if (not row.uom or row.uom == stock_uom) and not row.customer and not row.supplier and not row.batch_no
		]
		plan.append((usable, rate, owned))
		if rate <= 0 and owned:
			actions.add("delete")
		elif rate > 0 and not owned:
			actions.add("create")
		elif rate > 0 and owned and (len(owned) > 1 or flt(owned[0].price_list_rate) != rate):
			actions.add("write")
			if len(owned) > 1:
				actions.add("delete")
	if not actions:
		return
	missing = sorted(a for a in actions if not frappe.has_permission("Item Price", a))
	if missing:
		frappe.throw(_("Saving prices needs {0} permission on Item Price. Ask for the Sales Master "
		               "Manager role, or clear the price fields.").format(", ".join(missing)), frappe.PermissionError)

	for price_list, rate, owned in plan:
		if rate <= 0:
			for row in owned:
				frappe.delete_doc("Item Price", row.name, ignore_permissions=False)
			continue
		if not owned:
			frappe.get_doc({"doctype": "Item Price", "item_code": doc.name, "price_list": price_list,
			                "price_list_rate": rate, "uom": stock_uom}).insert()
			continue
		primary, *dups = owned
		for row in dups:
			frappe.delete_doc("Item Price", row.name, ignore_permissions=False)
		if flt(primary.price_list_rate) != rate:
			ip = frappe.get_doc("Item Price", primary.name)
			ip.price_list_rate = rate
			ip.save()


@frappe.whitelist(methods=["GET"])
def get_product(name: str) -> dict:
	"""Load a product's simplified fields for the edit form."""
	if not frappe.has_permission("Item", "read", doc=name):
		frappe.throw(_("Not permitted."), frappe.PermissionError)
	doc = frappe.get_doc("Item", name)
	prices = {
		row.price_list: flt(row.price_list_rate)
		for row in frappe.get_all("Item Price", filters={"item_code": name},
		                          fields=["price_list", "price_list_rate", "customer", "supplier"])
		if not row.customer and not row.supplier
	}
	show_cost = _require_manager_for_cost()
	return {
		"name": doc.name, "product_id": doc.item_code, "sku": doc.custom_sku,
		"product_name": doc.item_name, "image": doc.image, "image_2": doc.custom_image_2,
		"size": doc.custom_product_size, "category": doc.item_group, "material": doc.custom_product_material,
		"carton_qty": flt(doc.custom_carton_qty), "margin": flt(doc.custom_margin),
		"stock_location_1": doc.custom_stock_location_1, "stock_location_2": doc.custom_stock_location_2,
		"stock_location_3": doc.custom_stock_location_3,
		"restock_qty": flt(next((r.warehouse_reorder_qty for r in doc.reorder_levels), 0)),
		"cost_price": prices.get(frappe.db.get_single_value("Buying Settings", "buying_price_list") or "Standard Buying") if show_cost else None,
		"wholesale_price": prices.get("Wholesale Price List"),
		"retail_price": prices.get("Retail Price List"),
		"department_price": prices.get("Department Price List"),
		"is_batch_managed": bool(doc.has_batch_no),
		"is_stock_item": bool(doc.is_stock_item),
		"cost_visible": show_cost,
		"created": str(doc.creation),
	}
