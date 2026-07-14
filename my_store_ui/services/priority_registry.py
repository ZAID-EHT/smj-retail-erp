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


# --- Generated in-scope DocType routes (Full Feature Parity, batch: masters) ---
# Curated standard parent DocTypes served read/write by the universal metadata
# engine with standard Frappe permissions. Ledger/system tables, single
# Settings/Tools and the POS family are intentionally excluded. Status is
# generated_provisional until behavioural verification exists.
_GENERATED_ENTITY_ROUTES = {
	"/crm/address-template": {"doctype": "Address Template", "module": "crm", "classification": "generated_provisional"},
	"/crm/competitor": {"doctype": "Competitor", "module": "crm", "classification": "generated_provisional"},
	"/crm/contract": {"doctype": "Contract", "module": "crm", "classification": "generated_provisional"},
	"/crm/contract-template": {"doctype": "Contract Template", "module": "crm", "classification": "generated_provisional"},
	"/crm/email-campaign": {"doctype": "Email Campaign", "module": "crm", "classification": "generated_provisional"},
	"/crm/gender": {"doctype": "Gender", "module": "crm", "classification": "generated_provisional"},
	"/crm/lead-source": {"doctype": "Lead Source", "module": "crm", "classification": "generated_provisional"},
	"/crm/market-segment": {"doctype": "Market Segment", "module": "crm", "classification": "generated_provisional"},
	"/crm/opportunity-lost-reason": {"doctype": "Opportunity Lost Reason", "module": "crm", "classification": "generated_provisional"},
	"/crm/opportunity-type": {"doctype": "Opportunity Type", "module": "crm", "classification": "generated_provisional"},
	"/crm/prospect": {"doctype": "Prospect", "module": "crm", "classification": "generated_provisional"},
	"/crm/sales-stage": {"doctype": "Sales Stage", "module": "crm", "classification": "generated_provisional"},
	"/crm/salutation": {"doctype": "Salutation", "module": "crm", "classification": "generated_provisional"},
	"/finance/accounting-dimension": {"doctype": "Accounting Dimension", "module": "finance", "classification": "generated_provisional"},
	"/finance/accounting-dimension-filter": {"doctype": "Accounting Dimension Filter", "module": "finance", "classification": "generated_provisional"},
	"/finance/accounting-period": {"doctype": "Accounting Period", "module": "finance", "classification": "generated_provisional"},
	"/finance/bank": {"doctype": "Bank", "module": "finance", "classification": "generated_provisional"},
	"/finance/bank-account": {"doctype": "Bank Account", "module": "finance", "classification": "generated_provisional"},
	"/finance/bank-account-subtype": {"doctype": "Bank Account Subtype", "module": "finance", "classification": "generated_provisional"},
	"/finance/bank-account-type": {"doctype": "Bank Account Type", "module": "finance", "classification": "generated_provisional"},
	"/finance/bank-guarantee": {"doctype": "Bank Guarantee", "module": "finance", "classification": "generated_provisional"},
	"/finance/bank-statement-import": {"doctype": "Bank Statement Import", "module": "finance", "classification": "generated_provisional"},
	"/finance/bank-transaction": {"doctype": "Bank Transaction", "module": "finance", "classification": "generated_provisional"},
	"/finance/budget": {"doctype": "Budget", "module": "finance", "classification": "generated_provisional"},
	"/finance/cheque-print-template": {"doctype": "Cheque Print Template", "module": "finance", "classification": "generated_provisional"},
	"/finance/cost-center-allocation": {"doctype": "Cost Center Allocation", "module": "finance", "classification": "generated_provisional"},
	"/finance/coupon-code": {"doctype": "Coupon Code", "module": "finance", "classification": "generated_provisional"},
	"/finance/dunning": {"doctype": "Dunning", "module": "finance", "classification": "generated_provisional"},
	"/finance/dunning-type": {"doctype": "Dunning Type", "module": "finance", "classification": "generated_provisional"},
	"/finance/exchange-rate-revaluation": {"doctype": "Exchange Rate Revaluation", "module": "finance", "classification": "generated_provisional"},
	"/finance/finance-book": {"doctype": "Finance Book", "module": "finance", "classification": "generated_provisional"},
	"/finance/fiscal-year": {"doctype": "Fiscal Year", "module": "finance", "classification": "generated_provisional"},
	"/finance/invoice-discounting": {"doctype": "Invoice Discounting", "module": "finance", "classification": "generated_provisional"},
	"/finance/item-tax-template": {"doctype": "Item Tax Template", "module": "finance", "classification": "generated_provisional"},
	"/finance/journal-entry-template": {"doctype": "Journal Entry Template", "module": "finance", "classification": "generated_provisional"},
	"/finance/loyalty-program": {"doctype": "Loyalty Program", "module": "finance", "classification": "generated_provisional"},
	"/finance/monthly-distribution": {"doctype": "Monthly Distribution", "module": "finance", "classification": "generated_provisional"},
	"/finance/party-link": {"doctype": "Party Link", "module": "finance", "classification": "generated_provisional"},
	"/finance/payment-gateway-account": {"doctype": "Payment Gateway Account", "module": "finance", "classification": "generated_provisional"},
	"/finance/payment-order": {"doctype": "Payment Order", "module": "finance", "classification": "generated_provisional"},
	"/finance/payment-term": {"doctype": "Payment Term", "module": "finance", "classification": "generated_provisional"},
	"/finance/payment-terms-template": {"doctype": "Payment Terms Template", "module": "finance", "classification": "generated_provisional"},
	"/finance/period-closing-voucher": {"doctype": "Period Closing Voucher", "module": "finance", "classification": "generated_provisional"},
	"/finance/pricing-rule": {"doctype": "Pricing Rule", "module": "finance", "classification": "generated_provisional"},
	"/finance/promotional-scheme": {"doctype": "Promotional Scheme", "module": "finance", "classification": "generated_provisional"},
	"/finance/purchase-taxes-and-charges-template": {"doctype": "Purchase Taxes and Charges Template", "module": "finance", "classification": "generated_provisional"},
	"/finance/sales-taxes-and-charges-template": {"doctype": "Sales Taxes and Charges Template", "module": "finance", "classification": "generated_provisional"},
	"/finance/share-transfer": {"doctype": "Share Transfer", "module": "finance", "classification": "generated_provisional"},
	"/finance/share-type": {"doctype": "Share Type", "module": "finance", "classification": "generated_provisional"},
	"/finance/shareholder": {"doctype": "Shareholder", "module": "finance", "classification": "generated_provisional"},
	"/finance/shipping-rule": {"doctype": "Shipping Rule", "module": "finance", "classification": "generated_provisional"},
	"/finance/subscription": {"doctype": "Subscription", "module": "finance", "classification": "generated_provisional"},
	"/finance/subscription-plan": {"doctype": "Subscription Plan", "module": "finance", "classification": "generated_provisional"},
	"/finance/tax-category": {"doctype": "Tax Category", "module": "finance", "classification": "generated_provisional"},
	"/finance/tax-rule": {"doctype": "Tax Rule", "module": "finance", "classification": "generated_provisional"},
	"/finance/tax-withholding-category": {"doctype": "Tax Withholding Category", "module": "finance", "classification": "generated_provisional"},
	"/inventory/customs-tariff-number": {"doctype": "Customs Tariff Number", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/delivery-trip": {"doctype": "Delivery Trip", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/inventory-dimension": {"doctype": "Inventory Dimension", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/item-alternative": {"doctype": "Item Alternative", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/item-attribute": {"doctype": "Item Attribute", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/item-manufacturer": {"doctype": "Item Manufacturer", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/landed-cost-voucher": {"doctype": "Landed Cost Voucher", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/manufacturer": {"doctype": "Manufacturer", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/packing-slip": {"doctype": "Packing Slip", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/pick-list": {"doctype": "Pick List", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/putaway-rule": {"doctype": "Putaway Rule", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/quality-inspection-parameter": {"doctype": "Quality Inspection Parameter", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/quality-inspection-parameter-group": {"doctype": "Quality Inspection Parameter Group", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/quality-inspection-template": {"doctype": "Quality Inspection Template", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/shipment": {"doctype": "Shipment", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/shipment-parcel-template": {"doctype": "Shipment Parcel Template", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/stock-entry-type": {"doctype": "Stock Entry Type", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/stock-reservation-entry": {"doctype": "Stock Reservation Entry", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/uom-category": {"doctype": "UOM Category", "module": "inventory", "classification": "generated_provisional"},
	"/inventory/warehouse-type": {"doctype": "Warehouse Type", "module": "inventory", "classification": "generated_provisional"},
	"/operations/activity-cost": {"doctype": "Activity Cost", "module": "operations", "classification": "generated_provisional"},
	"/operations/activity-type": {"doctype": "Activity Type", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-activity": {"doctype": "Asset Activity", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-capitalization": {"doctype": "Asset Capitalization", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-category": {"doctype": "Asset Category", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-maintenance": {"doctype": "Asset Maintenance", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-maintenance-log": {"doctype": "Asset Maintenance Log", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-maintenance-team": {"doctype": "Asset Maintenance Team", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-repair": {"doctype": "Asset Repair", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-shift-allocation": {"doctype": "Asset Shift Allocation", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-shift-factor": {"doctype": "Asset Shift Factor", "module": "operations", "classification": "generated_provisional"},
	"/operations/asset-value-adjustment": {"doctype": "Asset Value Adjustment", "module": "operations", "classification": "generated_provisional"},
	"/operations/issue-priority": {"doctype": "Issue Priority", "module": "operations", "classification": "generated_provisional"},
	"/operations/issue-type": {"doctype": "Issue Type", "module": "operations", "classification": "generated_provisional"},
	"/operations/location": {"doctype": "Location", "module": "operations", "classification": "generated_provisional", "view": "tree"},
	"/operations/non-conformance": {"doctype": "Non Conformance", "module": "operations", "classification": "generated_provisional"},
	"/operations/project-template": {"doctype": "Project Template", "module": "operations", "classification": "generated_provisional"},
	"/operations/project-type": {"doctype": "Project Type", "module": "operations", "classification": "generated_provisional"},
	"/operations/project-update": {"doctype": "Project Update", "module": "operations", "classification": "generated_provisional"},
	"/operations/quality-action": {"doctype": "Quality Action", "module": "operations", "classification": "generated_provisional"},
	"/operations/quality-feedback": {"doctype": "Quality Feedback", "module": "operations", "classification": "generated_provisional"},
	"/operations/quality-feedback-template": {"doctype": "Quality Feedback Template", "module": "operations", "classification": "generated_provisional"},
	"/operations/quality-goal": {"doctype": "Quality Goal", "module": "operations", "classification": "generated_provisional"},
	"/operations/quality-meeting": {"doctype": "Quality Meeting", "module": "operations", "classification": "generated_provisional"},
	"/operations/quality-procedure": {"doctype": "Quality Procedure", "module": "operations", "classification": "generated_provisional", "view": "tree"},
	"/operations/quality-review": {"doctype": "Quality Review", "module": "operations", "classification": "generated_provisional"},
	"/operations/service-level-agreement": {"doctype": "Service Level Agreement", "module": "operations", "classification": "generated_provisional"},
	"/operations/task-type": {"doctype": "Task Type", "module": "operations", "classification": "generated_provisional"},
	"/operations/timesheet": {"doctype": "Timesheet", "module": "operations", "classification": "generated_provisional"},
	"/operations/warranty-claim": {"doctype": "Warranty Claim", "module": "operations", "classification": "generated_provisional"},
	"/purchases/supplier-scorecard": {"doctype": "Supplier Scorecard", "module": "purchases", "classification": "generated_provisional"},
	"/purchases/supplier-scorecard-criteria": {"doctype": "Supplier Scorecard Criteria", "module": "purchases", "classification": "generated_provisional"},
	"/purchases/supplier-scorecard-period": {"doctype": "Supplier Scorecard Period", "module": "purchases", "classification": "generated_provisional"},
	"/purchases/supplier-scorecard-standing": {"doctype": "Supplier Scorecard Standing", "module": "purchases", "classification": "generated_provisional"},
	"/purchases/supplier-scorecard-variable": {"doctype": "Supplier Scorecard Variable", "module": "purchases", "classification": "generated_provisional"},
	"/sales/industry-type": {"doctype": "Industry Type", "module": "sales", "classification": "generated_provisional"},
	"/sales/installation-note": {"doctype": "Installation Note", "module": "sales", "classification": "generated_provisional"},
	"/sales/party-specific-item": {"doctype": "Party Specific Item", "module": "sales", "classification": "generated_provisional"},
	"/sales/product-bundle": {"doctype": "Product Bundle", "module": "sales", "classification": "generated_provisional"},
	"/sales/sales-partner-type": {"doctype": "Sales Partner Type", "module": "sales", "classification": "generated_provisional"},
}
ENTITY_ROUTES.update(_GENERATED_ENTITY_ROUTES)


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
