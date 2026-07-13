from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import frappe
from frappe.model import NO_VALUE_FIELDS
from frappe.utils import cint


SCHEMA_VERSION = 1
GENERATED_START = "<!-- BEGIN MACHINE-GENERATED FEATURE INVENTORY -->"
GENERATED_END = "<!-- END MACHINE-GENERATED FEATURE INVENTORY -->"

CAPABILITY_KEYS = (
	"create", "read", "write", "delete", "submit", "cancel", "amend", "import", "export",
	"print", "pdf", "email", "share", "assign", "comment", "attach",
)

SPECIALIZED_DOCTYPES = {
	"Account", "Asset", "Asset Movement", "BOM", "Bank Transaction", "Delivery Note", "Item",
	"Job Card", "Journal Entry", "Material Request", "Payment Entry", "Pick List", "POS Invoice",
	"Production Plan", "Purchase Invoice", "Purchase Order", "Purchase Receipt", "Quality Inspection",
	"Quotation", "Request for Quotation", "Sales Invoice", "Sales Order", "Stock Entry",
	"Stock Reconciliation", "Subcontracting Order", "Subcontracting Receipt", "Supplier Quotation",
	"Work Order",
}

ADMIN_MODULES = {
	"Core", "Custom", "Desk", "Email", "Integrations", "Printing", "Setup", "Social", "Website",
	"Workflow",
}

INTERNAL_DOCTYPES = {
	"Activity Log", "Access Log", "Background Task", "Deleted Document", "Document Follow",
	"Document Share Key", "Error Log", "Event Sync Log", "Integration Request", "Prepared Report",
	"RQ Job", "Route History", "Scheduled Job Log", "Token Cache", "Unhandled Email", "View Log",
	"Webhook Request Log",
}

ACTION_NAME_RE = re.compile(
	r"^(?:make_|create_|get_payment_entry|close$|reopen$|hold$|unhold$|stop$|resume$|start$|"
	r"finish$|complete$|update_status$|set_status$|cancel_|submit_)",
	re.I,
)
WHITELISTED_RE = re.compile(
	r"@frappe\.whitelist(?:\([^)]*\))?\s*(?:@[^\n]+\s*)*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.M
)
BUTTON_RE = re.compile(r"add_custom_button\s*\(\s*(?:__?\()?\s*['\"]([^'\"]+)['\"]", re.M)


def _slug(value: str) -> str:
	return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-") or "unnamed"


def _feature_id(application: str, feature_type: str, name: str, parent: str | None = None) -> str:
	parts = (application or "unknown", feature_type, parent or "", name)
	return ":".join(_slug(part) for part in parts if part)


def _json_value(value: Any):
	if isinstance(value, datetime | date):
		return value.isoformat()
	if isinstance(value, bytes):
		return value.decode(errors="replace")
	if isinstance(value, frappe._dict):
		return {key: _json_value(item) for key, item in value.items()}
	if isinstance(value, dict):
		return {str(key): _json_value(item) for key, item in value.items()}
	if isinstance(value, list | tuple | set):
		return [_json_value(item) for item in value]
	return value


def _base_feature(**values) -> dict:
	feature = {
		"feature_id": "",
		"application": "",
		"module": "",
		"feature_type": "",
		"name": "",
		"doctype": None,
		"report": None,
		"page": None,
		"tool": None,
		"parent_feature": None,
		"child_doctype": None,
		"route": None,
		"source_location": [],
		"standard_desk_route": None,
		"standard_list_route": None,
		"standard_form_route": None,
		"current_custom_route": None,
		"relevant_roles": [],
		"doctype_permissions": [],
		"page_permissions": [],
		"report_permissions": [],
		"active_workflow": None,
		"supported_views": [],
		"metadata": {},
		"fields": [],
		"child_tables": [],
		"links": [],
		"controller_class": None,
		"actions": [],
		**{key: False for key in CAPABILITY_KEYS},
		"mapped_actions": [],
		"related_documents": [],
		"status_dependent_actions": [],
		"customizations": [],
		"implementation_type": "",
		"classification": "",
		"user_facing": True,
		"exclusion_reason": None,
		"test_status": "Not tested",
		"completion_status": "Not implemented",
		"remaining_desk_dependency": "Required for ordinary-user parity",
		"notes": [],
	}
	feature.update(values)
	return _json_value(feature)


def _existing_fields(doctype: str, requested: list[str]) -> list[str]:
	meta = frappe.get_meta(doctype)
	valid = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "parent", "parenttype", "parentfield"}
	valid.update(field.fieldname for field in meta.fields if field.fieldtype not in NO_VALUE_FIELDS)
	return [field for field in requested if field in valid]


def _get_all(doctype: str, fields: list[str], **kwargs) -> list[frappe._dict]:
	if not frappe.db.exists("DocType", doctype):
		return []
	return frappe.get_all(doctype, fields=_existing_fields(doctype, fields), **kwargs)


def _load_json(path: Path) -> dict | list | None:
	try:
		return json.loads(path.read_text(encoding="utf-8"))
	except (OSError, UnicodeDecodeError, json.JSONDecodeError):
		return None


def _app_paths(installed_apps: list[str]) -> tuple[dict[str, Path], dict[str, Path]]:
	package_paths = {}
	repo_paths = {}
	for app in installed_apps:
		try:
			package = Path(frappe.get_app_path(app)).resolve()
		except Exception:
			continue
		package_paths[app] = package
		repo_paths[app] = package.parent
	return package_paths, repo_paths


def _source_catalog(installed_apps: list[str], package_paths: dict[str, Path]) -> dict:
	catalog = {
		"doctypes": {}, "reports": {}, "pages": {}, "workspaces": {}, "dashboards": defaultdict(list),
		"actions": [], "modules": defaultdict(set), "hooks": {}, "source_counts": defaultdict(Counter),
		"customization_owners": {},
	}
	for app in installed_apps:
		package = package_paths.get(app)
		if not package:
			continue
		modules_file = package / "modules.txt"
		if modules_file.exists():
			catalog["modules"][app].update(
				line.strip() for line in modules_file.read_text(encoding="utf-8").splitlines() if line.strip()
			)
		hooks_file = package / "hooks.py"
		if hooks_file.exists():
			text = hooks_file.read_text(encoding="utf-8", errors="replace")
			try:
				tree = ast.parse(text)
				hook_names = sorted(
					node.targets[0].id for node in tree.body
					if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
				)
			except SyntaxError:
				hook_names = []
			catalog["hooks"][app] = {"source": str(hooks_file), "declared_names": hook_names}

		for path in sorted(package.rglob("*.json")):
			parts = path.parts
			data = _load_json(path)
			if "fixtures" in parts and isinstance(data, list):
				for record in data:
					if isinstance(record, dict) and record.get("doctype") and record.get("name"):
						catalog["customization_owners"][(record["doctype"], record["name"])] = app
				continue
			if not isinstance(data, dict):
				continue
			relative = str(path.relative_to(package))
			if "doctype" in parts and data.get("doctype") == "DocType" and data.get("name"):
				catalog["doctypes"][data["name"]] = {"app": app, "source": relative, "data": data}
				catalog["source_counts"][app]["doctype"] += 1
			elif "report" in parts and data.get("doctype") == "Report" and data.get("name"):
				catalog["reports"][data["name"]] = {"app": app, "source": relative, "data": data}
				catalog["source_counts"][app]["report"] += 1
			elif "page" in parts and data.get("doctype") == "Page" and data.get("name"):
				catalog["pages"][data["name"]] = {"app": app, "source": relative, "data": data}
				catalog["source_counts"][app]["page"] += 1
			elif "workspace" in parts and data.get("doctype") == "Workspace" and data.get("name"):
				catalog["workspaces"][data["name"]] = {"app": app, "source": relative, "data": data}
				catalog["source_counts"][app]["workspace"] += 1

		for path in sorted(package.rglob("*_dashboard.py")):
			parent_slug = path.stem.removesuffix("_dashboard")
			parent = next(
				(name for name, entry in catalog["doctypes"].items() if entry["app"] == app and _slug(name) == parent_slug.replace("_", "-")),
				parent_slug.replace("_", " ").title(),
			)
			text = path.read_text(encoding="utf-8", errors="replace")
			catalog["dashboards"][parent].append({"app": app, "source": str(path.relative_to(package)), "text": text})

		for path in sorted(package.rglob("*.py")):
			if "doctype" not in path.parts:
				continue
			text = path.read_text(encoding="utf-8", errors="replace")
			parent = _parent_doctype_for_source(path, catalog["doctypes"], app)
			for match in WHITELISTED_RE.finditer(text):
				action = match.group(1)
				if ACTION_NAME_RE.match(action):
					catalog["actions"].append(
						{"app": app, "parent": parent, "action": action, "label": action.replace("_", " ").title(),
						 "source": str(path.relative_to(package)), "status_dependent": bool(re.search(r"docstatus|status", text[max(0, match.start()-400):match.end()+900]))}
					)
		for path in sorted(package.rglob("*.js")):
			if "doctype" not in path.parts:
				continue
			text = path.read_text(encoding="utf-8", errors="replace")
			parent = _parent_doctype_for_source(path, catalog["doctypes"], app)
			for match in BUTTON_RE.finditer(text):
				label = match.group(1)
				catalog["actions"].append(
					{"app": app, "parent": parent, "action": _slug(label).replace("-", "_"), "label": label,
					 "source": str(path.relative_to(package)), "status_dependent": bool(re.search(r"docstatus|status", text[max(0, match.start()-500):match.end()+500]))}
				)

	return catalog


