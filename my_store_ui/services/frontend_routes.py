"""Server-owned Retail ERP route and navigation registry.

The browser never supplies a DocType or permission target.  Every supported
frontend path is resolved against this allowlist before navigation is allowed.
"""

from __future__ import annotations

import re
from urllib.parse import unquote, urlsplit

import frappe


BASE_PATH = "/retail-erp"


ROUTE_REGISTRY = (
	{"name": "home", "pattern": r"^/home/?$", "module": "Home", "feature_id": "retail.home", "implemented": True},
	{"name": "smart-sales", "pattern": r"^/smart-sales/?$", "module": "Sales", "feature_id": "retail.smart_sales", "implemented": True, "any_read": ("Customer", "Item", "Sales Order")},
	{"name": "sales", "pattern": r"^/sales/?$", "module": "Sales", "feature_id": "retail.sales", "implemented": True, "any_read": ("Customer", "Sales Order", "Delivery Note", "Sales Invoice")},
	{"name": "purchases", "pattern": r"^/purchases/?$", "module": "Purchases", "feature_id": "retail.purchases", "implemented": True, "any_read": ("Supplier", "Material Request", "Purchase Order", "Purchase Receipt", "Purchase Invoice")},
	{"name": "inventory", "pattern": r"^/inventory/?$", "module": "Inventory", "feature_id": "retail.inventory", "implemented": True, "any_read": ("Item", "Warehouse", "Stock Entry")},
	{"name": "finance", "pattern": r"^/finance/?$", "module": "Finance", "feature_id": "retail.finance", "implemented": True, "any_read": ("Payment Entry", "Journal Entry", "Account")},
	{"name": "operations", "pattern": r"^/operations/?$", "module": "Operations", "feature_id": "retail.operations", "implemented": True, "any_read": ("Asset", "Work Order", "Project", "Issue")},
	{"name": "crm", "pattern": r"^/crm/?$", "module": "CRM", "feature_id": "retail.crm", "implemented": True, "any_read": ("Lead", "Opportunity", "Customer")},
	{"name": "reports", "pattern": r"^/reports/?$", "module": "Reports", "feature_id": "retail.reports", "implemented": True},
	{"name": "admin", "pattern": r"^/admin/?$", "module": "Admin", "feature_id": "retail.admin", "implemented": True, "roles": ("System Manager",)},
	{"name": "feature-unavailable", "pattern": r"^/feature-unavailable/?$", "module": "System", "feature_id": "retail.feature_unavailable", "implemented": True},
	{"name": "permission-denied", "pattern": r"^/permission-denied/?$", "module": "System", "feature_id": "retail.permission_denied", "implemented": True},
	{"name": "not-found", "pattern": r"^/not-found/?$", "module": "System", "feature_id": "retail.not_found", "implemented": True},
	{"name": "customer-list", "pattern": r"^/sales/customers/?$", "module": "Sales", "feature_id": "doctype.customer.list", "implemented": True, "doctype": "Customer", "permission": "read"},
	{"name": "customer-new", "pattern": r"^/sales/customers/new/?$", "module": "Sales", "feature_id": "doctype.customer.create", "implemented": True, "doctype": "Customer", "permission": "create"},
	{"name": "customer-edit", "pattern": r"^/sales/customers/(?P<name>[^/]+)/edit/?$", "module": "Sales", "feature_id": "doctype.customer.edit", "implemented": True, "doctype": "Customer", "permission": "write"},
	{"name": "customer-detail", "pattern": r"^/sales/customers/(?P<name>[^/]+)/?$", "module": "Sales", "feature_id": "doctype.customer.detail", "implemented": True, "doctype": "Customer", "permission": "read"},
	{"name": "item-list", "pattern": r"^/inventory/products/?$", "module": "Inventory", "feature_id": "doctype.item.list", "implemented": True, "doctype": "Item", "permission": "read"},
	{"name": "item-new", "pattern": r"^/inventory/products/new/?$", "module": "Inventory", "feature_id": "doctype.item.create", "implemented": True, "doctype": "Item", "permission": "create"},
	{"name": "item-edit", "pattern": r"^/inventory/products/(?P<name>[^/]+)/edit/?$", "module": "Inventory", "feature_id": "doctype.item.edit", "implemented": True, "doctype": "Item", "permission": "write"},
	{"name": "item-detail", "pattern": r"^/inventory/products/(?P<name>[^/]+)/?$", "module": "Inventory", "feature_id": "doctype.item.detail", "implemented": True, "doctype": "Item", "permission": "read"},
	{"name": "sales-order-list", "pattern": r"^/sales/orders/?$", "module": "Sales", "feature_id": "doctype.sales_order.list", "implemented": True, "doctype": "Sales Order", "permission": "read"},
	{"name": "sales-order-new", "pattern": r"^/sales/orders/new/?$", "module": "Sales", "feature_id": "doctype.sales_order.create", "implemented": True, "doctype": "Sales Order", "permission": "create"},
	{"name": "sales-order-edit", "pattern": r"^/sales/orders/(?P<name>[^/]+)/edit/?$", "module": "Sales", "feature_id": "doctype.sales_order.edit", "implemented": True, "doctype": "Sales Order", "permission": "write"},
	{"name": "sales-order-detail", "pattern": r"^/sales/orders/(?P<name>[^/]+)/?$", "module": "Sales", "feature_id": "doctype.sales_order.detail", "implemented": True, "doctype": "Sales Order", "permission": "read"},
	{"name": "delivery-note-list", "pattern": r"^/sales/delivery-notes/?$", "module": "Sales", "feature_id": "doctype.delivery_note.list", "implemented": True, "doctype": "Delivery Note", "permission": "read"},
	{"name": "delivery-note-new", "pattern": r"^/sales/delivery-notes/new/?$", "module": "Sales", "feature_id": "doctype.delivery_note.create", "implemented": True, "doctype": "Delivery Note", "permission": "create"},
	{"name": "delivery-note-edit", "pattern": r"^/sales/delivery-notes/(?P<name>[^/]+)/edit/?$", "module": "Sales", "feature_id": "doctype.delivery_note.edit", "implemented": True, "doctype": "Delivery Note", "permission": "write"},
	{"name": "delivery-note-detail", "pattern": r"^/sales/delivery-notes/(?P<name>[^/]+)/?$", "module": "Sales", "feature_id": "doctype.delivery_note.detail", "implemented": True, "doctype": "Delivery Note", "permission": "read"},
	{"name": "sales-invoice-list", "pattern": r"^/sales/invoices/?$", "module": "Sales", "feature_id": "doctype.sales_invoice.list", "implemented": True, "doctype": "Sales Invoice", "permission": "read"},
	{"name": "sales-invoice-new", "pattern": r"^/sales/invoices/new/?$", "module": "Sales", "feature_id": "doctype.sales_invoice.create", "implemented": True, "doctype": "Sales Invoice", "permission": "create"},
	{"name": "sales-invoice-edit", "pattern": r"^/sales/invoices/(?P<name>[^/]+)/edit/?$", "module": "Sales", "feature_id": "doctype.sales_invoice.edit", "implemented": True, "doctype": "Sales Invoice", "permission": "write"},
	{"name": "sales-invoice-detail", "pattern": r"^/sales/invoices/(?P<name>[^/]+)/?$", "module": "Sales", "feature_id": "doctype.sales_invoice.detail", "implemented": True, "doctype": "Sales Invoice", "permission": "read"},
	{"name": "payment-entry-list", "pattern": r"^/finance/payments/?$", "module": "Finance", "feature_id": "doctype.payment_entry.list", "implemented": True, "doctype": "Payment Entry", "permission": "read"},
	{"name": "payment-entry-new", "pattern": r"^/finance/payments/new/?$", "module": "Finance", "feature_id": "doctype.payment_entry.create", "implemented": True, "doctype": "Payment Entry", "permission": "create"},
	{"name": "payment-entry-edit", "pattern": r"^/finance/payments/(?P<name>[^/]+)/edit/?$", "module": "Finance", "feature_id": "doctype.payment_entry.edit", "implemented": True, "doctype": "Payment Entry", "permission": "write"},
	{"name": "payment-entry-detail", "pattern": r"^/finance/payments/(?P<name>[^/]+)/?$", "module": "Finance", "feature_id": "doctype.payment_entry.detail", "implemented": True, "doctype": "Payment Entry", "permission": "read"},
)


