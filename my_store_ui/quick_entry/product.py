"""Exact Product quick-create/edit workflow.

Atomic: a single whitelisted method that generates identifiers, creates the Item
through the standard controller, configures batch tracking, saves preferred stock
locations + reorder, and synchronises buying/selling Item Prices. Any failure rolls
the whole thing back. Stock quantity is NEVER stored on the Item — actual stock stays
in Bin/Stock Ledger via standard transactions.

Field order (business layout): Product ID, Image 1, Image 2, SKU, Product Name,
Product Category, Carton Qty, Size / Material / Carpet Category (carpets only),
Stock Location 1-3, Re-Stock Qty, Cost Price, Wholesale Price, Department Price,
Retail Price.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils import cint, flt

from my_store_ui.my_store_ui.doctype.retail_price_code.retail_price_code import (
	issue_sku,
	peek_next_sku,
)
from my_store_ui.wholesale.uom import CARTON_UOM, sync_carton_uom

# Product ID series (PID00001, PID00002, …). make_autoname uses dots as format
# separators; literal chars stay, hashes become a zero-padded counter.
# "PID.#####" -> PID00001.
PRODUCT_ID_SERIES = "PID.#####"
PRODUCT_ID_PREFIX = "PID"
# Fallback SKU series for a product saved without a price code. A product that
# carries one is numbered by the code itself (CCA 1, CCA 2 …) instead.
SKU_SERIES = "5.###"
BATCH_SERIES = "BAT-.YYYY.-.######"

# The category whose products carry Size, Material and a Carpet Category. Set by
# the system, not chosen by the user: those three fields appear exactly when the
# selected product category is Carpets (or sits underneath it).
CARPET_CATEGORY = "Carpets"

# Third selling list from the requirements document. Created on demand so a site
# that has never used it still works.
DEPARTMENT_PRICE_LIST = "Department Price List"

# Three selling prices (Wholesale, Retail, Department) plus the buying Cost Price,
# as listed in ACCOUNT CREATION.docx. All standard Item Price rows.
PRICE_MAP = (
	{"field": "cost_price", "price_list": "Standard Buying", "flag": "buying", "site_default": True},
	{"field": "wholesale_price", "price_list": "Wholesale Price List", "flag": "selling"},
	{"field": "retail_price", "price_list": "Retail Price List", "flag": "selling"},
	{"field": "department_price", "price_list": DEPARTMENT_PRICE_LIST, "flag": "selling"},
)

# Only these input keys are accepted (explicit allowlist — no arbitrary field mutation).
# "margin" is still accepted so an integration that has always sent it keeps working;
# the Product form no longer offers it.
ALLOWED_KEYS = {
	"product_id", "image", "image_2", "product_name", "size", "category", "material",
	"carpet_category", "price_code", "carton_qty", "stock_location_1", "stock_location_2",
	"stock_location_3", "restock_qty", "cost_price", "margin", "wholesale_price",
	"retail_price", "department_price", "is_stock_item",
}


def is_carpet_category(category: str) -> bool:
	"""Whether this category is Carpets, or sits underneath it.

	Walks the Item Group tree upward so a sub-category such as "Hand-Knotted
	Carpets" also gets the carpet-only fields, rather than only an exact match.
	"""
	seen: set[str] = set()
	current = str(category or "").strip()
	while current and current not in seen:
		if current.strip().lower() == CARPET_CATEGORY.lower():
			return True
		seen.add(current)
		current = frappe.db.get_value("Item Group", current, "parent_item_group") or ""
	return False


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
	"""Create or edit a Product atomically. name set = edit.

	Wrapped in a savepoint so a failure at any step (e.g. the Item Price permission
	gate) rolls back the whole operation -- atomic even outside an HTTP request.
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	sp = "product_quick_entry"
	frappe.db.savepoint(sp)
	try:
		return _create_product(values, name)
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise


