from __future__ import annotations

import json
from datetime import timedelta

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate

from my_store_ui.wholesale import idempotency
from my_store_ui.wholesale.uom import conversion_factor


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


def _customer_price_list(customer: str | None) -> str | None:
	"""The selling Price List that applies to a customer.

	Standard ERPNext resolution: the customer's own default_price_list, else the
	customer group's default. Returns None when the customer has no specific list
	(caller falls back to the site default).
	"""
	if not customer:
		return None
	try:
		from erpnext.accounts.party import get_default_price_list

		party = frappe.get_cached_doc("Customer", customer)
		resolved = get_default_price_list(party)
	except Exception:
		resolved = frappe.db.get_value("Customer", customer, "default_price_list")
	if resolved and frappe.db.exists("Price List", {"name": resolved, "enabled": 1, "selling": 1}):
		return resolved
	return None


def _available_to_sell(item_code: str, warehouse: str | None) -> dict:
	"""Actual / Reserved / Available-to-Sell for one item (+warehouse). Permission-safe."""
	actual = reserved = 0.0
	if frappe.has_permission("Bin", "read"):
		filters = {"item_code": item_code}
		if warehouse:
			filters["warehouse"] = warehouse
		for row in frappe.get_all("Bin", filters=filters, fields=["actual_qty", "reserved_stock"]):
			actual += flt(row.actual_qty)
			reserved += flt(row.reserved_stock)
	return {"actual_qty": actual, "reserved_qty": reserved, "available_to_sell": actual - reserved}


@frappe.whitelist()
def get_bootstrap(page: int = 1, page_length: int = 24, search: str = "", item_group: str = "", warehouse: str = "", price_list: str = "", customer: str = ""):
	"""Return a permission-filtered, paginated catalogue and selector options.

	When a customer is supplied the catalogue is priced against that customer's
	own selling Price List (their default_price_list / customer-group default),
	so different customers see different prices. Full Pricing-Rule resolution for
	a specific quantity is applied authoritatively by ``get_cart_pricing`` and by
	ERPNext on Sales Order insert.
	"""
	_require_login()
	_require_permission("Item")

	page = max(cint(page), 1)
	page_length = min(max(cint(page_length), 1), 48)
	company = _default_company()
	customer = (customer or "").strip()
	if customer:
		_validate_link("Customer", customer, {"disabled": 0})
	# Customer's price list wins over an explicitly passed one so switching
	# customer reprices; fall back to the passed list, then the site default.
	price_list = _customer_price_list(customer) or price_list or _default_price_list() or "Standard Selling"
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
		fields=[
			"name", "item_code", "item_name", "image", "brand", "item_group", "description",
			"stock_uom", "is_stock_item",
			# Reference only on the catalogue card: a wholesale customer may order
			# below a full carton, so this never gates the order.
			"custom_carton_qty as carton_qty",
		],
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

	# Actual / Reserved / Available-to-Sell / Projected per item.
	# Available to Sell = Actual - Reserved (standard Bin.reserved_stock, i.e.
	# stock reservation entries). Reserved is 0 while reservation is disabled.
	stock: dict[str, dict] = {code: {"actual": 0.0, "reserved": 0.0, "projected": 0.0} for code in item_codes}
	if item_codes and frappe.has_permission("Bin", "read"):
		bin_filters = {"item_code": ["in", item_codes]}
		if warehouse:
			bin_filters["warehouse"] = warehouse
		for row in frappe.get_list(
			"Bin",
			filters=bin_filters,
			fields=["item_code", "actual_qty", "reserved_stock", "projected_qty"],
			limit_page_length=page_length * 20,
		):
			entry = stock.setdefault(row.item_code, {"actual": 0.0, "reserved": 0.0, "projected": 0.0})
			entry["actual"] += flt(row.actual_qty)
			entry["reserved"] += flt(row.reserved_stock)
			entry["projected"] += flt(row.projected_qty)

	for item in items:
		item.rate = prices.get(item.item_code, 0)
		entry = stock.get(item.item_code, {"actual": 0.0, "reserved": 0.0, "projected": 0.0})
		item.actual_qty = entry["actual"]
		item.reserved_qty = entry["reserved"]
		item.available_to_sell = entry["actual"] - entry["reserved"]
		item.projected_qty = entry["projected"]

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
		"customer": customer or None,
		"customer_price_list": _customer_price_list(customer) if customer else None,
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


def _stock_status(available: float, qty: float, is_stock_item: bool) -> str:
	if not is_stock_item:
		return "not_stock_item"
	if available <= 0:
		return "out_of_stock"
	if qty and qty > available:
		return "insufficient"
	if available <= 5:
		return "low_stock"
	return "in_stock"