NAVIGATION = (
	{"name": "home", "label": "Home", "path": "/home", "accent": "blue", "icon": "home"},
	{"name": "sales", "label": "Sales", "path": "/sales", "accent": "blue", "icon": "sales", "any_read": ("Customer", "Sales Order", "Delivery Note", "Sales Invoice")},
	{"name": "purchases", "label": "Purchases", "path": "/purchases", "accent": "orange", "icon": "bag", "any_read": ("Supplier", "Material Request", "Purchase Order", "Purchase Receipt", "Purchase Invoice")},
	{"name": "inventory", "label": "Inventory", "path": "/inventory", "accent": "green", "icon": "box", "any_read": ("Item", "Warehouse", "Stock Entry")},
	{"name": "finance", "label": "Finance", "path": "/finance", "accent": "purple", "icon": "finance", "any_read": ("Payment Entry", "Journal Entry", "Account")},
	{"name": "operations", "label": "Operations", "path": "/operations", "accent": "turquoise", "icon": "settings", "any_read": ("Asset", "Work Order", "Project", "Issue")},
	{"name": "crm", "label": "CRM", "path": "/crm", "accent": "pink", "icon": "users", "any_read": ("Lead", "Opportunity", "Customer")},
	{"name": "reports", "label": "Reports", "path": "/reports", "accent": "dark-blue", "icon": "chart"},
	{"name": "admin", "label": "Admin", "path": "/admin", "accent": "purple", "icon": "shield", "roles": ("System Manager",)},
)