def _create_product(values: dict | str, name: str | None = None):
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
		frappe.throw(_("A valid Product Category is required."), frappe.ValidationError)
	carpet = is_carpet_category(category)

	price_code = str(data.get("price_code") or "").strip().upper()
	if price_code:
		code_row = frappe.db.get_value(
			"Retail Price Code", price_code, ["name", "category", "is_active"], as_dict=True)
		if not code_row:
			frappe.throw(_("Price Code {0} does not exist.").format(price_code), frappe.ValidationError)
		if not code_row.is_active:
			frappe.throw(_("Price Code {0} is no longer active.").format(price_code), frappe.ValidationError)
		# The codes are category-wise, so a code from another category on this
		# product would make the SKU say something the product is not.
		if code_row.category != category:
			frappe.throw(
				_("Price Code {0} belongs to {1}, not {2}.").format(
					price_code, code_row.category, category),
				frappe.ValidationError,
			)
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
		# A price code numbers its own products (CCA 1, CCA 2 …); without one the
		# product falls back to the plain SKU series.
		doc.custom_sku = issue_sku(price_code) if price_code else make_autoname(SKU_SERIES)
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
	# Size, Material and Carpet Category belong to carpets only. Anything sent for a
	# non-carpet product is cleared rather than stored, so moving a product out of
	# Carpets cannot leave stale carpet attributes behind it.
	doc.custom_product_size = (str(data.get("size") or "").strip() or None) if carpet else None
	doc.custom_product_material = (str(data.get("material") or "").strip() or None) if carpet else None
	if doc.meta.get_field("custom_carpet_category"):
		doc.custom_carpet_category = (
			str(data.get("carpet_category") or "").strip() or None) if carpet else None
	if doc.meta.get_field("custom_price_code"):
		# Immutable on edit: it is already baked into this product's SKU.
		if not editing:
			doc.custom_price_code = price_code or None
	doc.custom_carton_qty = flt(data.get("carton_qty"))
	# Carton Qty is a real UOM conversion, not a display number: mirror it onto
	# Item.uoms so every sales/purchase document converts through ERPNext itself.
	sync_carton_uom(doc, doc.custom_carton_qty)
	# The Product form no longer offers Margin. Only write it when the caller
	# actually sent it, so saving through the form leaves an existing value alone
	# instead of silently resetting it to zero.
	if "margin" in data:
		doc.custom_margin = flt(data.get("margin"))
	doc.custom_stock_location_1 = locations[0] or None
	doc.custom_stock_location_2 = locations[1] or None
	doc.custom_stock_location_3 = locations[2] or None
	# Computed pricing fields kept for the form + downstream sync.
	doc.custom_purchase_price = flt(data.get("cost_price"))
	doc.custom_wholesale_price = flt(data.get("wholesale_price"))
	doc.custom_retail_price = flt(data.get("retail_price"))

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
		"price_code": doc.get("custom_price_code"),
		"route": f"/inventory/products/{doc.name}",
	}


@frappe.whitelist(methods=["GET"])
def preview_identifiers(price_code: str = "") -> dict:
	"""The Product ID and SKU the next product would receive.

	A preview, not a reservation: it reads the counters without advancing them, so
	opening the form ten times does not burn ten numbers. The real values are
	settled at save time, which is why the form labels these as previews.
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	# tabSeries is Frappe's own counter table, not a DocType, so it is read the way
	# Frappe reads it -- and without FOR UPDATE, because this only looks.
	row = frappe.db.sql("SELECT `current` FROM `tabSeries` WHERE `name` = %s",
	                    (PRODUCT_ID_PREFIX,))
	current = cint(row[0][0]) if row and row[0][0] is not None else 0
	# Width comes from the series definition rather than a repeated literal, so
	# changing PRODUCT_ID_SERIES cannot make the preview disagree with the real name.
	digits = len(PRODUCT_ID_SERIES.split(".")[-1])
	product_id = f"{PRODUCT_ID_PREFIX}{current + 1:0{digits}d}"
	code = str(price_code or "").strip().upper()
	return {
		"product_id": product_id,
		"sku": peek_next_sku(code) if code else None,
		"price_code": code or None,
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
		"carpet_category": doc.get("custom_carpet_category"),
		"price_code": doc.get("custom_price_code"),
		"is_carpet": is_carpet_category(doc.item_group),
		"carton_qty": flt(doc.custom_carton_qty), "margin": flt(doc.custom_margin),
		"stock_location_1": doc.custom_stock_location_1, "stock_location_2": doc.custom_stock_location_2,
		"stock_location_3": doc.custom_stock_location_3,
		"restock_qty": flt(next((r.warehouse_reorder_qty for r in doc.reorder_levels), 0)),
		"cost_price": prices.get(frappe.db.get_single_value("Buying Settings", "buying_price_list") or "Standard Buying") if show_cost else None,
		"wholesale_price": prices.get("Wholesale Price List"),
		"retail_price": prices.get("Retail Price List"),
		"department_price": prices.get(DEPARTMENT_PRICE_LIST),
		"is_batch_managed": bool(doc.has_batch_no),
		"is_stock_item": bool(doc.is_stock_item),
		"cost_visible": show_cost,
		"created": str(doc.creation),
	}


# --- Default margin -------------------------------------------------------
# The Product form's "Set default" action stores the percentage so future
# products start from it. Held in Stock Settings' own defaults table via a
# Singles-backed key so it survives migrate without a bespoke DocType.
DEFAULT_MARGIN_KEY = "my_store_ui_default_margin"


def _margin_managers() -> bool:
	return frappe.session.user == "Administrator" or bool(
		set(frappe.get_roles()) & {"Item Manager", "System Manager", "Sales Master Manager",
		                           "Purchase Master Manager"})


@frappe.whitelist(methods=["GET"])
def get_default_margin():
	"""The saved default margin percentage, or None when never set."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	value = frappe.db.get_default(DEFAULT_MARGIN_KEY)
	return {"margin": flt(value) if value not in (None, "") else None}


@frappe.whitelist(methods=["POST"])
def save_default_margin(margin: float):
	"""Store the default margin for future products. Authorised roles only."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	if not _margin_managers():
		frappe.throw(_("You cannot change the default margin."), frappe.PermissionError)
	value = flt(margin)
	if value < 0 or value > 100:
		frappe.throw(_("Margin must be between 0 and 100."), frappe.ValidationError)
	frappe.db.set_default(DEFAULT_MARGIN_KEY, value)
	return {"margin": value}
