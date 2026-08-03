"""Server-owned Retail ERP route and navigation registry.

The browser never supplies a DocType or permission target.  Every supported
frontend path is resolved against this allowlist before navigation is allowed.
"""

from __future__ import annotations

import re
from urllib.parse import quote, unquote, urlsplit

import frappe

from my_store_ui.services.priority_registry import ENTITY_ROUTES, FORM_VARIANTS, REPORT_GROUPS, SPECIAL_ROUTES


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
	# Access Control reports effective permissions and edits User Permissions, so it
	# is gated exactly like the rest of /admin. Every endpoint behind it re-checks
	# System Manager server-side; this registration only stops the SPA's own route
	# guard from treating a real page as not-found.
	{"name": "access-control", "pattern": r"^/admin/access-control(?:/(?P<tab>access|restrictions|roles|profiles|email))?/?$", "module": "Admin", "feature_id": "retail.admin.access_control", "implemented": True, "roles": ("System Manager",)},
	# System Operations -- read-only health/readiness/backup, System Manager gated.
	{"name": "system-operations", "pattern": r"^/admin/system(?:/(?P<tab>health|backups|errors|scheduler|readiness))?/?$", "module": "Admin", "feature_id": "retail.admin.system_operations", "implemented": True, "roles": ("System Manager",)},
	# Data Management -- guided import/export of allowlisted DocTypes.
	{"name": "data-management", "pattern": r"^/admin/data(?:/(?P<tab>import|export|opening-stock|opening-balances|history))?/?$", "module": "Admin", "feature_id": "retail.admin.data_management", "implemented": True, "roles": ("System Manager",)},
	# Email & Notifications administration (status, templates, notifications).
	{"name": "email-admin", "pattern": r"^/admin/email(?:/(?P<tab>accounts|templates|notifications|status))?/?$", "module": "Admin", "feature_id": "retail.admin.email", "implemented": True, "roles": ("System Manager",)},
	# Printing & Branding landing + preview (Letter Head / Print Format CRUD is generated).
	{"name": "printing-admin", "pattern": r"^/admin/printing(?:/(?P<tab>letter-heads|templates|settings|preview))?/?$", "module": "Admin", "feature_id": "retail.admin.printing", "implemented": True, "roles": ("System Manager",)},
	# Launch readiness dashboard -- System Manager gated (truthful go-live checklist).
	{"name": "launch-readiness", "pattern": r"^/admin/readiness/?$", "module": "Admin", "feature_id": "retail.admin.readiness", "implemented": True, "roles": ("System Manager",)},
	# Scheduled reports -- any authenticated user with report access; create is gated server-side.
	{"name": "scheduled-reports", "pattern": r"^/reports/scheduled/?$", "module": "Reports", "feature_id": "retail.reports.scheduled", "implemented": True},
	# First-time setup wizard -- any authenticated user may reach it; the create
	# action is gated server-side. Steps are open-ended so the SPA owns them.
	{"name": "setup-wizard", "pattern": r"^/setup(?:/(?P<step>[a-z-]{1,40}))?/?$", "module": "Setup", "feature_id": "retail.setup", "implemented": True},
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
	{"name": "home", "label": "Home", "path": "/home", "accent": "blue", "icon": "home", "links": (
		{"label": "Dashboard", "path": "/home"}, {"label": "Sales", "path": "/sales"},
		{"label": "Purchases", "path": "/purchases"}, {"label": "Inventory", "path": "/inventory"},
		{"label": "Finance", "path": "/finance"}, {"label": "Reports", "path": "/reports"},
	)},
	{"name": "smart-sales", "label": "Smart Sales", "path": "/smart-sales", "accent": "blue", "icon": "cart", "any_read": ("Customer", "Item", "Sales Order"), "links": (
		{"label": "Open Smart Sales", "path": "/smart-sales", "any_read": ("Customer", "Item", "Sales Order")},
		{"label": "Customers", "path": "/sales/customers", "doctype": "Customer"},
		{"label": "Products", "path": "/inventory/products", "doctype": "Item"},
		{"label": "Sales Orders", "path": "/sales/orders", "doctype": "Sales Order"},
	)},
	{"name": "sales", "label": "Sales", "path": "/sales", "accent": "green", "icon": "sales", "any_read": ("Customer", "Quotation", "Sales Order", "Delivery Note", "Sales Invoice"), "links": (
		{"label": "Sales Dashboard", "path": "/sales", "any_read": ("Customer", "Quotation", "Sales Order", "Delivery Note", "Sales Invoice")},
		{"label": "Customers", "path": "/sales/customers", "doctype": "Customer"},
		# A Sales module master alongside Customers, and the source of every
		# customer's commission split -- kept high so it is reachable without
		# expanding the menu. Permission-gated by the doctype, so a user without
		# Retail Sales Team read never sees it.
		{"label": "Sales Teams", "path": "/sales/teams", "doctype": "Retail Sales Team"},
		{"label": "Quotations", "path": "/sales/quotations", "doctype": "Quotation"},
		{"label": "Sales Orders", "path": "/sales/orders", "doctype": "Sales Order"},
		{"label": "Delivery Notes", "path": "/sales/delivery-notes", "doctype": "Delivery Note"},
		{"label": "Sales Invoices", "path": "/sales/invoices", "doctype": "Sales Invoice"},
		{"label": "Payment Entries", "path": "/finance/payments", "doctype": "Payment Entry"},
		{"label": "Sales Funnel", "path": "/sales/funnel", "page": "sales-funnel"},
		{"label": "Sales Reports", "path": "/reports/sales", "report": "Sales Analytics"},
	)},
	{"name": "purchases", "label": "Purchases", "path": "/purchases", "accent": "purple", "icon": "bag", "any_read": ("Supplier", "Material Request", "Request for Quotation", "Supplier Quotation", "Purchase Order", "Purchase Receipt", "Purchase Invoice"), "links": (
		{"label": "Purchases Dashboard", "path": "/purchases", "any_read": ("Supplier", "Purchase Order", "Purchase Invoice")},
		{"label": "Suppliers", "path": "/purchases/suppliers", "doctype": "Supplier"},
		{"label": "Supplier Groups", "path": "/purchases/supplier-groups", "doctype": "Supplier Group"},
		{"label": "Material Requests", "path": "/purchases/material-requests", "doctype": "Material Request"},
		{"label": "Requests for Quotation", "path": "/purchases/requests-for-quotation", "doctype": "Request for Quotation"},
		{"label": "Supplier Quotations", "path": "/purchases/supplier-quotations", "doctype": "Supplier Quotation"},
		{"label": "Purchase Orders", "path": "/purchases/orders", "doctype": "Purchase Order"},
		{"label": "Purchase Receipts", "path": "/purchases/receipts", "doctype": "Purchase Receipt"},
		{"label": "Purchase Invoices", "path": "/purchases/invoices", "doctype": "Purchase Invoice"},
		{"label": "Purchase Reports", "path": "/reports/purchases", "report": "Purchase Register"},
	)},
	{"name": "inventory", "label": "Inventory", "path": "/inventory", "accent": "orange", "icon": "box", "any_read": ("Item", "Item Group", "Brand", "Warehouse", "Stock Entry"), "links": (
		{"label": "Inventory Dashboard", "path": "/inventory", "any_read": ("Item", "Warehouse", "Stock Entry")},
		{"label": "Products", "path": "/inventory/products", "doctype": "Item"}, {"label": "New Product", "path": "/inventory/products/new", "doctype": "Item", "permission": "create"},
		{"label": "Item Groups", "path": "/inventory/item-groups", "doctype": "Item Group"}, {"label": "Brands", "path": "/inventory/brands", "doctype": "Brand"},
		{"label": "Warehouses", "path": "/inventory/warehouses", "doctype": "Warehouse"}, {"label": "Item Prices", "path": "/inventory/item-prices", "doctype": "Item Price"},
		{"label": "Price Lists", "path": "/inventory/price-lists", "doctype": "Price List"}, {"label": "Units of Measure", "path": "/inventory/uoms", "doctype": "UOM"},
		{"label": "Stock Entries", "path": "/inventory/stock-entries", "doctype": "Stock Entry"}, {"label": "Stock Transfer", "path": "/inventory/transfers/new", "doctype": "Stock Entry", "permission": "create"},
		{"label": "Stock Receipt", "path": "/inventory/receipts/new", "doctype": "Stock Entry", "permission": "create"}, {"label": "Stock Issue", "path": "/inventory/issues/new", "doctype": "Stock Entry", "permission": "create"},
		{"label": "Stock Reconciliation", "path": "/inventory/reconciliations", "doctype": "Stock Reconciliation"}, {"label": "Serial Numbers", "path": "/inventory/serial-numbers", "doctype": "Serial No"},
		{"label": "Batch Numbers", "path": "/inventory/batches", "doctype": "Batch"}, {"label": "Reorder Alerts", "path": "/inventory/reorder-alerts", "report": "Stock Projected Qty"},
		{"label": "Warehouse Capacity", "path": "/inventory/warehouse-capacity", "page": "warehouse-capacity-summary"},
		{"label": "Stock Reports", "path": "/reports/inventory", "report": "Stock Balance"},
	)},
	{"name": "finance", "label": "Finance", "path": "/finance", "accent": "gold", "icon": "finance", "any_read": ("Payment Entry", "Journal Entry", "Account"), "links": (
		{"label": "Finance Dashboard", "path": "/finance"},
		{"label": "Chart of Accounts", "path": "/finance/chart-of-accounts", "doctype": "Account"},
		{"label": "Journal Entries", "path": "/finance/journal-entries", "doctype": "Journal Entry"}, {"label": "Payment Entries", "path": "/finance/payments", "doctype": "Payment Entry"},
		{"label": "Payment Requests", "path": "/finance/payment-requests", "doctype": "Payment Request"}, {"label": "Payment Reconciliation", "path": "/finance/payment-reconciliation", "doctype": "Payment Reconciliation"},
		{"label": "Bank Reconciliation", "path": "/finance/bank-reconciliation", "doctype": "Bank Reconciliation Tool"},
		{"label": "Bank Clearance", "path": "/finance/bank-clearance", "doctype": "Bank Clearance"},
		{"label": "Pegged Currencies", "path": "/finance/pegged-currencies", "doctype": "Pegged Currencies"},
		{"label": "Cost Centers", "path": "/finance/cost-centers", "doctype": "Cost Center"}, {"label": "Modes of Payment", "path": "/finance/modes-of-payment", "doctype": "Mode of Payment"},
		{"label": "Financial Reports", "path": "/reports/finance", "report": "General Ledger"},
	)},
	{"name": "operations", "label": "Operations", "path": "/operations", "accent": "turquoise", "icon": "settings", "any_read": ("Asset", "Work Order", "BOM", "Quality Inspection", "Project", "Issue"), "links": (
		{"label": "Operations Dashboard", "path": "/operations", "any_read": ("Project", "Asset", "Work Order", "Issue")},
		{"label": "Projects", "path": "/operations/projects", "doctype": "Project"}, {"label": "Tasks", "path": "/operations/tasks", "doctype": "Task"},
		{"label": "Assets", "path": "/operations/assets", "doctype": "Asset"}, {"label": "Asset Movements", "path": "/operations/asset-movements", "doctype": "Asset Movement"},
		{"label": "Quality Inspections", "path": "/operations/quality-inspections", "doctype": "Quality Inspection"}, {"label": "Support Issues", "path": "/operations/support/issues", "doctype": "Issue"},
		{"label": "Manufacturing", "path": "/operations/manufacturing", "doctype": "Work Order"}, {"label": "Bills of Materials", "path": "/operations/manufacturing/boms", "doctype": "BOM"},
		{"label": "Production Plans", "path": "/operations/manufacturing/production-plans", "doctype": "Production Plan"}, {"label": "Work Orders", "path": "/operations/manufacturing/work-orders", "doctype": "Work Order"},
		{"label": "Job Cards", "path": "/operations/manufacturing/job-cards", "doctype": "Job Card"}, {"label": "Operations", "path": "/operations/manufacturing/operations", "doctype": "Operation"},
		{"label": "Workstations", "path": "/operations/manufacturing/workstations", "doctype": "Workstation"}, {"label": "Subcontracting", "path": "/operations/subcontracting", "doctype": "Subcontracting Order"},
		{"label": "Departments", "path": "/operations/departments", "doctype": "Department"}, {"label": "Designations", "path": "/operations/designations", "doctype": "Designation"},
	)},
	{"name": "crm", "label": "CRM", "path": "/crm", "accent": "pink", "icon": "users", "any_read": ("Lead", "Opportunity", "Customer", "Contact"), "links": (
		{"label": "CRM Dashboard", "path": "/crm", "any_read": ("Lead", "Opportunity", "Customer", "Contact")},
		{"label": "Leads", "path": "/crm/leads", "doctype": "Lead"}, {"label": "Opportunities", "path": "/crm/opportunities", "doctype": "Opportunity"},
		{"label": "Customers", "path": "/crm/customers", "doctype": "Customer"}, {"label": "Contacts", "path": "/crm/contacts", "doctype": "Contact"},
		{"label": "Addresses", "path": "/crm/addresses", "doctype": "Address"}, {"label": "Campaigns", "path": "/crm/campaigns", "doctype": "Campaign"},
		{"label": "Appointments", "path": "/crm/appointments", "doctype": "Appointment"}, {"label": "Territories", "path": "/crm/territories", "doctype": "Territory"},
		{"label": "Customer Groups", "path": "/crm/customer-groups", "doctype": "Customer Group"}, {"label": "Sales People", "path": "/crm/sales-people", "doctype": "Sales Person"},
		{"label": "CRM Reports", "path": "/reports/crm", "report": "CRM Analytics"},
	)},
	{"name": "reports", "label": "Reports", "path": "/reports", "accent": "dark-blue", "icon": "chart", "links": (
		{"label": "Report Hub", "path": "/reports"}, {"label": "Sales Reports", "path": "/reports/sales", "report": "Sales Analytics"},
		{"label": "Purchase Reports", "path": "/reports/purchases", "report": "Purchase Register"}, {"label": "Inventory Reports", "path": "/reports/inventory", "report": "Stock Balance"},
		{"label": "Finance Reports", "path": "/reports/finance", "report": "General Ledger"}, {"label": "CRM Reports", "path": "/reports/crm", "report": "CRM Analytics"},
		{"label": "Operations Reports", "path": "/reports/operations", "report": "Project Summary"},
	)},
	{"name": "pos", "label": "POS", "path": "/pos", "accent": "green", "icon": "cart", "any_read": ("POS Profile",), "links": (
		{"label": "Point of Sale", "path": "/pos", "doctype": "POS Profile"},
		{"label": "Sales Invoices", "path": "/sales/invoices", "doctype": "Sales Invoice"},
	)},
	{"name": "admin", "label": "Admin", "path": "/admin", "accent": "purple", "icon": "shield", "roles": ("System Manager",), "links": (
		{"label": "Admin Dashboard", "path": "/admin", "roles": ("System Manager",)},
		{"label": "Users", "path": "/admin/users", "doctype": "User"}, {"label": "Roles", "path": "/admin/roles", "doctype": "Role"},
		{"label": "Role Permissions", "path": "/admin/permissions", "page": "permission-manager"}, {"label": "Companies", "path": "/admin/companies", "doctype": "Company"},
		{"label": "Warehouses", "path": "/admin/warehouses", "doctype": "Warehouse"}, {"label": "Price Lists", "path": "/admin/price-lists", "doctype": "Price List"},
		{"label": "Settings", "path": "/admin/settings", "doctype": "System Settings"}, {"label": "Integrations", "path": "/admin/integrations", "doctype": "Integration Request"},
		{"label": "Website", "path": "/admin/website", "doctype": "Website Settings"}, {"label": "Background Jobs", "path": "/admin/background-jobs", "roles": ("System Manager",)},
		{"label": "System Health", "path": "/admin/system-health", "roles": ("System Manager",)},
	)},
)


