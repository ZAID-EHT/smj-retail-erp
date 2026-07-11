from __future__ import annotations

import json
from datetime import timedelta

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Please sign in to use Smart Sales."), frappe.PermissionError)


def _require_permission(doctype: str, permission_type: str = "read") -> None:
	if not frappe.has_permission(doctype, permission_type):
		frappe.throw(
			_("You do not have {0} permission for {1}.").format(permission_type, doctype),
			frappe.PermissionError,
		)


def _default_company() -> str | None:
	return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)


def _default_price_list() -> str | None:
	return frappe.defaults.get_user_default("Selling Price List") or frappe.db.get_single_value(
		"Selling Settings", "selling_price_list"
	)


def _validate_link(doctype: str, name: str | None, filters: dict | None = None) -> None:
	if not name:
		return
	filters = {"name": name, **(filters or {})}
	if not frappe.db.exists(doctype, filters):
		frappe.throw(_("Invalid {0}: {1}").format(doctype, name))
	if not frappe.has_permission(doctype, "read", doc=name):
		frappe.throw(_("You do not have permission to use {0} {1}.").format(doctype, name), frappe.PermissionError)


@frappe.whitelist()
def get_bootstrap(page: int = 1, page_length: int = 24, search: str = "", item_group: str = "", warehouse: str = "", price_list: str = ""):
	"""Return a permission-filtered, paginated catalogue and selector options."""
	_require_login()
	_require_permission("Item")

	page = max(cint(page), 1)
	page_length = min(max(cint(page_length), 1), 48)
	company = _default_company()
	price_list = price_list or _default_price_list() or "Standard Selling"
	_validate_link("Company", company)
	_validate_link("Price List", price_list, {"enabled": 1, "selling": 1})
	if warehouse:
		_validate_link("Warehouse", warehouse, {"disabled": 0, "is_group": 0})

	filters: dict = {"disabled": 0, "is_sales_item": 1}
	if item_group:
		filters["item_group"] = item_group

	or_filters = None
	search = (search or "").strip()
	if search:
		like = f"%{search}%"
		or_filters = {
			"item_code": ["like", like],
			"item_name": ["like", like],
			"brand": ["like", like],
			"item_group": ["like", like],
			"description": ["like", like],
		}

	items = frappe.get_list(
		"Item",
		filters=filters,
		or_filters=or_filters,
		fields=["name", "item_code", "item_name", "image", "brand", "item_group", "description", "stock_uom"],
		order_by="modified desc",
		limit_start=(page - 1) * page_length,
		limit_page_length=page_length,
	)
	item_codes = [row.item_code for row in items]

	prices: dict[str, float] = {}
	if item_codes and frappe.has_permission("Item Price", "read"):
		for row in frappe.get_list(
			"Item Price",
			filters={"item_code": ["in", item_codes], "price_list": price_list, "selling": 1},
			fields=["item_code", "price_list_rate"],
			order_by="valid_from desc, modified desc",
			limit_page_length=page_length * 3,
		):
			prices.setdefault(row.item_code, flt(row.price_list_rate))

	stock: dict[str, float] = {code: 0 for code in item_codes}
	if item_codes and frappe.has_permission("Bin", "read"):
		bin_filters = {"item_code": ["in", item_codes]}
		if warehouse:
			bin_filters["warehouse"] = warehouse
		for row in frappe.get_list(
			"Bin",
			filters=bin_filters,
			fields=["item_code", "actual_qty"],
			limit_page_length=page_length * 20,
		):
			stock[row.item_code] = stock.get(row.item_code, 0) + flt(row.actual_qty)

	for item in items:
		item.rate = prices.get(item.item_code, 0)
		item.actual_qty = stock.get(item.item_code, 0)

	groups = []
	if frappe.has_permission("Item Group", "read"):
		groups = frappe.get_list(
			"Item Group", filters={"is_group": 0}, pluck="name", order_by="name", limit_page_length=100
		)

	warehouses = []
	if frappe.has_permission("Warehouse", "read"):
		warehouse_filters = {"disabled": 0, "is_group": 0}
		if company:
			warehouse_filters["company"] = company
		warehouses = frappe.get_list(
			"Warehouse", filters=warehouse_filters, pluck="name", order_by="name", limit_page_length=100
		)

	price_lists = []
	if frappe.has_permission("Price List", "read"):
		price_lists = frappe.get_list(
			"Price List", filters={"enabled": 1, "selling": 1}, pluck="name", order_by="name", limit_page_length=50
		)

	return {
		"items": items,
		"page": page,
		"has_more": len(items) == page_length,
		"company": company,
		"currency": frappe.get_cached_value("Company", company, "default_currency") if company else None,
		"price_list": price_list,
		"item_groups": groups,
		"warehouses": warehouses,
		"price_lists": price_lists,
		"navigation": get_navigation(),
		"can_create_customer": frappe.has_permission("Customer", "create"),
		"can_create_sales_order": frappe.has_permission("Sales Order", "create"),
	}


@frappe.whitelist()
def search_customers(txt: str = "", page_length: int = 20):
	_require_login()
	_require_permission("Customer")
	txt = (txt or "").strip()
	like = f"%{txt}%"
	return frappe.get_list(
		"Customer",
		filters={"disabled": 0},
		or_filters={"name": ["like", like], "customer_name": ["like", like], "mobile_no": ["like", like]},
		fields=["name", "customer_name", "mobile_no", "email_id", "customer_group", "territory"],
		order_by="customer_name",
		limit_page_length=min(max(cint(page_length), 1), 50),
	)


