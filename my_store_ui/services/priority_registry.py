"""Server-owned clean-route registry for priority Retail ERP coverage.

The values in this module are presentation and routing declarations only. They
never grant access: every resolver and API rechecks Frappe permissions.
"""

from __future__ import annotations

from collections import defaultdict


MODULES = {
	"home": {"label": "Home", "description": "Your permitted records, quick actions and recent activity.", "accent": "blue"},
	"sales": {"label": "Sales", "description": "Customers, quotations, orders, delivery and invoicing.", "accent": "blue"},
	"purchases": {"label": "Purchases", "description": "Suppliers, sourcing, ordering, receipts and supplier invoices.", "accent": "orange"},
	"inventory": {"label": "Inventory", "description": "Products, warehouses, stock movements and traceability.", "accent": "green"},
	"finance": {"label": "Finance", "description": "Accounting documents, payments, reconciliation and financial reports.", "accent": "purple"},
	"crm": {"label": "CRM", "description": "Leads, opportunities, contacts, campaigns and customer relationships.", "accent": "pink"},
	"operations": {"label": "Operations", "description": "Projects, assets, quality, support and manufacturing operations.", "accent": "turquoise"},
	"reports": {"label": "Reports", "description": "Permission-aware ERPNext operational and financial reports.", "accent": "dark-blue"},
	"admin": {"label": "Admin", "description": "Restricted users, permissions, setup and system monitoring.", "accent": "purple"},
}


# Clean path -> feature. Handcrafted paths are deliberately absent; the static
# route registry resolves them before consulting this table.
ENTITY_ROUTES = {
	# Sales
	"/sales/quotations": {"doctype": "Quotation", "module": "sales", "classification": "transaction_provisional"},
	# Purchases
	"/purchases/suppliers": {"doctype": "Supplier", "module": "purchases"},
	"/purchases/material-requests": {"doctype": "Material Request", "module": "purchases", "classification": "transaction_provisional"},
	"/purchases/requests-for-quotation": {"doctype": "Request for Quotation", "module": "purchases", "classification": "transaction_provisional"},
	"/purchases/supplier-quotations": {"doctype": "Supplier Quotation", "module": "purchases", "classification": "transaction_provisional"},
	"/purchases/orders": {"doctype": "Purchase Order", "module": "purchases", "classification": "transaction_provisional"},
	"/purchases/receipts": {"doctype": "Purchase Receipt", "module": "purchases", "classification": "transaction_provisional"},
	"/purchases/invoices": {"doctype": "Purchase Invoice", "module": "purchases", "classification": "transaction_provisional"},
	# Inventory
	"/inventory/item-groups": {"doctype": "Item Group", "module": "inventory", "view": "tree"},
	"/inventory/brands": {"doctype": "Brand", "module": "inventory"},
	"/inventory/warehouses": {"doctype": "Warehouse", "module": "inventory", "view": "tree"},
	"/inventory/item-prices": {"doctype": "Item Price", "module": "inventory"},
	"/inventory/price-lists": {"doctype": "Price List", "module": "inventory"},
	"/inventory/uoms": {"doctype": "UOM", "module": "inventory"},
	"/inventory/stock-entries": {"doctype": "Stock Entry", "module": "inventory", "classification": "transaction_provisional"},
	"/inventory/reconciliations": {"doctype": "Stock Reconciliation", "module": "inventory", "classification": "specialised_provisional"},
	"/inventory/serial-numbers": {"doctype": "Serial No", "module": "inventory"},
	"/inventory/batches": {"doctype": "Batch", "module": "inventory"},
	# Finance
	"/finance/chart-of-accounts": {"doctype": "Account", "module": "finance", "view": "tree"},
	"/finance/journal-entries": {"doctype": "Journal Entry", "module": "finance", "classification": "transaction_provisional"},
	"/finance/payment-requests": {"doctype": "Payment Request", "module": "finance", "classification": "transaction_provisional"},
	"/finance/cost-centers": {"doctype": "Cost Center", "module": "finance", "view": "tree"},
	"/finance/modes-of-payment": {"doctype": "Mode of Payment", "module": "finance"},
	# CRM
	"/crm/leads": {"doctype": "Lead", "module": "crm"},
	"/crm/opportunities": {"doctype": "Opportunity", "module": "crm"},
	"/crm/contacts": {"doctype": "Contact", "module": "crm"},
	"/crm/addresses": {"doctype": "Address", "module": "crm"},
	"/crm/campaigns": {"doctype": "Campaign", "module": "crm"},
	"/crm/appointments": {"doctype": "Appointment", "module": "crm"},
	"/crm/territories": {"doctype": "Territory", "module": "crm", "view": "tree"},
	"/crm/customer-groups": {"doctype": "Customer Group", "module": "crm", "view": "tree"},
	"/crm/sales-people": {"doctype": "Sales Person", "module": "crm", "view": "tree"},
	# Operations
	"/operations/projects": {"doctype": "Project", "module": "operations"},
	"/operations/tasks": {"doctype": "Task", "module": "operations", "classification": "specialised_provisional"},
	"/operations/assets": {"doctype": "Asset", "module": "operations"},
	"/operations/asset-movements": {"doctype": "Asset Movement", "module": "operations", "classification": "transaction_provisional"},
	"/operations/quality-inspections": {"doctype": "Quality Inspection", "module": "operations", "classification": "transaction_provisional"},
	"/operations/support/issues": {"doctype": "Issue", "module": "operations"},
	"/operations/departments": {"doctype": "Department", "module": "operations", "view": "tree"},
	"/operations/designations": {"doctype": "Designation", "module": "operations"},
	"/operations/manufacturing/boms": {"doctype": "BOM", "module": "operations", "classification": "specialised_provisional"},
	"/operations/manufacturing/production-plans": {"doctype": "Production Plan", "module": "operations", "classification": "specialised_provisional"},
	"/operations/manufacturing/work-orders": {"doctype": "Work Order", "module": "operations", "classification": "specialised_provisional"},
	"/operations/manufacturing/job-cards": {"doctype": "Job Card", "module": "operations", "classification": "specialised_provisional"},
	"/operations/manufacturing/operations": {"doctype": "Operation", "module": "operations"},
	"/operations/manufacturing/workstations": {"doctype": "Workstation", "module": "operations"},
	"/operations/subcontracting/orders": {"doctype": "Subcontracting Order", "module": "operations", "classification": "specialised_provisional"},
	"/operations/subcontracting/receipts": {"doctype": "Subcontracting Receipt", "module": "operations", "classification": "specialised_provisional"},
	# Restricted administration. System Manager checks are additionally applied.
	"/admin/users": {"doctype": "User", "module": "admin", "roles": ("System Manager",)},
	"/admin/roles": {"doctype": "Role", "module": "admin", "roles": ("System Manager",)},
	"/admin/companies": {"doctype": "Company", "module": "admin", "roles": ("System Manager",)},
	"/admin/warehouses": {"doctype": "Warehouse", "module": "admin", "roles": ("System Manager",), "view": "tree"},
	"/admin/price-lists": {"doctype": "Price List", "module": "admin", "roles": ("System Manager",)},
	"/purchases/supplier-groups": {"doctype": "Supplier Group", "module": "purchases", "view": "tree"},
}