def _has_any_read(doctypes: tuple[str, ...]) -> bool:
	return any(frappe.has_permission(doctype, "read") for doctype in doctypes)


def _has_roles(roles: tuple[str, ...]) -> bool:
	return frappe.session.user == "Administrator" or bool(set(roles) & set(frappe.get_roles()))


def _link_is_permitted(link: dict) -> bool:
	if link.get("roles") and not _has_roles(link["roles"]):
		return False
	if link.get("any_read") and not _has_any_read(link["any_read"]):
		return False
	if link.get("doctype") and not frappe.has_permission(link["doctype"], link.get("permission", "read")):
		return False
	if link.get("page"):
		return bool(frappe.db.exists("Page", link["page"]) and frappe.has_permission("Page", "read", doc=link["page"]))
	if link.get("report"):
		return bool(frappe.db.exists("Report", link["report"]) and frappe.has_permission("Report", "read", doc=link["report"]))
	return True


def _public_navigation_link(link: dict) -> dict:
	path = link.get("path")
	implemented = bool(path)
	if not path and link.get("doctype"):
		from my_store_ui.universal.registry import ALL_GENERATED_DOCTYPES, get_feature
		if link["doctype"] in ALL_GENERATED_DOCTYPES:
			path = get_feature(frappe.scrub(link["doctype"]).replace("_", "-")).get("route")
			implemented = True
	if not path:
		path = f"/feature-unavailable?feature={quote(link['label'], safe='')}"
	return {"label": link["label"], "path": path, "implemented": implemented}


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
			# An optional group that did not participate yields None, and
			# unquote(None) raises -- a 500 on a perfectly valid URL. A group that
			# did not match is simply an absent parameter.
			params = {
				key: unquote(value)
				for key, value in match.groupdict().items()
				if value is not None
			}
			if any(not value or len(value) > 140 or "\x00" in value or "/" in value for value in params.values()):
				return None, {}
			return definition, params
	if relative in FORM_VARIANTS:
		spec = FORM_VARIANTS[relative]
		return {
			"name": "priority-variant-new", "module": spec["module"].title(),
			"feature_id": f"doctype.{frappe.scrub(spec['doctype'])}.create", "implemented": True,
			"doctype": spec["doctype"], "permission": "create", "component": "entity",
			"mode": "new", "base_path": spec["base_path"], "defaults": spec.get("defaults") or {},
		}, {}
	for base_path, spec in sorted(ENTITY_ROUTES.items(), key=lambda item: len(item[0]), reverse=True):
		if relative == base_path:
			permission = "read"
			mode = "tree" if spec.get("view") == "tree" else "list"
			params = {}
		elif relative == f"{base_path}/new":
			permission, mode, params = "create", "new", {}
		elif relative.startswith(f"{base_path}/"):
			remainder = relative[len(base_path) + 1:]
			if remainder.endswith("/edit"):
				permission, mode, encoded = "write", "edit", remainder[:-5]
			else:
				permission, mode, encoded = "read", "detail", remainder
			name = unquote(encoded)
			if not name or len(name) > 140 or "\x00" in name or "/" in name:
				return None, {}
			params = {"name": name}
		else:
			continue
		return {
			"name": f"priority-{frappe.scrub(spec['doctype'])}-{mode}", "module": spec["module"].title(),
			"feature_id": f"doctype.{frappe.scrub(spec['doctype'])}.{mode}", "implemented": True,
			"doctype": spec["doctype"], "permission": permission, "component": "tree" if mode == "tree" else "entity",
			"mode": mode, "base_path": base_path, "roles": spec.get("roles") or (),
			"classification": spec.get("classification", "generated_provisional"),
		}, params
	if relative in {f"/reports/{group}" for group in REPORT_GROUPS}:
		group = relative.rsplit("/", 1)[-1]
		return {"name": "priority-report-group", "module": "Reports", "feature_id": f"reports.{group}", "implemented": True, "component": "report_hub", "group": group}, {}
	if relative.startswith("/reports/view/"):
		report_name = unquote(relative[len("/reports/view/"):])
		if not report_name or report_name not in {name for names in REPORT_GROUPS.values() for name in names}:
			return None, {}
		return {"name": "priority-report-view", "module": "Reports", "feature_id": f"report.{frappe.scrub(report_name)}", "implemented": True, "component": "report", "report": report_name}, {"report": report_name}
	if relative in SPECIAL_ROUTES:
		spec = SPECIAL_ROUTES[relative]
		definition = {
			"name": f"priority-special-{frappe.scrub(spec['label'])}", "module": spec["module"].title(),
			"feature_id": f"special.{frappe.scrub(spec['label'])}", "implemented": True,
			"component": "tree" if spec.get("view") == "tree" else "special", "roles": spec.get("roles") or (),
			"classification": spec.get("classification", "specialised_provisional"), **spec,
		}
		return definition, {}
	generated = re.fullmatch(r"/generated/(?P<feature>[a-z0-9-]+)(?:/(?P<name>[^/]+))?(?:/(?P<edit>edit))?/?", relative)
	if generated:
		params = {key: unquote(value) for key, value in generated.groupdict().items() if value}
		if any(not value or len(value) > 140 or "\x00" in value or "/" in value for value in params.values()):
			return None, {}
		try:
			from my_store_ui.universal.registry import get_generated_feature
			record = get_generated_feature(params["feature"])
		except Exception:
			return None, {}
		is_new = params.get("name") == "new"
		permission = "create" if is_new else "write" if params.get("edit") else "read"
		return {"name": f"generated-{permission}", "module": record.get("module"), "feature_id": record["feature_id"], "implemented": True, "doctype": record["doctype"], "permission": permission}, params
	special = re.fullmatch(r"/(?P<kind>reports|views)/(?P<feature>[^/]+)(?:/(?P<view>[^/]+))?/?", relative)
	if special:
		params = {key: unquote(value) for key, value in special.groupdict().items() if value}
		try:
			from my_store_ui.universal.registry import feature_is_permitted, get_feature
			category = "report" if params["kind"] == "reports" else params.get("view", "page").lower()
			record = get_feature(f"{category}:{params['feature']}")
			if not feature_is_permitted(record):
				return None, {}
		except Exception:
			return None, {}
		# Special renderers remain explicitly provisional and never execute methods.
		return {"name": f"generated-{params['kind']}", "module": record.get("module"), "feature_id": record["feature_id"], "implemented": True}, params
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
	if definition.get("page") and not (frappe.db.exists("Page", definition["page"]) and frappe.has_permission("Page", "read", doc=definition["page"])):
		return False
	if definition.get("report") and not (frappe.db.exists("Report", definition["report"]) and frappe.has_permission("Report", "read", doc=definition["report"])):
		return False
	if definition.get("doctypes") and not _has_any_read(tuple(doctype for doctype in definition["doctypes"] if frappe.db.exists("DocType", doctype))):
		return False
	return True