def _has_any_read(doctypes: tuple[str, ...]) -> bool:
	return any(frappe.has_permission(doctype, "read") for doctype in doctypes)


def _has_roles(roles: tuple[str, ...]) -> bool:
	return frappe.session.user == "Administrator" or bool(set(roles) & set(frappe.get_roles()))


def _safe_relative_path(path: str) -> str:
	path = urlsplit(path or "").path
	if path.startswith(BASE_PATH):
		path = path[len(BASE_PATH):]
	if not path.startswith("/"):
		path = f"/{path}"
	if len(path) > 512 or "\x00" in path or any(part in {".", ".."} for part in path.split("/")):
		return "/not-found"
	return path


def resolve_frontend_route(path: str) -> tuple[dict | None, dict]:
	relative = _safe_relative_path(path)
	for definition in ROUTE_REGISTRY:
		if match := re.fullmatch(definition["pattern"], relative):
			params = {key: unquote(value) for key, value in match.groupdict().items()}
			if any(not value or len(value) > 140 or "\x00" in value or "/" in value for value in params.values()):
				return None, {}
			return definition, params
	return None, {}


def route_is_permitted(definition: dict) -> bool:
	if frappe.session.user == "Guest":
		return False
	if definition.get("roles") and not _has_roles(definition["roles"]):
		return False
	if definition.get("any_read") and not _has_any_read(definition["any_read"]):
		return False
	if definition.get("doctype") and not frappe.has_permission(definition["doctype"], definition.get("permission", "read")):
		return False
	return True


def get_permitted_navigation() -> list[dict]:
	result = []
	for item in NAVIGATION:
		if item.get("roles") and not _has_roles(item["roles"]):
			continue
		if item.get("any_read") and not _has_any_read(item["any_read"]):
			continue
		result.append({key: value for key, value in item.items() if key not in {"roles", "any_read"}})
	return result