FORM_VARIANTS = {
	"/inventory/transfers/new": {"doctype": "Stock Entry", "module": "inventory", "base_path": "/inventory/stock-entries", "defaults": {"stock_entry_type": "Material Transfer"}},
	"/inventory/receipts/new": {"doctype": "Stock Entry", "module": "inventory", "base_path": "/inventory/stock-entries", "defaults": {"stock_entry_type": "Material Receipt"}},
	"/inventory/issues/new": {"doctype": "Stock Entry", "module": "inventory", "base_path": "/inventory/stock-entries", "defaults": {"stock_entry_type": "Material Issue"}},
}


SPECIAL_ROUTES = {
	"/inventory/reorder-alerts": {"module": "inventory", "label": "Reorder Alerts", "report": "Stock Projected Qty", "classification": "report", "alias": "/reports/view/Stock%20Projected%20Qty"},
	"/finance/payment-reconciliation": {"module": "finance", "label": "Payment Reconciliation", "doctype": "Payment Reconciliation", "classification": "specialised_provisional"},
	"/finance/bank-reconciliation": {"module": "finance", "label": "Bank Reconciliation", "doctype": "Bank Reconciliation Tool", "classification": "specialised_provisional"},
	"/crm/customers": {"module": "crm", "label": "Customers", "alias": "/sales/customers", "doctype": "Customer"},
	"/operations/manufacturing": {"module": "operations", "label": "Manufacturing", "doctypes": ("BOM", "Production Plan", "Work Order", "Job Card")},
	"/operations/subcontracting": {"module": "operations", "label": "Subcontracting", "doctypes": ("Subcontracting Order", "Subcontracting Receipt")},
	"/pos": {"module": "sales", "label": "Point of Sale", "doctype": "POS Profile", "classification": "safe_integration"},
	"/admin/permissions": {"module": "admin", "label": "Role Permissions", "page": "permission-manager", "roles": ("System Manager",)},
	"/admin/settings": {"module": "admin", "label": "Settings", "doctypes": ("System Settings",), "roles": ("System Manager",), "classification": "read_only"},
	"/admin/integrations": {"module": "admin", "label": "Integrations", "doctypes": ("OAuth Client", "Connected App"), "roles": ("System Manager",)},
	"/admin/website": {"module": "admin", "label": "Website", "doctypes": ("Website Settings", "Web Page"), "roles": ("System Manager",)},
	"/admin/system-health": {"module": "admin", "label": "System Health", "roles": ("System Manager",), "classification": "read_only"},
	"/admin/background-jobs": {"module": "admin", "label": "Background Jobs", "roles": ("System Manager",), "classification": "read_only"},
}


