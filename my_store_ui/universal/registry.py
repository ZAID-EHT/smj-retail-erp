"""Server-owned feature registry derived from the complete site inventory."""

from __future__ import annotations

import json
from pathlib import Path

import frappe
from frappe.utils import cint

from my_store_ui.services.priority_registry import ALL_PRIORITY_DOCTYPES, CANONICAL_ROUTE_BY_DOCTYPE


CUSTOM_OVERRIDES = {
	"Customer": "/sales/customers",
	"Item": "/inventory/products",
	"Sales Order": "/sales/orders",
	"Delivery Note": "/sales/delivery-notes",
	"Sales Invoice": "/sales/invoices",
	"Payment Entry": "/finance/payments",
}

GENERATED_ALLOWLIST = {
	"Supplier", "Warehouse", "Lead", "Opportunity", "Project", "Asset", "Address", "Contact",
	"Territory", "Customer Group", "Supplier Group", "Item Group", "Brand", "UOM", "Sales Person",
	"Price List", "Mode of Payment", "Cost Center", "Department", "Designation",
}

ALL_GENERATED_DOCTYPES = frozenset(GENERATED_ALLOWLIST | ALL_PRIORITY_DOCTYPES)

# These account-security records remain restricted even through the legacy
# /generated compatibility aliases.  The DocType permission check below is
# still mandatory; this is an additional administration boundary.
ADMIN_FEATURE_ROLES = {
	"User": {"System Manager"},
	"Role": {"System Manager"},
}

MODULE_PRESENTATION = {
	"Buying": "orange", "Stock": "green", "CRM": "pink", "Projects": "turquoise",
	"Assets": "purple", "Setup": "blue", "Selling": "blue", "Accounts": "purple",
}