@frappe.whitelist()
def create_draft_sales_order(payload: str | dict):
	"""Create a standard draft Sales Order; browser-supplied rates are ignored."""
	_require_login()
	_require_permission("Sales Order", "create")
	data = json.loads(payload) if isinstance(payload, str) else payload
	if not isinstance(data, dict):
		frappe.throw(_("Invalid sales order request."))

	request_id = (data.get("request_id") or "").strip()
	if not request_id or len(request_id) > 80:
		frappe.throw(_("A valid request ID is required."))
	cache_key = f"my_store_ui:sales_order:{frappe.session.user}:{request_id}"
	existing = frappe.cache.get_value(cache_key)
	if existing and frappe.db.exists("Sales Order", existing):
		return {"name": existing, "route": f"/app/sales-order/{existing}", "duplicate": True}

	customer = (data.get("customer") or "").strip()
	company = (data.get("company") or _default_company() or "").strip()
	warehouse = (data.get("warehouse") or "").strip()
	price_list = (data.get("price_list") or _default_price_list() or "Standard Selling").strip()
	_validate_link("Customer", customer, {"disabled": 0})
	_validate_link("Company", company)
	_validate_link("Warehouse", warehouse, {"company": company, "disabled": 0, "is_group": 0})
	_validate_link("Price List", price_list, {"enabled": 1, "selling": 1})

	rows = data.get("items") or []
	if not isinstance(rows, list) or not rows:
		frappe.throw(_("Add at least one product to the cart."))
	if len(rows) > 100:
		frappe.throw(_("A sales order cannot contain more than 100 cart lines."))

	delivery_date = (frappe.utils.getdate(nowdate()) + timedelta(days=7)).isoformat()
	order = frappe.new_doc("Sales Order")
	order.customer = customer
	order.company = company
	order.selling_price_list = price_list
	order.set_warehouse = warehouse
	order.delivery_date = delivery_date

	seen: set[str] = set()
	for row in rows:
		item_code = str(row.get("item_code") or "").strip()
		qty = flt(row.get("qty"))
		if not item_code or item_code in seen:
			frappe.throw(_("Each product must appear once in the cart."))
		if qty <= 0:
			frappe.throw(_("Quantity for {0} must be greater than zero.").format(item_code))
		_validate_link("Item", item_code, {"disabled": 0, "is_sales_item": 1})
		seen.add(item_code)
		order.append("items", {"item_code": item_code, "qty": qty, "warehouse": warehouse, "delivery_date": delivery_date})

	# ERPNext fetches item defaults, rates, taxes and totals during insertion.
	order.insert()
	frappe.cache.set_value(cache_key, order.name, expires_in_sec=3600)
	return {"name": order.name, "route": f"/app/sales-order/{order.name}", "duplicate": False}


def get_navigation():
	sections = [
		("Sales", "#1463E6", [("Smart Sales", "/app/smart-sales", "Page", "smart-sales"), ("POS Awesome", "/app/posapp", "Page", "posapp"), ("Customers", "/app/customer", "Customer", None), ("Sales Orders", "/app/sales-order", "Sales Order", None), ("Sales Invoices", "/app/sales-invoice", "Sales Invoice", None)]),
		("Purchases", "#FF7A18", [("Buying", "/app/buying", None, None), ("Suppliers", "/app/supplier", "Supplier", None), ("Purchase Orders", "/app/purchase-order", "Purchase Order", None), ("Purchase Invoices", "/app/purchase-invoice", "Purchase Invoice", None)]),
		("Inventory", "#14A85A", [("Stock", "/app/stock", None, None), ("Items", "/app/item", "Item", None), ("Warehouses", "/app/warehouse", "Warehouse", None), ("Stock Entry", "/app/stock-entry", "Stock Entry", None)]),
		("Finance", "#7038D4", [("Accounting", "/app/accounting", None, None), ("Payments", "/app/payment-entry", "Payment Entry", None), ("Chart of Accounts", "/app/account/view/tree", "Account", None), ("Journal Entries", "/app/journal-entry", "Journal Entry", None)]),
		("Operations", "#149CC2", [("Assets", "/app/assets", None, None), ("Manufacturing", "/app/manufacturing", None, None), ("Projects", "/app/projects", None, None), ("Support", "/app/support", None, None)]),
		("CRM", "#DF2D88", [("CRM", "/app/crm", None, None), ("Leads", "/app/lead", "Lead", None), ("Opportunities", "/app/opportunity", "Opportunity", None), ("Contacts", "/app/contact", "Contact", None)]),
		("Reports", "#1239B8", [("Sales Analytics", "/app/query-report/Sales Analytics", "Report", "Sales Analytics"), ("Stock Balance", "/app/query-report/Stock Balance", "Report", "Stock Balance"), ("Accounts Receivable", "/app/query-report/Accounts Receivable", "Report", "Accounts Receivable")]),
		("Admin", "#7038D4", [("Users", "/app/user", "User", None), ("Role Permissions", "/app/permission-manager", "Page", "permission-manager"), ("System Settings", "/app/system-settings/System Settings", "System Settings", None)]),
	]
	result = []
	for label, color, links in sections:
		allowed = []
		for link_label, route, doctype, document in links:
			if doctype is None:
				allowed.append({"label": link_label, "route": route})
			elif doctype == "Page":
				if frappe.has_permission("Page", "read", doc=document):
					allowed.append({"label": link_label, "route": route})
			elif doctype == "Report":
				if frappe.has_permission("Report", "read", doc=document):
					allowed.append({"label": link_label, "route": route})
			elif frappe.has_permission(doctype, "read"):
				allowed.append({"label": link_label, "route": route})
		if allowed:
			result.append({"label": label, "color": color, "links": allowed})
	return result