def _parent_doctype_for_source(path: Path, source_doctypes: dict, app: str) -> str:
	try:
		slug = path.parts[path.parts.index("doctype") + 1]
	except (ValueError, IndexError):
		return path.stem.replace("_", " ").title()
	return next(
		(name for name, entry in source_doctypes.items() if entry["app"] == app and _slug(name) == slug.replace("_", "-")),
		slug.replace("_", " ").title(),
	)


def _module_app_map(module_rows: list[frappe._dict], catalog: dict, installed_apps: list[str]) -> dict[str, str]:
	mapping = {}
	for row in module_rows:
		if row.get("app_name") in installed_apps:
			mapping[row.name] = row.app_name
	for app, modules in catalog["modules"].items():
		for module in modules:
			mapping.setdefault(module, app)
	return mapping


def _permissions_by_parent(doctype: str) -> dict[str, list[dict]]:
	rows = _get_all(
		doctype,
		["parent", "role", "permlevel", "read", "write", "create", "delete", "submit", "cancel", "amend", "report", "export", "import", "email", "print", "share"],
		order_by="parent asc, permlevel asc, role asc",
	)
	result = defaultdict(list)
	for row in rows:
		result[row.parent].append(dict(row))
	return result


def _aggregate_permissions(rows: list[dict], *, allow_import=False, is_table=False) -> dict:
	result = {key: False for key in CAPABILITY_KEYS}
	for key in ("create", "read", "write", "delete", "submit", "cancel", "amend", "export", "email", "print", "share"):
		result[key] = any(cint(row.get(key)) for row in rows)
	result["import"] = bool(allow_import and any(cint(row.get("import")) for row in rows))
	result["pdf"] = result["print"]
	if result["read"] and not is_table:
		result.update({"assign": True, "comment": True, "attach": True})
	return result


def _doctype_classification(row: frappe._dict) -> tuple[str, str, bool, str | None]:
	if cint(row.get("istable")):
		return "G", "System-internal and not independently user-facing", False, "Child table rendered through its parent document"
	if row.name in INTERNAL_DOCTYPES:
		return "G", "System-internal and not user-facing", False, "Framework log, queue, cache or technical record"
	if row.name in SPECIALIZED_DOCTYPES:
		return "B", "Specialized transaction interface", True, None
	if cint(row.get("is_tree")) or row.get("default_view") in {"Tree", "Calendar", "Kanban", "Gantt", "Map", "Image"}:
		return "C", "Specialized visual view", True, None
	if row.module in ADMIN_MODULES:
		return "E", "Administrative interface", True, None
	return "A", "Generic list/detail/form engine", True, None


def _source_locations(name: str, catalog: dict, source_type: str) -> list[str]:
	entry = catalog.get(source_type, {}).get(name)
	return [f"{entry['app']}:{entry['source']}"] if entry else []


def _controller_classes(source: dict | None, package_paths: dict[str, Path]) -> list[str]:
	if not source:
		return []
	json_path = package_paths[source["app"]] / source["source"]
	controller = json_path.with_suffix(".py")
	if not controller.exists():
		return []
	try:
		tree = ast.parse(controller.read_text(encoding="utf-8", errors="replace"))
	except SyntaxError:
		return []
	return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def _report_source_metadata(source: dict | None, package_paths: dict[str, Path]) -> dict:
	if not source:
		return {"files": [], "has_chart": False, "has_totals": False, "declares_filters": False, "filter_fieldnames": [], "column_fieldnames": []}
	directory = (package_paths[source["app"]] / source["source"]).parent
	files = []
	text = ""
	for path in sorted(directory.glob("*")):
		if path.suffix in {".py", ".js", ".json"}:
			files.append(str(path.relative_to(package_paths[source["app"]])))
			text += path.read_text(encoding="utf-8", errors="replace")
	return {
		"files": files,
		"has_chart": bool(re.search(r"\bchart\b|chart_data|report_summary", text, re.I)),
		"has_totals": bool(re.search(r"add_total_row|total_row|report_summary|\btotals?\b", text, re.I)),
		"declares_filters": bool(re.search(r"\bfilters\b|get_filters", text)),
		"filter_fieldnames": sorted(set(re.findall(r"fieldname\s*[:=]\s*['\"]([^'\"]+)", text))),
		"column_fieldnames": sorted(set(re.findall(r"(?:fieldname|field)\s*[:=]\s*['\"]([^'\"]+)", text))),
	}


def _doctype_views(row: frappe._dict, source: dict | None, calendars: set[str], kanbans: set[str], dashboards: set[str]) -> list[str]:
	views = ["List", "Form"]
	if cint(row.get("is_tree")):
		views.append("Tree")
	default_view = row.get("default_view")
	if default_view and default_view not in views:
		views.append(default_view)
	if row.name in calendars:
		views.append("Calendar")
	if row.name in kanbans:
		views.append("Kanban")
	if row.name in dashboards:
		views.append("Dashboard")
	if source:
		base = Path(source["source"]).parent
		package = source.get("package")
		if package:
			for view, suffix in (("Calendar", "_calendar.js"), ("Tree", "_tree.js"), ("List", "_list.js")):
				if any((package / base).glob(f"*{suffix}")) and view not in views:
					views.append(view)
	return sorted(set(views))


def _custom_route_for_doctype(name: str) -> str | None:
	custom = {
		"Customer": "/retail-erp/sales/customers",
		"Item": "/retail-erp/inventory/products",
		"Sales Order": "/retail-erp/sales/orders",
		"Delivery Note": "/retail-erp/sales/delivery-notes",
		"Sales Invoice": "/retail-erp/sales/invoices",
		"Payment Entry": "/retail-erp/finance/payments",
	}
	if name in custom:
		return custom[name]
	# The priority registry is a pure server-owned declaration. Importing it
	# here keeps the generated inventory aligned with clean registered routes
	# without making any feature discoverable merely because it exists.
	from my_store_ui.services.priority_registry import CANONICAL_ROUTE_BY_DOCTYPE
	return CANONICAL_ROUTE_BY_DOCTYPE.get(name)


def _custom_route_for_report(name: str) -> str | None:
	from my_store_ui.services.priority_registry import REPORT_GROUPS
	if name not in {report for reports in REPORT_GROUPS.values() for report in reports}:
		return None
	return f"/retail-erp/reports/view/{quote(name, safe='')}"