# Presentation overrides contain no permissions or business rules.  Missing
# values are inferred from installed metadata by the universal API.
PRESENTATION_OVERRIDES = {
	"Supplier": {"plural": "Suppliers", "description": "Manage supplier identities, groups, payment defaults and purchasing details.", "primary_fields": ["supplier_name", "supplier_group", "supplier_type"], "default_columns": ["name", "supplier_name", "supplier_group", "supplier_type", "country", "disabled", "modified"], "main_filters": ["supplier_group", "supplier_type", "country", "disabled"]},
	"Warehouse": {"plural": "Warehouses", "description": "Browse and maintain the warehouses available to permitted companies.", "primary_fields": ["warehouse_name", "company", "parent_warehouse"], "default_columns": ["name", "warehouse_name", "company", "parent_warehouse", "is_group", "disabled", "modified"], "main_filters": ["company", "parent_warehouse", "is_group", "disabled"]},
	"Lead": {"plural": "Leads", "description": "Track prospective customers and their current CRM status.", "primary_fields": ["lead_name", "company_name", "status", "source"], "default_columns": ["name", "lead_name", "company_name", "status", "source", "email_id", "mobile_no", "modified"], "main_filters": ["status", "source", "territory", "industry"]},
	"Opportunity": {"plural": "Opportunities", "description": "Review qualified sales opportunities, parties, values and expected closing dates.", "primary_fields": ["opportunity_from", "party_name", "status", "opportunity_type"], "default_columns": ["name", "opportunity_from", "party_name", "status", "opportunity_amount", "currency", "expected_closing", "modified"], "main_filters": ["status", "opportunity_type", "opportunity_from", "company"]},
	"Project": {"plural": "Projects", "description": "Manage permitted projects, progress, customers and expected dates.", "primary_fields": ["project_name", "status", "project_type", "customer"], "default_columns": ["name", "project_name", "status", "customer", "percent_complete", "expected_start_date", "expected_end_date", "modified"], "main_filters": ["status", "project_type", "customer", "company"]},
	"Asset": {"plural": "Assets", "description": "Review fixed assets, categories, locations and operational status.", "primary_fields": ["asset_name", "item_code", "asset_category", "company"], "default_columns": ["name", "asset_name", "item_code", "asset_category", "status", "location", "company", "modified"], "main_filters": ["status", "asset_category", "location", "company"]},
	"Address": {"plural": "Addresses", "description": "Maintain postal and business addresses linked to permitted records.", "primary_fields": ["address_title", "address_type", "city", "country"], "default_columns": ["name", "address_title", "address_type", "city", "state", "country", "disabled", "modified"], "main_filters": ["address_type", "city", "state", "country", "disabled"]},
	"Contact": {"plural": "Contacts", "description": "Manage people, email addresses, phone numbers and linked organisations.", "primary_fields": ["first_name", "last_name", "company_name", "status"], "default_columns": ["name", "first_name", "last_name", "company_name", "email_id", "mobile_no", "status", "modified"], "main_filters": ["status", "gender", "designation", "department"]},
	"Territory": {"plural": "Territories", "description": "Organise sales territories in the permitted hierarchy.", "primary_fields": ["territory_name", "parent_territory", "is_group"], "default_columns": ["name", "territory_name", "parent_territory", "is_group", "modified"], "main_filters": ["parent_territory", "is_group"]},
	"Customer Group": {"plural": "Customer Groups", "description": "Maintain the hierarchy used to classify customers.", "primary_fields": ["customer_group_name", "parent_customer_group", "is_group"], "default_columns": ["name", "customer_group_name", "parent_customer_group", "is_group", "default_price_list", "modified"], "main_filters": ["parent_customer_group", "is_group", "default_price_list"]},
	"Supplier Group": {"plural": "Supplier Groups", "description": "Maintain the hierarchy used to classify suppliers.", "primary_fields": ["supplier_group_name", "parent_supplier_group", "is_group"], "default_columns": ["name", "supplier_group_name", "parent_supplier_group", "is_group", "modified"], "main_filters": ["parent_supplier_group", "is_group"]},
	"Item Group": {"plural": "Item Groups", "description": "Organise items into the permitted product hierarchy.", "primary_fields": ["item_group_name", "parent_item_group", "is_group"], "default_columns": ["name", "item_group_name", "parent_item_group", "is_group", "modified"], "main_filters": ["parent_item_group", "is_group"]},
	"Brand": {"plural": "Brands", "description": "Maintain the brands used by products and catalogues.", "primary_fields": ["brand"], "default_columns": ["name", "brand", "description", "modified"], "main_filters": []},
	"UOM": {"plural": "Units of Measure", "description": "Maintain units of measure used by products and transactions.", "primary_fields": ["uom_name", "must_be_whole_number"], "default_columns": ["name", "uom_name", "must_be_whole_number", "enabled", "modified"], "main_filters": ["must_be_whole_number", "enabled"]},
	"Sales Person": {"plural": "Sales People", "description": "Maintain the sales-person hierarchy and allocation settings.", "primary_fields": ["sales_person_name", "parent_sales_person", "is_group", "enabled"], "default_columns": ["name", "sales_person_name", "parent_sales_person", "is_group", "enabled", "modified"], "main_filters": ["parent_sales_person", "is_group", "enabled"]},
	"Price List": {"plural": "Price Lists", "description": "Manage buying and selling price-list definitions and currencies.", "primary_fields": ["price_list_name", "currency", "selling", "buying"], "default_columns": ["name", "price_list_name", "currency", "selling", "buying", "enabled", "modified"], "main_filters": ["currency", "selling", "buying", "enabled"]},
	"Mode of Payment": {"plural": "Modes of Payment", "description": "Maintain payment methods and their permitted account defaults.", "primary_fields": ["mode_of_payment", "type", "enabled"], "default_columns": ["name", "mode_of_payment", "type", "enabled", "modified"], "main_filters": ["type", "enabled"]},
	"Cost Center": {"plural": "Cost Centers", "description": "Maintain the accounting cost-center hierarchy for permitted companies.", "primary_fields": ["cost_center_name", "company", "parent_cost_center", "is_group"], "default_columns": ["name", "cost_center_name", "company", "parent_cost_center", "is_group", "disabled", "modified"], "main_filters": ["company", "parent_cost_center", "is_group", "disabled"]},
	"Department": {"plural": "Departments", "description": "Maintain organisation departments and company assignments.", "primary_fields": ["department_name", "company", "parent_department", "is_group"], "default_columns": ["name", "department_name", "company", "parent_department", "is_group", "disabled", "modified"], "main_filters": ["company", "parent_department", "is_group", "disabled"]},
	"Designation": {"plural": "Designations", "description": "Maintain employee designation names and descriptions.", "primary_fields": ["designation_name"], "default_columns": ["name", "designation_name", "description", "modified"], "main_filters": []},
}