def get_permitted_navigation() -> list[dict]:
	result = []
	for item in NAVIGATION:
		if item.get("roles") and not _has_roles(item["roles"]):
			continue
		if item.get("any_read") and not _has_any_read(item["any_read"]):
			continue
		links = [_public_navigation_link(link) for link in item.get("links", ()) if _link_is_permitted(link)]
		public = {key: value for key, value in item.items() if key not in {"roles", "any_read", "links"}}
		public["links"] = links
		result.append(public)
	return result


# Curated, permission-aware Quick Create ("+ Create") menu. Only doctypes that
# resolve to a REAL create route in the universal registry and for which the user
# holds create permission are offered — never a guessed URL or a dead action.
# A menu entry is either a plain DocType (create route taken from the registry) or
# a dict that overrides the label and/or pins a preset FORM_VARIANTS path.
QUICK_CREATE_GROUPS = (
	("Sales", (
		"Customer", "Quotation", "Sales Order", "Delivery Note", "Sales Invoice",
		{"doctype": "Payment Entry", "label": "Receive Payment", "path": "/finance/payments/receive/new"},
	)),
	("Purchasing", (
		"Supplier", "Material Request", "Request for Quotation", "Supplier Quotation",
		"Purchase Order", "Purchase Receipt", "Purchase Invoice",
		{"doctype": "Payment Entry", "label": "Pay Supplier", "path": "/finance/payments/pay/new"},
	)),
	("Inventory", (
		{"doctype": "Item", "label": "Product"}, "Stock Entry", "Stock Reconciliation", "Warehouse",
	)),
	("Administration", ("User", "Role", "Role Profile")),
	("More", (
		"Journal Entry", "Contact", "Address",
		{"doctype": "Payment Entry", "label": "Internal Transfer", "path": "/finance/payments/internal-transfer/new"},
	)),
)