def _collect_database_snapshot() -> dict:
	return {
		"modules": _get_all("Module Def", ["name", "app_name", "custom", "restrict_to_domain", "disabled"], order_by="name asc"),
		"doctypes": _get_all("DocType", ["name", "module", "custom", "istable", "is_submittable", "is_tree", "issingle", "is_virtual", "editable_grid", "track_changes", "autoname", "title_field", "image_field", "search_fields", "allow_import", "default_view", "document_type", "icon", "modified"], order_by="name asc"),
		"docfields": _get_all("DocField", ["parent", "fieldname", "label", "fieldtype", "options", "reqd", "read_only", "hidden", "permlevel", "in_list_view", "in_standard_filter", "depends_on", "mandatory_depends_on"], order_by="parent asc, idx asc"),
		"doctype_links": _get_all("DocType Link", ["parent", "link_doctype", "link_fieldname", "group", "hidden"], order_by="parent asc, idx asc"),
		"doctype_actions": _get_all("DocType Action", ["parent", "label", "action", "group", "hidden"], order_by="parent asc, idx asc"),
		"custom_fields": _get_all("Custom Field", ["name", "dt", "fieldname", "label", "fieldtype", "options", "insert_after", "default", "reqd", "read_only", "hidden", "permlevel", "non_negative", "depends_on", "mandatory_depends_on"], order_by="dt asc, idx asc"),
		"property_setters": _get_all("Property Setter", ["name", "doc_type", "field_name", "property", "value", "property_type"], order_by="doc_type asc, name asc"),
		"reports": _get_all("Report", ["name", "module", "ref_doctype", "report_type", "is_standard", "disabled", "prepared_report", "add_total_row", "columns", "filters", "json", "custom_report"], order_by="name asc"),
		"report_columns": _get_all("Report Column", ["parent", "fieldname", "label", "fieldtype", "options", "width"], order_by="parent asc, idx asc"),
		"report_filters": _get_all("Report Filter", ["parent", "fieldname", "label", "fieldtype", "options", "mandatory", "default"], order_by="parent asc, idx asc"),
		"pages": _get_all("Page", ["name", "page_name", "title", "module", "standard", "system_page", "icon"], order_by="name asc"),
		"workspaces": _get_all("Workspace", ["name", "title", "module", "app", "public", "is_hidden", "content", "for_user", "restrict_to_domain"], order_by="name asc"),
		"workspace_links": _get_all("Workspace Link", ["parent", "label", "type", "link_type", "link_to", "hidden"], order_by="parent asc, idx asc"),
		"workspace_shortcuts": _get_all("Workspace Shortcut", ["parent", "label", "type", "link_to", "doc_view", "report_ref_doctype"], order_by="parent asc, idx asc"),
		"workspace_charts": _get_all("Workspace Chart", ["parent", "chart_name"], order_by="parent asc, idx asc"),
		"workspace_number_cards": _get_all("Workspace Number Card", ["parent", "number_card_name"], order_by="parent asc, idx asc"),
		"workspace_quick_lists": _get_all("Workspace Quick List", ["parent", "document_type", "label", "quick_list_filter"], order_by="parent asc, idx asc"),
		"workflows": _get_all("Workflow", ["name", "document_type", "workflow_name", "is_active", "module", "workflow_state_field", "send_email_alert"], order_by="name asc"),
		"workflow_states": _get_all("Workflow Document State", ["parent", "state", "doc_status", "allow_edit", "is_optional_state"], order_by="parent asc, idx asc"),
		"workflow_transitions": _get_all("Workflow Transition", ["parent", "state", "action", "next_state", "allowed", "condition", "allow_self_approval"], order_by="parent asc, idx asc"),
		"print_formats": _get_all("Print Format", ["name", "doc_type", "module", "standard", "custom_format", "disabled", "print_format_type", "raw_printing", "default_print_language"], order_by="doc_type asc, name asc"),
		"client_scripts": _get_all("Client Script", ["name", "dt", "view", "enabled", "module", "script"], order_by="dt asc, name asc"),
		"server_scripts": _get_all("Server Script", ["name", "script_type", "reference_doctype", "api_method", "disabled", "module", "script"], order_by="name asc"),
		"custom_docperms": _get_all("Custom DocPerm", ["name", "parent", "role", "permlevel", "read", "write", "create", "delete", "submit", "cancel", "amend", "report", "export", "import", "email", "print", "share"], order_by="parent asc, role asc"),
		"roles": _get_all("Role", ["name", "desk_access", "is_custom", "disabled", "restrict_to_domain"], order_by="name asc"),
		"calendar_views": _get_all("Calendar View", ["name", "reference_doctype", "subject_field", "start_date_field", "end_date_field"], order_by="name asc"),
		"kanban_boards": _get_all("Kanban Board", ["name", "reference_doctype", "field_name", "private"], order_by="name asc"),
		"dashboards": _get_all("Dashboard", ["name", "module", "is_standard"], order_by="name asc"),
		"dashboard_charts": _get_all("Dashboard Chart", ["name", "chart_name", "chart_type", "document_type", "report_name", "module", "is_public", "is_standard"], order_by="name asc"),
		"number_cards": _get_all("Number Card", ["name", "label", "type", "document_type", "report_name", "module", "is_public", "is_standard"], order_by="name asc"),
		"notification": _get_all("Notification", ["name", "document_type", "event", "enabled", "channel", "module"], order_by="name asc"),
		"auto_email_reports": _get_all("Auto Email Report", ["name", "report", "enabled", "user"], order_by="name asc"),
		"data_imports": _get_all("Data Import", ["name", "reference_doctype", "status", "import_type"], order_by="modified desc", limit_page_length=50),
		"installed_application_records": _get_all("Installed Application", ["app_name", "app_version", "git_branch", "has_setup_wizard", "is_setup_complete"], order_by="idx asc"),
	}


def _group_by(rows: list[frappe._dict], key: str) -> dict[str, list[frappe._dict]]:
	result = defaultdict(list)
	for row in rows:
		result[row.get(key)].append(row)
	return result


def _workspace_targets(workspace: frappe._dict, snapshot: dict) -> list[dict]:
	content = workspace.get("content")
	targets = []

	def walk(value):
		if isinstance(value, dict):
			block_type = value.get("type") or value.get("widget_type")
			block_data = value.get("data") if isinstance(value.get("data"), dict) else value
			target = block_data.get("link_to") or block_data.get("name") or block_data.get("report_name")
			target_type = block_data.get("link_type") or block_data.get("type") or block_type
			if target and target_type and str(target_type).lower() in {
				"doctype", "report", "page", "card", "shortcut", "link", "quick_list", "number_card", "chart"
			}:
				targets.append({"type": target_type, "target": target, "label": block_data.get("label")})
			for item in value.values():
				walk(item)
		elif isinstance(value, list):
			for item in value:
				walk(item)

	if content:
		try:
			data = json.loads(content) if isinstance(content, str) else content
		except (TypeError, json.JSONDecodeError):
			data = []
		walk(data)
	for row in snapshot["workspace_links"]:
		if row.parent == workspace.name and not cint(row.get("hidden")) and row.get("link_to"):
			targets.append({"type": row.get("link_type") or row.get("type") or "Link", "target": row.link_to, "label": row.get("label")})
	for row in snapshot["workspace_shortcuts"]:
		if row.parent == workspace.name and row.get("link_to"):
			targets.append({"type": row.get("type") or "Shortcut", "target": row.link_to, "label": row.get("label")})
	for row in snapshot["workspace_charts"]:
		if row.parent == workspace.name and row.get("chart_name"):
			targets.append({"type": "Chart", "target": row.chart_name, "label": row.chart_name})
	for row in snapshot["workspace_number_cards"]:
		if row.parent == workspace.name and row.get("number_card_name"):
			targets.append({"type": "Number Card", "target": row.number_card_name, "label": row.number_card_name})
	for row in snapshot["workspace_quick_lists"]:
		if row.parent == workspace.name and row.get("document_type"):
			targets.append({"type": "Quick List", "target": row.document_type, "label": row.get("label")})
	unique = {}
	for item in targets:
		key = (str(item["type"]), str(item["target"]))
		if key not in unique or (item.get("label") and len(str(item["label"])) < len(str(unique[key].get("label") or "~"))):
			unique[key] = item
	return [unique[key] for key in sorted(unique)]


def _dashboard_related(catalog: dict, doctype_names: set[str]) -> dict[str, list[str]]:
	result = defaultdict(set)
	for parent, entries in catalog["dashboards"].items():
		for entry in entries:
			try:
				tree = ast.parse(entry["text"])
			except SyntaxError:
				continue
			for node in ast.walk(tree):
				if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in doctype_names and node.value != parent:
					result[parent].add(node.value)
	return {key: sorted(values) for key, values in result.items()}


def _customizations_for(doctype: str, snapshot: dict) -> list[dict]:
	customizations = []
	for row in snapshot["custom_fields"]:
		if row.dt == doctype:
			customizations.append({"type": "Custom Field", "name": row.name, "fieldname": row.fieldname})
	for row in snapshot["property_setters"]:
		if row.doc_type == doctype:
			customizations.append({"type": "Property Setter", "name": row.name, "property": row.property})
	for row in snapshot["client_scripts"]:
		if row.dt == doctype and not cint(row.get("enabled") == 0):
			customizations.append({"type": "Client Script", "name": row.name})
	for row in snapshot["server_scripts"]:
		if row.reference_doctype == doctype and not cint(row.get("disabled")):
			customizations.append({"type": "Server Script", "name": row.name})
	return customizations


def _legacy_matrix_rows(matrix_text: str) -> list[list[str]]:
	base = matrix_text.split(GENERATED_START, 1)[0]
	if "## Complete feature and route inventory" in base:
		base = base.split("## Complete feature and route inventory", 1)[1]
		base = base.split("\n## ", 1)[0]
	rows = []
	for line in base.splitlines():
		if not line.startswith("|") or re.match(r"^\|\s*-", line):
			continue
		cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
		if cells and cells[0] not in {"Module", "Page type", "Source", "Role/persona", "Feature class", "Source type", "Phase", "Source document"}:
			rows.append(cells)
	return rows


def _legacy_represents(feature: dict, legacy_rows: list[list[str]]) -> bool:
	needle = (feature.get("doctype") or feature.get("report") or feature.get("page") or feature["name"]).lower()
	for row in legacy_rows:
		joined = " | ".join(row).lower()
		if needle and re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", joined):
			return True
	return False