SUPPORTED_FIELD_TYPES = {
	"Data", "Link", "Dynamic Link", "Select", "Date", "Datetime", "Time", "Currency", "Float", "Int",
	"Percent", "Check", "Small Text", "Text", "Long Text", "Text Editor", "Code", "Attach", "Attach Image",
	"Color", "Duration", "Rating", "Barcode", "Signature", "Geolocation", "HTML", "Section Break", "Column Break",
	"Tab Break", "Table", "Table MultiSelect", "Button",
}

_registry_cache = {"mtime": None, "records": None, "by_key": None}


def _inventory_path() -> Path:
	return Path(__file__).resolve().parents[2] / "docs" / "erpnext-v15-complete-inventory.json"


def _route_key(name: str) -> str:
	return frappe.scrub(name).replace("_", "-")


def _implementation_type(source: dict) -> str:
	if not source.get("user_facing"):
		return "internal"
	if source.get("feature_type") == "doctype" and source.get("doctype") in CUSTOM_OVERRIDES:
		return "custom"
	if source.get("feature_type") == "doctype" and source.get("doctype") in ALL_GENERATED_DOCTYPES:
		return "generated_provisional"
	if source.get("feature_type") in {"report", "page", "workspace", "dashboard", "dashboard_chart", "number_card"}:
		return "special"
	return "unavailable"


def _normalise(source: dict) -> dict:
	name = source.get("doctype") or source.get("report") or source.get("page") or source.get("name")
	implementation = _implementation_type(source)
	route_key = _route_key(name or source["feature_id"])
	base = CUSTOM_OVERRIDES.get(source.get("doctype"))
	generated_base = (CANONICAL_ROUTE_BY_DOCTYPE.get(source.get("doctype")) or f"/generated/{route_key}") if implementation.startswith("generated") else None
	presentation = PRESENTATION_OVERRIDES.get(source.get("doctype"), {})
	return {
		"feature_id": source["feature_id"], "route_key": route_key, "feature_label": name,
		"application": source.get("application"), "module": source.get("module"),
		"category": source.get("feature_type"), "doctype": source.get("doctype"), "page": source.get("page"),
		"report": source.get("report"), "workspace": source.get("name") if source.get("feature_type") == "workspace" else None,
		"route": base or generated_base, "list_route": base or generated_base,
		"create_route": f"{base or generated_base}/new" if base or generated_base else None,
		"detail_route": f"{base or generated_base}/{{name}}" if base or generated_base else None,
		"edit_route": f"{base or generated_base}/{{name}}/edit" if base or generated_base else None,
		"implementation_type": implementation, "custom_override": bool(base),
		"generated_component": "UniversalDocument" if generated_base else None,
		"supported_views": source.get("supported_views") or (["List", "Form"] if source.get("doctype") else []),
		"available_actions": source.get("actions") or source.get("mapped_actions") or [],
		"required_permissions": source.get("doctype_permissions") or source.get("page_permissions") or source.get("report_permissions") or [],
		"child_doctypes": source.get("child_tables") or [], "workflow_state": source.get("active_workflow"),
		"print_support": bool(source.get("print")), "pdf_support": bool(source.get("pdf")),
		"email_support": bool(source.get("email")), "import_support": bool(source.get("import")),
		"export_support": bool(source.get("export")), "testing_state": source.get("test_status") or "Not tested",
		"documentation_state": "Inventory documented", "known_limitations": source.get("remaining_desk_dependency"),
		"user_facing": bool(source.get("user_facing")), "source_location": source.get("source_location") or [],
		**({"presentation": {"accent": MODULE_PRESENTATION.get(source.get("module"), "blue"), **presentation}} if implementation.startswith("generated") else {}),
	}