@frappe.whitelist()
def get_cart_pricing(customer: str, items: str | list, warehouse: str = "", price_list: str = "", company: str = ""):
	"""Authoritative per-line pricing + availability for the current customer.

	Uses ERPNext's own pricing engine (``get_item_details``) so customer-specific
	Item Prices and Pricing Rules are honoured — no pricing logic is duplicated in
	Vue. Returns, per line, the final rate, the base price-list rate, discount, the
	pricing source, and Actual/Reserved/Available with a stock status. This is what
	the frontend calls when the customer changes or a product is added, to reprice
	the whole cart and re-check stock.
	"""
	_require_login()
	_require_permission("Item")
	customer = (customer or "").strip()
	_validate_link("Customer", customer, {"disabled": 0})
	company = (company or _default_company() or "").strip()
	_validate_link("Company", company)
	warehouse = (warehouse or "").strip()
	if warehouse:
		_validate_link("Warehouse", warehouse, {"disabled": 0, "is_group": 0})
	price_list = _customer_price_list(customer) or price_list or _default_price_list() or "Standard Selling"
	_validate_link("Price List", price_list, {"enabled": 1, "selling": 1})

	rows = json.loads(items) if isinstance(items, str) else items
	if not isinstance(rows, list):
		frappe.throw(_("Invalid cart."))
	if len(rows) > 100:
		frappe.throw(_("A cart cannot contain more than 100 lines."))

	currency = frappe.get_cached_value("Company", company, "default_currency") if company else None
	from erpnext.stock.get_item_details import get_item_details

	out = []
	seen: set[str] = set()
	for row in rows:
		item_code = str((row or {}).get("item_code") or "").strip()
		if not item_code or item_code in seen:
			continue
		seen.add(item_code)
		if not frappe.db.exists("Item", {"name": item_code, "disabled": 0, "is_sales_item": 1}):
			continue
		if not frappe.has_permission("Item", "read", doc=item_code):
			continue
		qty = flt((row or {}).get("qty")) or 1
		item = frappe.get_cached_doc("Item", item_code)
		# Unit or Carton: the factor comes from the Item's own UOM table, never the browser.
		uom = str((row or {}).get("uom") or "").strip() or item.stock_uom
		factor = conversion_factor(item_code, uom)
		stock_qty = qty * factor
		args = {
			"item_code": item_code, "customer": customer, "company": company,
			"selling_price_list": price_list, "price_list": price_list,
			"currency": currency, "price_list_currency": currency,
			"plc_conversion_rate": 1.0, "conversion_rate": 1.0, "qty": qty,
			"uom": uom, "conversion_factor": factor, "stock_qty": stock_qty,
			"doctype": "Sales Order", "transaction_type": "selling",
			"warehouse": warehouse or None, "transaction_date": nowdate(),
		}
		price_list_rate = rate = discount = 0.0
		pricing_rule = None
		try:
			detail = get_item_details(args)
			price_list_rate = flt(detail.get("price_list_rate"))
			discount = flt(detail.get("discount_percentage"))
			discount_amount = flt(detail.get("discount_amount"))
			# get_item_details returns the discount separately and leaves `rate` for
			# the transaction to compute — derive the effective selling rate here.
			rate = flt(detail.get("rate"))
			if not rate:
				if discount_amount:
					rate = price_list_rate - discount_amount
				elif discount:
					rate = price_list_rate * (1 - discount / 100)
				else:
					rate = price_list_rate
			rules = detail.get("pricing_rules")
			if rules:
				parsed = json.loads(rules) if isinstance(rules, str) else rules
				if parsed:
					pricing_rule = parsed[0] if isinstance(parsed, list) else str(parsed)
			elif detail.get("has_pricing_rule"):
				pricing_rule = _("Pricing Rule")
		except Exception:
			frappe.log_error(title="Smart Sales cart pricing failed", message=frappe.get_traceback())
			price_list_rate = flt(frappe.db.get_value(
				"Item Price", {"item_code": item_code, "price_list": price_list, "selling": 1}, "price_list_rate"
			))
			rate = price_list_rate
		if pricing_rule:
			source = "pricing_rule"
		elif _customer_price_list(customer):
			source = "customer_price_list"
		elif price_list_rate:
			source = "price_list"
		else:
			source = "unpriced"
		stock = _available_to_sell(item_code, warehouse)
		available = stock["available_to_sell"]
		# Availability is held in stock units, so compare the converted quantity and
		# express the cap back in the UOM the user is actually entering.
		max_in_uom = (available / factor) if factor else available
		out.append({
			"item_code": item_code, "item_name": item.item_name, "stock_uom": item.stock_uom,
			"uom": uom, "conversion_factor": factor, "stock_qty": stock_qty,
			"qty": qty, "rate": rate, "price_list_rate": price_list_rate,
			"discount_percentage": discount, "currency": currency,
			"pricing_rule": pricing_rule, "source": source, "price_list": price_list,
			"actual_qty": stock["actual_qty"], "reserved_qty": stock["reserved_qty"],
			"available_to_sell": available, "max_qty": max_in_uom if item.is_stock_item else None,
			"stock_status": _stock_status(available, stock_qty, bool(item.is_stock_item)),
		})
	return {"customer": customer, "company": company, "warehouse": warehouse, "price_list": price_list, "currency": currency, "lines": out}