def _build_features(installed_apps: list[str], package_paths: dict[str, Path], catalog: dict, snapshot: dict, matrix_text: str) -> tuple[list[dict], dict]:
	module_app = _module_app_map(snapshot["modules"], catalog, installed_apps)
	docfields = _group_by(snapshot["docfields"], "parent")
	custom_fields_by_dt = _group_by(snapshot["custom_fields"], "dt")
	doctype_links = _group_by(snapshot["doctype_links"], "parent")
	doctype_actions = _group_by(snapshot["doctype_actions"], "parent")
	permissions = _permissions_by_parent("DocPerm")
	custom_permissions = _group_by(snapshot["custom_docperms"], "parent")
	workflow_by_doctype = {row.document_type: row for row in snapshot["workflows"] if cint(row.get("is_active"))}
	report_columns = _group_by(snapshot["report_columns"], "parent")
	report_filters = _group_by(snapshot["report_filters"], "parent")
	workflow_states = _group_by(snapshot["workflow_states"], "parent")
	workflow_transitions = _group_by(snapshot["workflow_transitions"], "parent")
	calendar_doctypes = {row.reference_doctype for row in snapshot["calendar_views"] if row.get("reference_doctype")}
	kanban_doctypes = {row.reference_doctype for row in snapshot["kanban_boards"] if row.get("reference_doctype")}
	dashboard_doctypes = set(catalog["dashboards"])
	doctype_names = {row.name for row in snapshot["doctypes"]}
	dashboard_links = _dashboard_related(catalog, doctype_names)
	all_actions = list(catalog["actions"])
	for action in snapshot["doctype_actions"]:
		parent_source = catalog["doctypes"].get(action.parent)
		parent_row = next((row for row in snapshot["doctypes"] if row.name == action.parent), None)
		application = parent_source["app"] if parent_source else module_app.get(parent_row.module if parent_row else "", "unknown")
		all_actions.append({
			"app": application, "parent": action.parent, "action": action.get("action") or _slug(action.get("label") or "action").replace("-", "_"),
			"label": action.get("label") or action.get("action"), "source": "database:DocType Action", "status_dependent": False,
		})
	actions_by_parent = defaultdict(list)
	for action in all_actions:
		actions_by_parent[action["parent"]].append(action)
	features = []
	feature_by_doctype = {}

	for row in snapshot["doctypes"]:
		source = catalog["doctypes"].get(row.name)
		application = source["app"] if source else module_app.get(row.module, "custom" if cint(row.get("custom")) else "unknown")
		classification, implementation_type, user_facing, exclusion = _doctype_classification(row)
		perm_rows = [dict(item) for item in permissions.get(row.name, []) + custom_permissions.get(row.name, [])]
		capabilities = _aggregate_permissions(perm_rows, allow_import=cint(row.get("allow_import")), is_table=cint(row.get("istable")))
		workflow = workflow_by_doctype.get(row.name)
		mapped_actions = []
		status_actions = []
		for action in sorted(actions_by_parent.get(row.name, []), key=lambda item: (item["action"], item["source"])):
			payload = {"action": action["action"], "label": action["label"], "source": f"{action['app']}:{action['source']}"}
			mapped_actions.append(payload)
			if action["status_dependent"]:
				status_actions.append(payload)
		custom_route = _custom_route_for_doctype(row.name)
		field_rows = [dict(item) for item in docfields.get(row.name, [])]
		field_rows.extend(
			{
				"parent": item.dt, "fieldname": item.fieldname, "label": item.label, "fieldtype": item.fieldtype,
				"options": item.get("options"), "reqd": item.get("reqd", 0), "read_only": item.get("read_only", 0),
				"hidden": item.get("hidden", 0), "permlevel": item.get("permlevel", 0), "custom": True,
			}
			for item in custom_fields_by_dt.get(row.name, [])
		)
		child_tables = [
			{"fieldname": item.get("fieldname"), "label": item.get("label"), "child_doctype": item.get("options"), "required": bool(cint(item.get("reqd")))}
			for item in field_rows if item.get("fieldtype") in {"Table", "Table MultiSelect"}
		]
		field_links = [
			{"fieldname": item.get("fieldname"), "target": item.get("options"), "dynamic": item.get("fieldtype") == "Dynamic Link"}
			for item in field_rows if item.get("fieldtype") in {"Link", "Dynamic Link"}
		]
		dashboard_link_rows = [dict(item) for item in doctype_links.get(row.name, [])]
		completion = "Not implemented"
		test_status = "Not tested"
		remaining = "Required for ordinary-user parity"
		if custom_route:
			if row.name in {"Customer", "Item", "Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry"}:
				completion = "Handcrafted Retail ERP workflow implemented within documented scope"
				test_status = "Automated API, lifecycle and frontend regression tests"
				remaining = "Feature-specific advanced actions and complete interactive role/browser matrix remain"
			else:
				completion = "Generated provisional list/detail/form and allowlisted action coverage"
				test_status = "Priority route, permission and adapter regression tests"
				remaining = "Per-feature transaction, collaboration and interactive browser graduation remains"
		feature = _base_feature(
			feature_id=_feature_id(application, "child_doctype" if cint(row.get("istable")) else "doctype", row.name),
			application=application,
			module=row.module,
			feature_type="child_doctype" if cint(row.get("istable")) else "doctype",
			name=row.name,
			doctype=row.name,
			parent_feature=None,
			child_doctype=row.name if cint(row.get("istable")) else None,
			route=None if cint(row.get("istable")) else f"/app/{_slug(row.name)}",
			source_location=_source_locations(row.name, catalog, "doctypes"),
			standard_desk_route=None if cint(row.get("istable")) else f"/app/{_slug(row.name)}",
			standard_list_route=None if cint(row.get("istable")) or cint(row.get("issingle")) else f"/app/{_slug(row.name)}",
			standard_form_route=None if cint(row.get("istable")) else f"/app/{_slug(row.name)}/{{name}}",
			current_custom_route=custom_route,
			relevant_roles=sorted({item.get("role") for item in perm_rows if item.get("role")}),
			doctype_permissions=perm_rows,
			active_workflow={
				"name": workflow.name,
				"state_field": workflow.get("workflow_state_field"),
				"states": [dict(item) for item in workflow_states.get(workflow.name, [])],
				"transitions": [dict(item) for item in workflow_transitions.get(workflow.name, [])],
			} if workflow else None,
			supported_views=_doctype_views(row, source, calendar_doctypes, kanban_doctypes, dashboard_doctypes),
			metadata={
				"custom": bool(cint(row.get("custom"))), "is_submittable": bool(cint(row.get("is_submittable"))),
				"is_tree": bool(cint(row.get("is_tree"))), "is_single": bool(cint(row.get("issingle"))),
				"is_virtual": bool(cint(row.get("is_virtual"))), "editable_grid": bool(cint(row.get("editable_grid"))),
				"track_changes": bool(cint(row.get("track_changes"))), "naming_rule": row.get("autoname"),
				"title_field": row.get("title_field"), "image_field": row.get("image_field"),
				"search_fields": row.get("search_fields"), "default_view": row.get("default_view"),
			},
			fields=field_rows, child_tables=child_tables, links=field_links + dashboard_link_rows,
			controller_class=_controller_classes(source, package_paths),
			mapped_actions=mapped_actions,
			actions=mapped_actions,
			related_documents=dashboard_links.get(row.name, []),
			status_dependent_actions=status_actions,
			customizations=_customizations_for(row.name, snapshot),
			implementation_type=implementation_type,
			classification=classification,
			user_facing=user_facing,
			exclusion_reason=exclusion,
			test_status=test_status,
			completion_status=completion,
			remaining_desk_dependency=remaining if user_facing else "None: excluded from independent frontend routing",
			notes=[
				f"custom={bool(cint(row.get('custom')))}", f"submittable={bool(cint(row.get('is_submittable')))}",
				f"single={bool(cint(row.get('issingle')))}", f"virtual={bool(cint(row.get('is_virtual')))}",
				f"tree={bool(cint(row.get('is_tree')))}", f"track_changes={bool(cint(row.get('track_changes')))}",
				f"naming={row.get('autoname') or ''}", f"title_field={row.get('title_field') or ''}",
				f"image_field={row.get('image_field') or ''}", f"search_fields={row.get('search_fields') or ''}",
				f"fields={len(docfields.get(row.name, []))}",
			],
			**capabilities,
		)
		features.append(feature)
		feature_by_doctype[row.name] = feature

	for row in snapshot["doctypes"]:
		if not cint(row.get("istable")):
			continue
		parents = sorted(
			{field.parent for field in snapshot["docfields"] if field.parent and field.fieldtype == "Table" and field.options == row.name}
		)
		feature = feature_by_doctype.get(row.name)
		if feature:
			feature["parent_feature"] = [_feature_id(feature_by_doctype[parent]["application"], "doctype", parent) for parent in parents if parent in feature_by_doctype]
			feature["notes"].append(f"parent_doctypes={','.join(parents)}")

	for row in snapshot["reports"]:
		source = catalog["reports"].get(row.name)
		application = source["app"] if source else module_app.get(row.module, "unknown")
		disabled = bool(cint(row.get("disabled")))
		custom_route = _custom_route_for_report(row.name) if not disabled else None
		roles = _roles_for_parent("Report", row.name)
		source_metadata = _report_source_metadata(source, package_paths)
		feature = _base_feature(
			feature_id=_feature_id(application, "report", row.name), application=application, module=row.module,
			feature_type="report", name=row.name, report=row.name, parent_feature=row.get("ref_doctype"),
			route=f"/app/query-report/{row.name}", standard_desk_route=f"/app/query-report/{row.name}",
			current_custom_route=custom_route,
			source_location=_source_locations(row.name, catalog, "reports"), relevant_roles=roles,
			report_permissions=roles, supported_views=[row.get("report_type") or "Report"],
			metadata={
				"report_type": row.get("report_type"), "reference_doctype": row.get("ref_doctype"),
				"prepared_report": bool(cint(row.get("prepared_report"))), "disabled": disabled,
				"add_total_row": bool(cint(row.get("add_total_row"))), "has_chart": source_metadata["has_chart"],
				"has_totals": source_metadata["has_totals"] or bool(cint(row.get("add_total_row"))),
				"source_files": source_metadata["files"],
				"source_filter_fieldnames": source_metadata["filter_fieldnames"],
				"source_column_fieldnames": source_metadata["column_fieldnames"],
			},
			fields=[dict(item) for item in report_columns.get(row.name, [])],
			links=[dict(item) for item in report_filters.get(row.name, [])],
			read=not disabled, export=not disabled, print=not disabled, pdf=not disabled,
			implementation_type="Report engine", classification="D", user_facing=not disabled,
			exclusion_reason="Report is disabled on this site" if disabled else None,
			test_status="Priority report permission and execution adapter tests" if custom_route else "Not tested",
			completion_status="Permission-aware report viewer provisional" if custom_route else "Not implemented",
			remaining_desk_dependency=("Interactive filter/chart/PDF verification remains" if custom_route else "Required: no Retail ERP report adapter") if not disabled else "None while disabled",
			notes=[f"type={row.get('report_type')}", f"reference_doctype={row.get('ref_doctype') or ''}",
				f"prepared_report={bool(cint(row.get('prepared_report')))}", f"total_row={bool(cint(row.get('add_total_row')))}",
				f"has_filters={bool(row.get('filters'))}", f"has_columns={bool(row.get('columns'))}"],
		)
		features.append(feature)

	database_reports = {row.name for row in snapshot["reports"]}
	for name, source in sorted(catalog["reports"].items()):
		if name in database_reports:
			continue
		data = source["data"]
		features.append(_base_feature(
			feature_id=_feature_id(source["app"], "source_only_report", name), application=source["app"],
			module=data.get("module") or "", feature_type="source_only_report", name=name, report=name,
			parent_feature=data.get("ref_doctype"), source_location=[f"{source['app']}:{source['source']}"],
			supported_views=[data.get("report_type") or "Report"], implementation_type="Report engine", classification="D",
			user_facing=False, exclusion_reason="Source-defined Report is absent from the running site database",
			remaining_desk_dependency="None until the Report is installed/enabled on this site",
			notes=["Kept in source reconciliation so upgrades or migrations cannot silently add an unmapped report."],
		))

	for row in snapshot["pages"]:
		name = row.get("page_name") or row.name
		source = catalog["pages"].get(row.name) or catalog["pages"].get(name)
		application = source["app"] if source else module_app.get(row.module, "unknown")
		roles = _roles_for_parent("Page", row.name)
		is_integration = application not in {"frappe", "erpnext", "my_store_ui"}
		classification = "F" if is_integration else ("E" if row.module in ADMIN_MODULES else "C")
		implementation = "Safe embedded integration" if is_integration else ("Administrative interface" if classification == "E" else "Specialized visual view")
		custom_route = "/retail-erp" if name == "retail-erp" else None
		features.append(_base_feature(
			feature_id=_feature_id(application, "page", name), application=application, module=row.module,
			feature_type="page", name=name, page=name, route=f"/app/{name}", standard_desk_route=f"/app/{name}",
			current_custom_route=custom_route, source_location=_source_locations(row.name, catalog, "pages"),
			relevant_roles=roles, page_permissions=roles, supported_views=["Page"], read=True,
			implementation_type=implementation, classification=classification, user_facing=True,
			completion_status="SPA shell implemented; feature coverage partial" if name == "retail-erp" else "Not implemented",
			test_status="Shell route tests" if name == "retail-erp" else "Not tested",
			remaining_desk_dependency="Partial modules remain" if name == "retail-erp" else "Required or safe integration route must be designed",
		))

	for row in snapshot["workspaces"]:
		source = catalog["workspaces"].get(row.name)
		application = source["app"] if source else row.get("app") or module_app.get(row.module, "unknown")
		hidden = bool(cint(row.get("is_hidden")))
		workspace_id = _feature_id(application, "workspace", row.name)
		features.append(_base_feature(
			feature_id=workspace_id, application=application, module=row.module, feature_type="workspace",
			name=row.name, route=f"/app/{_slug(row.name)}", source_location=_source_locations(row.name, catalog, "workspaces"),
			standard_desk_route=f"/app/{_slug(row.name)}", supported_views=["Dashboard", "Workspace"], read=not hidden,
			implementation_type="Specialized visual view", classification="C", user_facing=not hidden,
			exclusion_reason="Workspace hidden on this site" if hidden else None,
			remaining_desk_dependency="Workspace targets require Retail ERP launchers/routes" if not hidden else "None while hidden",
			notes=[f"public={bool(cint(row.get('public')))}", f"for_user={row.get('for_user') or ''}", f"domain={row.get('restrict_to_domain') or ''}"],
		))
		for target in _workspace_targets(row, snapshot):
			target_name = str(target["target"])
			target_type = str(target["type"])
			features.append(_base_feature(
				feature_id=_feature_id(application, "workspace_target", f"{target_type}-{target_name}", row.name), application=application,
				module=row.module, feature_type="workspace_target", name=target.get("label") or target_name,
				parent_feature=workspace_id, tool=target_type, route=None, standard_desk_route=None,
				implementation_type="Specialized visual view", classification="C", user_facing=not hidden,
				exclusion_reason="Parent Workspace hidden" if hidden else None, read=not hidden,
				remaining_desk_dependency="Target must resolve to a classified Retail ERP feature",
				notes=[f"target_type={target_type}", f"target={target_name}"],
			))

	for row in snapshot["workflows"]:
		active = bool(cint(row.get("is_active")))
		application = module_app.get(row.get("module"), "custom")
		features.append(_base_feature(
			feature_id=_feature_id(application, "workflow", row.name), application=application, module=row.get("module") or "Workflow",
			feature_type="workflow", name=row.name, parent_feature=row.get("document_type"),
			standard_desk_route=f"/app/workflow/{_slug(row.name)}", relevant_roles=sorted({item.allowed for item in workflow_transitions.get(row.name, []) if item.get('allowed')}),
			supported_views=["Workflow"], read=active, write=active, implementation_type="Administrative interface",
			classification="E", user_facing=active, exclusion_reason="Workflow inactive" if not active else None,
			status_dependent_actions=[dict(item) for item in workflow_transitions.get(row.name, [])],
			remaining_desk_dependency="Active workflow transitions require custom document integration" if active else "None while inactive",
			notes=[f"document_type={row.get('document_type')}", f"states={len(workflow_states.get(row.name, []))}", f"transitions={len(workflow_transitions.get(row.name, []))}"],
		))

	for row in snapshot["print_formats"]:
		disabled = bool(cint(row.get("disabled")))
		application = module_app.get(row.get("module"), "custom" if cint(row.get("custom_format")) else "unknown")
		features.append(_base_feature(
			feature_id=_feature_id(application, "print_format", row.name, row.get("doc_type")), application=application,
			module=row.get("module") or "Printing", feature_type="print_format", name=row.name,
			parent_feature=row.get("doc_type"), standard_desk_route=f"/app/print-format/{_slug(row.name)}",
			supported_views=["Print", "PDF"], read=not disabled, print=not disabled, pdf=not disabled,
			implementation_type="Administrative interface", classification="E", user_facing=not disabled,
			exclusion_reason="Print Format disabled" if disabled else None,
			remaining_desk_dependency="Print preview/PDF selector not implemented" if not disabled else "None while disabled",
			notes=[f"doctype={row.get('doc_type')}", f"standard={bool(cint(row.get('standard')))}", f"type={row.get('print_format_type') or ''}"],
		))

	for action in _deduplicate_actions(all_actions):
		features.append(_base_feature(
			feature_id=_feature_id(action["app"], "document_action", action["action"], action["parent"]),
			application=action["app"], module=feature_by_doctype.get(action["parent"], {}).get("module", ""),
			feature_type="document_action", name=action["label"], parent_feature=action["parent"],
			source_location=action["sources"], mapped_actions=[{"action": action["action"], "label": action["label"]}],
			status_dependent_actions=[action["label"]] if action["status_dependent"] else [],
			read=True, write=True, implementation_type="Specialized transaction interface", classification="B",
			user_facing=True, remaining_desk_dependency="Action not implemented in Retail ERP",
			notes=["Source-discovered action; inputs, target mapping and state conditions require controller-level verification"],
		))

	features.extend(_customization_features(snapshot, module_app, feature_by_doctype, catalog))
	features.extend(_visual_features(snapshot, module_app, catalog))
	features.extend(_communication_features(snapshot, module_app))
	features.extend(_installed_app_features(installed_apps, catalog))
	features.extend(_platform_capabilities())
	features = sorted(features, key=lambda item: item["feature_id"])
	legacy_rows = _legacy_matrix_rows(matrix_text)
	for feature in features:
		feature["represented_in_previous_matrix"] = _legacy_represents(feature, legacy_rows)
	by_feature_type = {}
	for feature_type in sorted({item["feature_type"] for item in features}):
		items = [item for item in features if item["feature_type"] == feature_type]
		by_feature_type[feature_type] = {
			"total": len(items),
			"represented": sum(item["represented_in_previous_matrix"] for item in items),
			"missing_user_facing": sum(item["user_facing"] and not item["represented_in_previous_matrix"] for item in items),
			"excluded": sum(not item["user_facing"] for item in items),
		}
	duplicates = _legacy_duplicates(legacy_rows)
	reconciliation = {
		"user_supplied_previous_row_count": 98,
		"observed_previous_row_count": len(legacy_rows),
		"represented_feature_ids": [item["feature_id"] for item in features if item["represented_in_previous_matrix"]],
		"missing_feature_ids": [item["feature_id"] for item in features if item["user_facing"] and not item["represented_in_previous_matrix"]],
		"duplicate_legacy_rows": duplicates,
		"by_feature_type": by_feature_type,
	}
	return features, reconciliation