def _synthetic_features() -> list[dict]:
	return [
		{"feature_id": "my_store_ui:special:payment-entry-allocation", "route_key": "payment-entry-allocation", "feature_label": "Payment Entry Allocation", "application": "my_store_ui", "module": "Accounts", "category": "special", "doctype": "Payment Entry", "page": None, "report": None, "workspace": None, "route": "/finance/payments/new", "list_route": "/finance/payments", "create_route": "/finance/payments/new", "detail_route": "/finance/payments/{name}", "edit_route": "/finance/payments/{name}/edit", "implementation_type": "custom", "custom_override": True, "generated_component": None, "supported_views": ["Dialog"], "available_actions": ["allocate"], "required_permissions": ["Payment Entry:read/create/write"], "child_doctypes": ["Payment Entry Reference"], "workflow_state": None, "print_support": False, "pdf_support": False, "email_support": False, "import_support": False, "export_support": False, "testing_state": "Automated", "documentation_state": "Documented", "known_limitations": None, "user_facing": True, "source_location": []},
		{"feature_id": "my_store_ui:page:smart-sales", "route_key": "smart-sales", "feature_label": "Smart Sales", "application": "my_store_ui", "module": "Selling", "category": "special", "doctype": None, "page": "smart-sales", "report": None, "workspace": None, "route": "/smart-sales", "list_route": "/smart-sales", "create_route": None, "detail_route": None, "edit_route": None, "implementation_type": "custom", "custom_override": True, "generated_component": None, "supported_views": ["POS"], "available_actions": ["cart", "draft_sales_order"], "required_permissions": [], "child_doctypes": [], "workflow_state": None, "print_support": False, "pdf_support": False, "email_support": False, "import_support": False, "export_support": False, "testing_state": "Automated", "documentation_state": "Documented", "known_limitations": "Full catalogue migration remains", "user_facing": True, "source_location": []},
	]


def get_registry_records() -> list[dict]:
	path = _inventory_path()
	mtime = path.stat().st_mtime_ns
	if _registry_cache["records"] is None or _registry_cache["mtime"] != mtime:
		source = json.loads(path.read_text())
		records = [_normalise(feature) for feature in source.get("features", [])]
		records.extend(_synthetic_features())
		by_key = {}
		for record in records:
			by_key[record["feature_id"]] = record
			by_key[f"{record['category']}:{record['route_key']}"] = record
			if record["category"] == "doctype":
				by_key[record["route_key"]] = record
		_registry_cache.update({"mtime": mtime, "records": records, "by_key": by_key})
	return _registry_cache["records"]


def get_feature(feature: str) -> dict:
	get_registry_records()
	record = _registry_cache["by_key"].get(str(feature or ""))
	if not record or record["implementation_type"] == "internal":
		frappe.throw("Feature is not registered.", frappe.DoesNotExistError)
	return record


def feature_is_permitted(record: dict, permission: str = "read") -> bool:
	if frappe.session.user == "Guest":
		return False
	if record.get("implementation_type") in {"internal", "unavailable"}:
		return False
	if record.get("doctype"):
		required_roles = ADMIN_FEATURE_ROLES.get(record["doctype"])
		if required_roles and frappe.session.user != "Administrator" and not required_roles.intersection(frappe.get_roles()):
			return False
		return frappe.has_permission(record["doctype"], permission)
	if record.get("feature_id") == "my_store_ui:page:smart-sales":
		return any(frappe.has_permission(doctype, "read") for doctype in ("Customer", "Item", "Sales Order"))
	if record.get("report"):
		return bool(frappe.db.exists("Report", record["report"]) and frappe.has_permission("Report", "read", doc=record["report"]))
	if record.get("page"):
		return bool(frappe.db.exists("Page", record["page"]) and frappe.has_permission("Page", "read", doc=record["page"]))
	if record.get("workspace"):
		try:
			return bool(frappe.get_doc("Workspace", record["workspace"]).is_permitted())
		except Exception:
			return False
	# Dashboard/visual adapters need their own role-aware resolver before exposure.
	return False


def get_generated_feature(feature: str, permission: str = "read") -> dict:
	record = get_feature(feature)
	if record["implementation_type"] not in {"generated", "generated_provisional"}:
		frappe.throw("This feature is not available through the generated engine.", frappe.PermissionError)
	if not feature_is_permitted(record, permission):
		frappe.throw("Feature is not available.", frappe.PermissionError)
	return record


def generate_registry_artifact() -> dict:
	"""Write the deterministic registry snapshot used by coverage review.

	This is documentation-only and performs no database writes.
	"""
	records = sorted(get_registry_records(), key=lambda row: row["feature_id"])
	counts = {}
	for record in records:
		counts[record["implementation_type"]] = counts.get(record["implementation_type"], 0) + 1
	payload = {
		"schema_version": 1,
		"source_inventory": "erpnext-v15-complete-inventory.json",
		"routing_priority": ["custom", "generated", "special", "unavailable"],
		"counts": counts,
		"records": records,
	}
	path = _inventory_path().parent / "universal-feature-registry.json"
	path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
	return {"path": str(path), "total": len(records), "counts": counts}