REPORT_GROUPS = {
	"sales": ("Sales Register", "Sales Order Analysis", "Customer Ledger Summary", "Item-wise Sales Register", "Sales Analytics"),
	"purchases": ("Purchase Register", "Purchase Order Analysis", "Supplier Ledger Summary", "Item-wise Purchase Register"),
	"inventory": ("Stock Balance", "Stock Ledger", "Stock Analytics", "Stock Projected Qty"),
	"finance": ("Accounts Receivable", "Accounts Payable", "General Ledger", "Trial Balance", "Profit and Loss Statement", "Balance Sheet", "Cash Flow", "Bank Reconciliation Statement"),
	"crm": ("CRM Analytics", "Lead Details", "Opportunity Summary by Sales Stage"),
	"operations": ("Project Summary", "Work Order Summary", "Asset Depreciation Ledger"),
}


REPORT_FILTERS = {
	"Sales Register": ("company", "from_date", "to_date", "customer"),
	"Sales Order Analysis": ("company", "from_date", "to_date", "customer"),
	"Customer Ledger Summary": ("company", "from_date", "to_date", "customer"),
	"Item-wise Sales Register": ("company", "from_date", "to_date", "item_code"),
	"Sales Analytics": ("company", "from_date", "to_date"),
	"Purchase Register": ("company", "from_date", "to_date", "supplier"),
	"Purchase Order Analysis": ("company", "from_date", "to_date", "supplier"),
	"Supplier Ledger Summary": ("company", "from_date", "to_date", "supplier"),
	"Item-wise Purchase Register": ("company", "from_date", "to_date", "item_code"),
	"Stock Balance": ("company", "from_date", "to_date", "warehouse", "item_group", "item_code"),
	"Stock Ledger": ("company", "from_date", "to_date", "warehouse", "item_code"),
	"Stock Analytics": ("company", "from_date", "to_date", "warehouse"),
	"Stock Projected Qty": ("company", "warehouse", "item_group", "item_code"),
	"Accounts Receivable": ("company", "posting_date", "party", "ageing_based_on"),
	"Accounts Payable": ("company", "posting_date", "party", "ageing_based_on"),
	"General Ledger": ("company", "from_date", "to_date", "account", "party_type", "party"),
	"Trial Balance": ("company", "fiscal_year", "period_start_date", "period_end_date"),
	"Profit and Loss Statement": ("company", "from_fiscal_year", "to_fiscal_year", "periodicity"),
	"Balance Sheet": ("company", "from_fiscal_year", "to_fiscal_year", "periodicity"),
	"Cash Flow": ("company", "from_fiscal_year", "to_fiscal_year", "periodicity"),
	"Bank Reconciliation Statement": ("company", "bank_account", "from_date", "to_date"),
}


ALL_PRIORITY_DOCTYPES = frozenset(
	{spec["doctype"] for spec in ENTITY_ROUTES.values()}
	| {spec["doctype"] for spec in FORM_VARIANTS.values()}
	| {spec["doctype"] for spec in SPECIAL_ROUTES.values() if spec.get("doctype")}
)

CANONICAL_ROUTE_BY_DOCTYPE = {}
for _path, _spec in ENTITY_ROUTES.items():
	CANONICAL_ROUTE_BY_DOCTYPE.setdefault(_spec["doctype"], _path)


def routes_by_module() -> dict[str, list[tuple[str, dict]]]:
	result = defaultdict(list)
	for path, spec in ENTITY_ROUTES.items():
		result[spec["module"]].append((path, spec))
	for path, spec in SPECIAL_ROUTES.items():
		result[spec["module"]].append((path, spec))
	return dict(result)