def _roles_for_parent(parenttype: str, parent: str) -> list[str]:
	if not frappe.db.exists("DocType", "Has Role"):
		return []
	return sorted(set(frappe.get_all("Has Role", filters={"parenttype": parenttype, "parent": parent}, pluck="role")))


def _deduplicate_actions(actions: list[dict]) -> list[dict]:
	result = {}
	for action in actions:
		key = (action["app"], action["parent"], action["action"])
		entry = result.setdefault(key, {**action, "sources": [], "status_dependent": False})
		entry["sources"].append(f"{action['app']}:{action['source']}")
		entry["status_dependent"] = entry["status_dependent"] or action["status_dependent"]
	for entry in result.values():
		entry["sources"] = sorted(set(entry["sources"]))
	return sorted(result.values(), key=lambda item: (item["app"], item["parent"], item["action"]))


def _customization_features(snapshot: dict, module_app: dict, feature_by_doctype: dict, catalog: dict) -> list[dict]:
	features = []
	collections = (
		("custom_field", "Custom Field", snapshot["custom_fields"], "dt"),
		("property_setter", "Property Setter", snapshot["property_setters"], "doc_type"),
		("client_script", "Client Script", snapshot["client_scripts"], "dt"),
		("server_script", "Server Script", snapshot["server_scripts"], "reference_doctype"),
		("custom_docperm", "Custom DocPerm", snapshot["custom_docperms"], "parent"),
	)
	for feature_type, label, rows, parent_field in collections:
		for row in rows:
			parent = row.get(parent_field)
			parent_feature = feature_by_doctype.get(parent)
			application = catalog["customization_owners"].get((label, row.name), "custom")
			features.append(_base_feature(
				feature_id=_feature_id(application, feature_type, row.name, parent), application=application,
				module=parent_feature.get("module", "Custom") if parent_feature else "Custom", feature_type=feature_type,
				name=row.name, parent_feature=parent, standard_desk_route=f"/app/{_slug(label)}/{_slug(row.name)}",
				read=True, write=True, implementation_type="Administrative interface", classification="E", user_facing=True,
				remaining_desk_dependency="Customization must be represented by approved Retail ERP schema/administration",
				notes=[f"customization_type={label}"],
			))
	return features