@frappe.whitelist(methods=["GET"])
def get_quick_create_actions() -> dict:
	if frappe.session.user == "Guest":
		frappe.throw(frappe._("Authentication is required."), frappe.AuthenticationError)
	from my_store_ui.universal.registry import feature_is_permitted, get_registry_records

	by_doctype: dict[str, dict] = {}
	for record in get_registry_records():
		doctype = record.get("doctype")
		if doctype and record.get("create_route") and doctype not in by_doctype:
			by_doctype[doctype] = record

	groups = []
	for group_label, entries in QUICK_CREATE_GROUPS:
		items = []
		for entry in entries:
			spec = {"doctype": entry} if isinstance(entry, str) else dict(entry)
			doctype = spec["doctype"]
			record = by_doctype.get(doctype)
			if not record:
				continue
			# Registry-level role/permission gate AND an explicit create check.
			if not feature_is_permitted(record, "create") or not frappe.has_permission(doctype, "create"):
				continue
			path = spec.get("path") or record["create_route"]
			# Never offer an action whose route does not resolve or is not
			# permitted -- a dead menu entry is worse than a missing one.
			definition, _params = resolve_frontend_route(path)
			if not definition or not route_is_permitted(definition):
				continue
			items.append({
				"label": frappe._(spec.get("label") or doctype),
				"doctype": doctype,
				"path": path,
				"feature": record.get("route_key"),
				"group": group_label,
			})
		if items:
			groups.append({"group": group_label, "items": items})
	return {"groups": groups}
