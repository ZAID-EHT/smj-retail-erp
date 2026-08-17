"""Authentication bootstrap and route authorization for standalone Retail ERP."""

from __future__ import annotations

import frappe
from frappe import _

from my_store_ui.services.frontend_routes import get_permitted_navigation, resolve_frontend_route, route_is_permitted


def _role_path_allowed(path: str) -> bool:
	from my_store_ui.role_pages import path_is_allowed_for_user
	return path_is_allowed_for_user(path)


ROLE_LANDINGS = (
	("Administrator", "/retail-erp/home"),
	("System Manager", "/retail-erp/home"),
	("Sales Manager", "/retail-erp/smart-sales"),
	("Sales User", "/retail-erp/smart-sales"),
	("POS Manager", "/retail-erp/smart-sales"),
	("POS User", "/retail-erp/smart-sales"),
	("Stock Manager", "/retail-erp/inventory"),
	("Stock User", "/retail-erp/inventory"),
	("Purchase Manager", "/retail-erp/purchases"),
	("Purchase User", "/retail-erp/purchases"),
	("Accounts Manager", "/retail-erp/finance"),
	("Accounts User", "/retail-erp/finance"),
)


def get_landing_route() -> str:
	if frappe.session.user == "Guest":
		return "/"
	roles = set(frappe.get_roles())
	if frappe.session.user == "Administrator":
		roles.add("Administrator")
	for role, route in ROLE_LANDINGS:
		if role in roles:
			definition, _params = resolve_frontend_route(route)
			if definition and route_is_permitted(definition) and _role_path_allowed(route):
				return route
	for module in get_permitted_navigation():
		if module.get("path"):
			return f"/retail-erp{module['path']}"
	return "/retail-erp/permission-denied"


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_session_bootstrap():
	if frappe.session.user == "Guest":
		return {"authenticated": False}

	user = frappe.get_cached_value("User", frappe.session.user, ["full_name", "user_image"], as_dict=True) or {}
	company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")
	csrf_token = frappe.session.data.get("csrf_token")
	if not csrf_token and hasattr(frappe.local, "session_obj"):
		csrf_token = frappe.sessions.get_csrf_token()
	return {
		"authenticated": True,
		"user": frappe.session.user,
		"display_name": user.get("full_name") or frappe.session.user,
		"user_image": user.get("user_image"),
		"company": company,
		"roles": frappe.get_roles(),
		"landing_route": get_landing_route(),
		"navigation": get_permitted_navigation(),
		"csrf_token": csrf_token,
		"allow_emergency_standard_desk": False,
	}


@frappe.whitelist(methods=["GET"])
def authorize_frontend_route(path: str):
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	definition, _params = resolve_frontend_route(path)
	if not definition:
		return {"outcome": "not_found", "route": "/retail-erp/not-found"}
	if not definition.get("implemented"):
		return {"outcome": "unavailable", "route": "/retail-erp/feature-unavailable"}
	if not route_is_permitted(definition) or not _role_path_allowed(path):
		frappe.logger("my_store_ui.security").warning({"event": "frontend_route_denied", "user": frappe.session.user, "feature_id": definition["feature_id"]})
		return {"outcome": "denied", "route": "/retail-erp/permission-denied"}
	return {"outcome": "allowed", "route_name": definition["name"], "feature_id": definition["feature_id"]}