def _visual_features(snapshot: dict, module_app: dict, catalog: dict) -> list[dict]:
	features = []
	collections = (
		("dashboard", snapshot["dashboards"], "Dashboard"),
		("dashboard_chart", snapshot["dashboard_charts"], "Chart"),
		("number_card", snapshot["number_cards"], "Dashboard"),
		("calendar_view", snapshot["calendar_views"], "Calendar"),
		("kanban_board", snapshot["kanban_boards"], "Kanban"),
	)
	for feature_type, rows, view in collections:
		for row in rows:
			module = row.get("module") or "Desk"
			features.append(_base_feature(
				feature_id=_feature_id(module_app.get(module, "custom"), feature_type, row.name),
				application=module_app.get(module, "custom"), module=module, feature_type=feature_type, name=row.name,
				parent_feature=row.get("reference_doctype") or row.get("document_type") or row.get("report_name"),
				standard_desk_route=f"/app/{_slug(row.name)}", supported_views=[view], read=True,
				implementation_type="Specialized visual view", classification="C", user_facing=True,
				remaining_desk_dependency=f"{view} view not implemented in Retail ERP",
			))
	for parent, entries in catalog["dashboards"].items():
		for entry in entries:
			features.append(_base_feature(
				feature_id=_feature_id(entry["app"], "dashboard_connection", parent, entry["source"]),
				application=entry["app"], module="", feature_type="dashboard_connection", name=f"{parent} Dashboard",
				parent_feature=parent, source_location=[f"{entry['app']}:{entry['source']}"], supported_views=["Dashboard"],
				read=True, implementation_type="Specialized visual view", classification="C", user_facing=True,
				remaining_desk_dependency="Dashboard connections and related-document actions require Retail ERP detail integration",
			))
	return features


def _communication_features(snapshot: dict, module_app: dict) -> list[dict]:
	features = []
	for row in snapshot["notification"]:
		enabled = bool(cint(row.get("enabled")))
		application = module_app.get(row.get("module"), "custom")
		features.append(_base_feature(
			feature_id=_feature_id(application, "notification", row.name, row.get("document_type")),
			application=application, module=row.get("module") or "Email", feature_type="notification", name=row.name,
			parent_feature=row.get("document_type"), standard_desk_route=f"/app/notification/{_slug(row.name)}",
			read=enabled, write=enabled, email=enabled, implementation_type="Administrative interface", classification="E",
			user_facing=enabled, exclusion_reason="Notification disabled" if not enabled else None,
			remaining_desk_dependency="Notification configuration and document event behavior require parity" if enabled else "None while disabled",
			notes=[f"event={row.get('event') or ''}", f"channel={row.get('channel') or ''}"],
		))
	for row in snapshot["auto_email_reports"]:
		enabled = bool(cint(row.get("enabled")))
		features.append(_base_feature(
			feature_id=_feature_id("frappe", "auto_email_report", row.name, row.get("report")), application="frappe",
			module="Email", feature_type="auto_email_report", name=row.name, parent_feature=row.get("report"),
			standard_desk_route=f"/app/auto-email-report/{_slug(row.name)}", read=enabled, write=enabled, email=enabled,
			implementation_type="Administrative interface", classification="E", user_facing=enabled,
			exclusion_reason="Auto Email Report disabled" if not enabled else None,
			remaining_desk_dependency="Scheduled report email configuration requires Retail ERP administration" if enabled else "None while disabled",
		))
	return features


def _installed_app_features(installed_apps: list[str], catalog: dict) -> list[dict]:
	features = []
	for app in installed_apps:
		is_integration = app not in {"frappe", "erpnext", "my_store_ui"}
		classification = "F" if is_integration else "E"
		implementation = "Safe embedded integration" if is_integration else "Administrative interface"
		features.append(_base_feature(
			feature_id=_feature_id(app, "installed_app", app), application=app, module=app,
			feature_type="installed_app", name=app, source_location=[catalog["hooks"].get(app, {}).get("source")]
			if catalog["hooks"].get(app, {}).get("source") else [],
			current_custom_route="/retail-erp" if app == "my_store_ui" else None,
			read=True, implementation_type=implementation, classification=classification, user_facing=True,
			completion_status="SPA shell implemented; app feature parity incomplete" if app == "my_store_ui" else "Not implemented",
			remaining_desk_dependency="Installed app capabilities require classified Retail ERP routes or safe embedding",
			notes=[f"modules={','.join(sorted(catalog['modules'].get(app, [])))}", f"hook_names={','.join(catalog['hooks'].get(app, {}).get('declared_names', []))}"],
		))
	return features


def _platform_capabilities() -> list[dict]:
	capabilities = (
		("Data Import", "/app/data-import", "E"), ("Data Export", "/app/data-export", "E"),
		("Bulk Update", None, "E"), ("Bulk Rename", "/app/rename-tool", "E"),
		("Document Print Preview", "/app/print", "E"), ("PDF Download", None, "E"),
		("Document Email", None, "E"), ("Document Sharing", None, "E"),
		("Assignments", None, "A"), ("Comments", None, "A"), ("Attachments", None, "A"),
		("Tags", None, "A"), ("Likes and Follows", None, "A"), ("Version History", None, "A"),
		("List Export", None, "A"), ("List Bulk Actions", None, "A"),
	)
	return [
		_base_feature(
			feature_id=_feature_id("frappe", "platform_capability", name), application="frappe", module="Desk",
			feature_type="platform_capability", name=name, standard_desk_route=route, supported_views=["Tool"],
			read=True, write=True, implementation_type="Administrative interface" if classification == "E" else "Generic list/detail/form engine",
			classification=classification, user_facing=True,
			remaining_desk_dependency="Shared platform capability is not fully implemented in Retail ERP",
			notes=["Source-backed generic Frappe capability; applicability must be evaluated per DocType and permission"],
		)
		for name, route, classification in capabilities
	]