@frappe.whitelist()
def create_draft_sales_order(payload: str | dict):
	"""Create a standard draft Sales Order; browser-supplied rates are ignored."""
	_require_login()
	_require_permission("Sales Order", "create")
	data = json.loads(payload) if isinstance(payload, str) else payload
	if not isinstance(data, dict):
		frappe.throw(_("Invalid sales order request."))

	# Idempotency is database-backed: a lost cache key must never let a retried
	# request create a second order for the same click.
	request_id = idempotency.normalise(data.get("request_id"), required=True)
	existing = idempotency.find_existing("Sales Order", request_id)
	if existing:
		return {"name": existing, "route": f"/sales/orders/{existing}", "duplicate": True}

	customer = (data.get("customer") or "").strip()
	company = (data.get("company") or _default_company() or "").strip()
	warehouse = (data.get("warehouse") or "").strip()
	# The customer's Price Category wins, exactly as it does in get_cart_pricing --
	# otherwise the order would price against the site default and quote a different
	# rate from the one the cart just showed.
	price_list = (
		_customer_price_list(customer)
		or (data.get("price_list") or "").strip()
		or _default_price_list()
		or "Standard Selling"
	).strip()
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
	shortfalls: list[dict] = []
	for row in rows:
		item_code = str(row.get("item_code") or "").strip()
		qty = flt(row.get("qty"))
		if not item_code or item_code in seen:
			frappe.throw(_("Each product must appear once in the cart."))
		if qty <= 0:
			frappe.throw(_("Quantity for {0} must be greater than zero.").format(item_code))
		_validate_link("Item", item_code, {"disabled": 0, "is_sales_item": 1})
		seen.add(item_code)
		# Unit or Carton: resolve the factor from the Item, never from the browser, and
		# convert to stock units before any availability decision.
		stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
		uom = str(row.get("uom") or "").strip() or stock_uom
		factor = conversion_factor(item_code, uom)
		stock_qty = qty * factor
		# Server-side stock recheck: never trust the browser's availability. Stock
		# items may not be ordered beyond Available-to-Sell (Actual - Reserved).
		if frappe.db.get_value("Item", item_code, "is_stock_item"):
			available = _available_to_sell(item_code, warehouse)["available_to_sell"]
			if stock_qty > available:
				shortfalls.append({
					"item_code": item_code,
					"requested": stock_qty,
					"available": available,
					"stock_uom": stock_uom,
				})
		order.append("items", {
			"item_code": item_code, "qty": qty, "uom": uom, "conversion_factor": factor,
			"warehouse": warehouse, "delivery_date": delivery_date,
		})

	if shortfalls:
		lines = ", ".join(
			_("{0} (requested {1}, available {2})").format(s["item_code"], s["requested"], s["available"])
			for s in shortfalls
		)
		frappe.throw(
			_("Insufficient stock in {0}: {1}. Reduce the quantity and try again.").format(warehouse, lines),
			frappe.ValidationError,
		)

	# ERPNext fetches item defaults, rates, taxes and totals during insertion.
	idempotency.stamp(order, request_id)
	order.insert()
	idempotency.remember("Sales Order", request_id, order.name)
	return {"name": order.name, "route": f"/sales/orders/{order.name}", "duplicate": False}


def _linked_record_permitted(doctype: str, name: str | None) -> bool:
	"""Readable and present. A link to a record that is not installed is dropped."""
	if not name or not frappe.db.exists(doctype, name):
		return False
	try:
		return bool(frappe.has_permission(doctype, "read", doc=name))
	except frappe.DoesNotExistError:
		return False


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
			elif doctype in ("Page", "Report"):
				# These point at optional apps (POS Awesome, extra reports). A missing
				# record must drop the link, not raise -- has_permission(doc=...) throws
				# DoesNotExistError, which previously broke the whole bootstrap.
				if _linked_record_permitted(doctype, document):
					allowed.append({"label": link_label, "route": route})
			elif frappe.has_permission(doctype, "read"):
				allowed.append({"label": link_label, "route": route})
		if allowed:
			result.append({"label": label, "color": color, "links": allowed})
	return result