def _legacy_duplicates(rows: list[list[str]]) -> list[dict]:
	seen = defaultdict(list)
	for index, row in enumerate(rows, start=1):
		key = "|".join(cell.lower() for cell in row[:4])
		seen[key].append(index)
	return [{"key": key, "row_indexes": indexes} for key, indexes in sorted(seen.items()) if len(indexes) > 1]


def _installed_app_metadata(installed_apps: list[str], package_paths: dict[str, Path], repo_paths: dict[str, Path], catalog: dict, installed_records: list[frappe._dict]) -> list[dict]:
	metadata = []
	records_by_app = {row.app_name: dict(row) for row in installed_records if row.get("app_name")}
	for app in installed_apps:
		repo = repo_paths.get(app)
		package = package_paths.get(app)
		commit = None
		if repo and (repo / ".git").exists():
			try:
				import subprocess
				commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
			except Exception:
				commit = None
		metadata.append({
			"application": app, "package_path": str(package) if package else None,
			"repository_path": str(repo) if repo else None, "git_commit": commit,
			"installed_application_record": records_by_app.get(app),
			"modules": sorted(catalog["modules"].get(app, [])), "hooks": catalog["hooks"].get(app, {}),
			"source_counts": dict(catalog["source_counts"].get(app, {})),
		})
	return metadata


def _counts(installed_apps: list[str], snapshot: dict, features: list[dict], reconciliation: dict) -> dict:
	feature_type_counts = Counter(item["feature_type"] for item in features)
	classification_counts = Counter(item["classification"] for item in features)
	return {
		"installed_applications": len(installed_apps),
		"modules": len(snapshot["modules"]),
		"parent_doctypes": sum(not cint(row.get("istable")) for row in snapshot["doctypes"]),
		"child_doctypes": sum(cint(row.get("istable")) for row in snapshot["doctypes"]),
		"custom_doctypes": sum(cint(row.get("custom")) for row in snapshot["doctypes"]),
		"reports": len(snapshot["reports"]), "pages": len(snapshot["pages"]),
		"workspaces": len(snapshot["workspaces"]),
		"dashboards": feature_type_counts["dashboard"] + feature_type_counts["dashboard_chart"] + feature_type_counts["number_card"] + feature_type_counts["dashboard_connection"],
		"active_workflows": sum(cint(row.get("is_active")) for row in snapshot["workflows"]),
		"print_formats": len(snapshot["print_formats"]), "client_scripts": len(snapshot["client_scripts"]),
		"server_scripts": len(snapshot["server_scripts"]), "custom_fields": len(snapshot["custom_fields"]),
		"property_setters": len(snapshot["property_setters"]),
		"document_mappings_and_actions": feature_type_counts["document_action"],
		"user_facing_features": sum(item["user_facing"] for item in features),
		"system_internal_exclusions": sum(not item["user_facing"] for item in features),
		"previous_matrix_rows_user_supplied": reconciliation["user_supplied_previous_row_count"],
		"previous_matrix_rows_observed": reconciliation["observed_previous_row_count"],
		"missing_features_added": len(reconciliation["missing_feature_ids"]),
		"duplicate_rows_detected": len(reconciliation["duplicate_legacy_rows"]),
		"specialized_interfaces": classification_counts["B"] + classification_counts["C"],
		"generic_engine_features": classification_counts["A"],
		"installed_app_features": sum(item["application"] not in {"frappe", "erpnext", "my_store_ui", "custom", "unknown"} for item in features),
		"remaining_desk_dependencies": sum(item["user_facing"] and item["remaining_desk_dependency"] not in {None, "None"} for item in features),
		"unclassified_features": sum(not item.get("classification") for item in features),
		"features_total": len(features),
		"feature_type_counts": dict(sorted(feature_type_counts.items())),
		"classification_counts": dict(sorted(classification_counts.items())),
	}


def _audit_result(features: list[dict]) -> dict:
	unclassified = [item["feature_id"] for item in features if not item.get("classification")]
	unmapped = [item["feature_id"] for item in features if item["user_facing"] and not item.get("current_custom_route")]
	undocumented_actions = [item["feature_id"] for item in features if item["feature_type"] == "document_action" and not item.get("mapped_actions")]
	untested_complete = [item["feature_id"] for item in features if item["completion_status"].lower().startswith("complete") and item["test_status"] == "Not tested"]
	unresolved_workflows = [item["feature_id"] for item in features if item["feature_type"] == "workflow" and item["user_facing"] and not item.get("current_custom_route")]
	failures = {
		"unclassified_user_facing": [item for item in unclassified if next(feature for feature in features if feature["feature_id"] == item)["user_facing"]],
		"unmapped_user_facing": unmapped,
		"undocumented_actions": undocumented_actions,
		"complete_without_tests": untested_complete,
		"unhandled_active_workflows": unresolved_workflows,
	}
	return {"status": "fail" if any(failures.values()) else "pass", "failure_counts": {key: len(value) for key, value in failures.items()}, "failures": failures}


def _fingerprint(features: list[dict]) -> str:
	payload = json.dumps(features, sort_keys=True, separators=(",", ":"), default=str).encode()
	return hashlib.sha256(payload).hexdigest()


def _markdown_inventory(inventory: dict) -> str:
	counts = inventory["counts"]
	lines = [
		"# ERPNext v15 complete installed feature inventory", "",
		"> Machine-generated from `site1.local` database metadata and installed source. Do not edit generated tables manually.", "",
		f"Inventory fingerprint: `{inventory['inventory_fingerprint']}`", "",
		"## Coverage summary", "",
		"| Metric | Count |", "|---|---:|",
	]
	for key, value in counts.items():
		if isinstance(value, int):
			lines.append(f"| {key.replace('_', ' ').title()} | {value} |")
	lines.extend(["", "## Feature records", "", "| Feature ID | App | Module | Type | Name | Class | User-facing | Custom route | Completion | Desk dependency |", "|---|---|---|---|---|---|---|---|---|---|"])
	for item in inventory["features"]:
		lines.append(
			f"| `{item['feature_id']}` | {item['application']} | {item['module']} | {item['feature_type']} | "
			f"{str(item['name']).replace('|', '/')} | {item['classification']} | {'Yes' if item['user_facing'] else 'No'} | "
			f"{item.get('current_custom_route') or '—'} | {item['completion_status']} | {item['remaining_desk_dependency'] or '—'} |"
		)
	return "\n".join(lines) + "\n"


def _audit_summary_markdown(inventory: dict) -> str:
	counts = inventory["counts"]
	audit = inventory["automated_audit"]
	recon = inventory["reconciliation"]
	lines = [
		"# Feature audit summary", "",
		"This audit is a discovery baseline, not a parity claim. The automated parity check currently fails until every permitted user-facing feature has a tested Retail ERP implementation or an evidence-backed exclusion.", "",
		"## Required totals", "", "| Metric | Count |", "|---|---:|",
	]
	ordered = [
		"installed_applications", "modules", "parent_doctypes", "child_doctypes", "custom_doctypes", "reports", "pages", "workspaces", "dashboards", "active_workflows", "print_formats", "client_scripts", "server_scripts", "custom_fields", "property_setters", "document_mappings_and_actions", "user_facing_features", "system_internal_exclusions", "previous_matrix_rows_user_supplied", "previous_matrix_rows_observed", "missing_features_added", "duplicate_rows_detected", "specialized_interfaces", "generic_engine_features", "installed_app_features", "remaining_desk_dependencies", "unclassified_features", "features_total",
	]
	for key in ordered:
		lines.append(f"| {key.replace('_', ' ').title()} | {counts[key]} |")
	lines.extend([
		"", "## Automated parity audit", "", f"Result: **{audit['status'].upper()}**", "",
		"| Failure class | Count |", "|---|---:|",
	])
	for key, value in audit["failure_counts"].items():
		lines.append(f"| {key.replace('_', ' ').title()} | {value} |")
	lines.extend([
		"", "## Reconciliation", "",
		f"- User-supplied previous matrix count: **{recon['user_supplied_previous_row_count']}**.",
		f"- Observed hand-authored rows before generation: **{recon['observed_previous_row_count']}**.",
		f"- Machine-discovered user-facing features not represented by the hand-authored matrix: **{len(recon['missing_feature_ids'])}**.",
		f"- Exact duplicate legacy rows detected: **{len(recon['duplicate_legacy_rows'])}**.",
		"- Existing manual rows were preserved. The generated appendix is canonical for completeness checks.",
		"", "### Representation by discovered feature type", "", "| Feature type | Total | Already represented | Missing user-facing | Excluded |", "|---|---:|---:|---:|---:|",
	])
	for feature_type, result in recon["by_feature_type"].items():
		lines.append(f"| {feature_type.replace('_', ' ').title()} | {result['total']} | {result['represented']} | {result['missing_user_facing']} | {result['excluded']} |")
	lines.extend([
		"", "### Implementation classification", "", "| Class | Meaning | Count |", "|---|---|---:|",
	])
	classification_labels = {
		"A": "Generic list/detail/form engine", "B": "Specialized transaction interface", "C": "Specialized visual view",
		"D": "Report engine", "E": "Administrative interface", "F": "Safe embedded integration", "G": "System-internal and not user-facing",
	}
	for code in "ABCDEFG":
		lines.append(f"| {code} | {classification_labels[code]} | {counts['classification_counts'].get(code, 0)} |")
	from my_store_ui.services.priority_registry import ENTITY_ROUTES, FORM_VARIANTS, REPORT_GROUPS, SPECIAL_ROUTES
	priority_reports = {report for reports in REPORT_GROUPS.values() for report in reports}
	lines.extend([
		"", "## Priority page expansion (2026-07-13)", "",
		f"- Clean priority entity bases registered: **{len(ENTITY_ROUTES)}**.",
		f"- Purpose-specific transaction forms registered: **{len(FORM_VARIANTS)}**.",
		f"- Special/read/alias routes registered: **{len(SPECIAL_ROUTES)}**.",
		f"- Priority report names allowlisted: **{len(priority_reports)}** across **{len(REPORT_GROUPS)}** groups.",
		"- Existing handcrafted Customer, Item, Sales Order, Delivery Note, Sales Invoice and Payment Entry routes retain priority.",
		"- Generated transactions and specialised tools remain provisional; a route does not count as full workflow parity.",
		"- Detailed route classifications and limitations are in `docs/priority-page-coverage.md`.",
	])
	lines.extend([
		"", "## Rerun commands", "",
		"```bash", "bench --site site1.local execute my_store_ui.audit.feature_inventory.generate_complete_inventory", "bench --site site1.local execute my_store_ui.audit.feature_inventory.audit_feature_parity", "```",
		"", "The first command refreshes all generated documents. The second intentionally exits non-zero until the parity contract is met.",
		"", "## Discovery limitations requiring implementation-time review", "",
		"- Source action discovery identifies whitelisted controller actions and custom buttons, but complex runtime conditions and dynamically constructed buttons still require controller-specific review.",
		"- Disabled/domain-restricted features remain inventoried; their runtime visibility depends on current user permissions, domains, module profiles and settings.",
		"- Child DocTypes are classified as non-independent routes, not discarded; they remain attached to parent form requirements.",
		"- Workspace blocks are resolved from stored content where target metadata is explicit. Unresolved blocks remain in the unmapped report.",
	])
	return "\n".join(lines) + "\n"


def _unmapped_markdown(inventory: dict) -> str:
	features = [item for item in inventory["features"] if item["user_facing"] and not item.get("current_custom_route")]
	lines = [
		"# Unmapped Retail ERP features", "",
		f"Total user-facing features without a registered custom route: **{len(features)}**.", "",
		"The priority page sprint registers clean routes for important daily DocTypes and selected reports. Generated transactions and specialised tools remain provisional even when their parent DocType is no longer counted as route-unmapped; unresolved actions, views, dashboards, customisations and per-feature tests remain listed below.", "",
		"| Feature ID | App | Module | Type | Name | Classification | Standard route | Dependency |", "|---|---|---|---|---|---|---|---|",
	]
	for item in features:
		lines.append(
			f"| `{item['feature_id']}` | {item['application']} | {item['module']} | {item['feature_type']} | "
			f"{str(item['name']).replace('|', '/')} | {item['classification']} | {item.get('standard_desk_route') or '—'} | {item['remaining_desk_dependency']} |"
		)
	return "\n".join(lines) + "\n"


def _matrix_appendix(inventory: dict) -> str:
	lines = [
		GENERATED_START, "", "## Machine-generated installed feature coverage", "",
		"> Generated by `my_store_ui.audit.feature_inventory.generate_complete_inventory`. The JSON inventory is canonical. Existing roadmap rows above are retained for historical planning context.", "",
		"| Feature ID | App | Module | Type | Name | Classification | User-facing | Custom route | Test status | Completion | Desk dependency |", "|---|---|---|---|---|---|---|---|---|---|---|",
	]
	for item in inventory["features"]:
		lines.append(
			f"| `{item['feature_id']}` | {item['application']} | {item['module']} | {item['feature_type']} | "
			f"{str(item['name']).replace('|', '/')} | {item['classification']} | {'Yes' if item['user_facing'] else 'No'} | "
			f"{item.get('current_custom_route') or '—'} | {item['test_status']} | {item['completion_status']} | {item['remaining_desk_dependency'] or '—'} |"
		)
	lines.extend(["", GENERATED_END, ""])
	return "\n".join(lines)


def _write_outputs(repo_path: Path, inventory: dict, original_matrix: str) -> None:
	docs = repo_path / "docs"
	docs.mkdir(parents=True, exist_ok=True)
	(docs / "erpnext-v15-complete-inventory.json").write_text(
		json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
	)
	(docs / "erpnext-v15-complete-inventory.md").write_text(_markdown_inventory(inventory), encoding="utf-8")
	(docs / "feature-audit-summary.md").write_text(_audit_summary_markdown(inventory), encoding="utf-8")
	(docs / "unmapped-features.md").write_text(_unmapped_markdown(inventory), encoding="utf-8")
	base = original_matrix.split(GENERATED_START, 1)[0].rstrip() + "\n\n"
	(docs / "frontend-feature-matrix.md").write_text(base + _matrix_appendix(inventory), encoding="utf-8")


def build_complete_inventory() -> dict:
	if frappe.session.user == "Guest":
		frappe.throw("Authentication is required for the feature audit.", frappe.AuthenticationError)
	installed_apps = list(frappe.get_installed_apps())
	package_paths, repo_paths = _app_paths(installed_apps)
	catalog = _source_catalog(installed_apps, package_paths)
	for name, entry in catalog["doctypes"].items():
		entry["package"] = package_paths.get(entry["app"])
	snapshot = _collect_database_snapshot()
	repo_path = repo_paths["my_store_ui"]
	matrix_path = repo_path / "docs" / "frontend-feature-matrix.md"
	matrix_text = matrix_path.read_text(encoding="utf-8")
	features, reconciliation = _build_features(installed_apps, package_paths, catalog, snapshot, matrix_text)
	counts = _counts(installed_apps, snapshot, features, reconciliation)
	counts["new_matrix_rows"] = reconciliation["observed_previous_row_count"] + len(features)
	inventory = {
		"schema_version": SCHEMA_VERSION,
		"site": frappe.local.site,
		"applications": _installed_app_metadata(installed_apps, package_paths, repo_paths, catalog, snapshot["installed_application_records"]),
		"counts": counts,
		"reconciliation": reconciliation,
		"features": features,
		"customization_summary": {
			"custom_fields": [dict(row) for row in snapshot["custom_fields"]],
			"property_setters": [dict(row) for row in snapshot["property_setters"]],
			"client_scripts": [{key: value for key, value in dict(row).items() if key != "script"} for row in snapshot["client_scripts"]],
			"server_scripts": [{key: value for key, value in dict(row).items() if key != "script"} for row in snapshot["server_scripts"]],
			"custom_docperms": [dict(row) for row in snapshot["custom_docperms"]],
			"custom_roles": [dict(row) for row in snapshot["roles"] if cint(row.get("is_custom"))],
		},
	}
	inventory["automated_audit"] = _audit_result(features)
	inventory["inventory_fingerprint"] = _fingerprint(features)
	return _json_value(inventory)


def generate_complete_inventory() -> dict:
	"""Generate repository documentation from read-only site/source inspection."""
	inventory = build_complete_inventory()
	repo_path = Path(frappe.get_app_path("my_store_ui")).resolve().parent
	matrix_path = repo_path / "docs" / "frontend-feature-matrix.md"
	_write_outputs(repo_path, inventory, matrix_path.read_text(encoding="utf-8"))
	return {
		"inventory_fingerprint": inventory["inventory_fingerprint"],
		"counts": inventory["counts"],
		"audit": inventory["automated_audit"]["failure_counts"],
		"status": inventory["automated_audit"]["status"],
	}


def audit_feature_parity(strict: int = 1) -> dict:
	"""Rebuild the read-only inventory and fail when parity contract gaps remain."""
	inventory = build_complete_inventory()
	result = inventory["automated_audit"]
	if cint(strict) and result["status"] != "pass":
		frappe.throw(
			"Retail ERP feature parity audit failed: "
			+ ", ".join(f"{key}={value}" for key, value in result["failure_counts"].items()),
			frappe.ValidationError,
		)
	return result
