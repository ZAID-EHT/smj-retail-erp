"""Scoped browser-route guard. API, asset, file and integration traffic is untouched."""

from __future__ import annotations

from urllib.parse import quote

import frappe
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect

from my_store_ui.standalone import get_landing_route


DESK_ROUTE_MAP = {
	"customer": "/retail-erp/sales/customers",
	"item": "/retail-erp/inventory/products",
	"sales-order": "/retail-erp/sales/orders",
	"delivery-note": "/retail-erp/sales/delivery-notes",
	"sales-invoice": "/retail-erp/sales/invoices",
	"payment-entry": "/retail-erp/finance/payments",
}


class RetailERPRedirect(HTTPException):
	"""A non-cacheable browser redirect that can safely escape before_request."""

	code = 302

	def __init__(self, location: str):
		super().__init__()
		self.location = location

	def get_response(self, environ=None, scope=None):
		response = redirect(self.location, code=self.code)
		response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
		return response


def _is_browser_html_get() -> bool:
	request = getattr(frappe.local, "request", None)
	if not request or request.method != "GET":
		return False
	if request.headers.get("X-Requested-With") == "XMLHttpRequest":
		return False
	accept = request.headers.get("Accept", "")
	return not accept or "text/html" in accept


def _mapped_desk_route(path: str) -> str:
	if path in {"/app", "/app/", "/app/home"}:
		return get_landing_route()
	if path.startswith("/app/retail-erp"):
		suffix = path[len("/app/retail-erp"):]
		return f"/retail-erp{suffix or '/home'}"
	parts = [part for part in path.removeprefix("/app/").split("/") if part]
	if parts and parts[0] in DESK_ROUTE_MAP:
		base = DESK_ROUTE_MAP[parts[0]]
		if len(parts) > 1:
			return f"{base}/{quote(parts[1], safe='')}"
		return base
	feature = quote((parts[0] if parts else "ERPNext feature").replace("-", " ")[:80])
	return f"/retail-erp/feature-unavailable?feature={feature}"


def before_request():
	request = getattr(frappe.local, "request", None)
	if not request:
		return
	path = request.path.rstrip("/") or "/"
	if path == "/":
		# This request-local flag takes precedence over Role and Portal home-page
		# settings without writing any site configuration or database record.
		frappe.local.flags.home_page = "retail_erp"
		return
	if not path.startswith("/app") or not _is_browser_html_get():
		return
	# Emergency Desk is disabled by default. Enabling it requires an explicit
	# site configuration change and still permits Administrator only.
	if frappe.conf.get("allow_emergency_standard_desk") and frappe.session.user == "Administrator" and request.args.get("retail_emergency") == "1":
		frappe.logger("my_store_ui.security").warning("Administrator activated emergency Standard Desk access")
		return
	raise RetailERPRedirect(_mapped_desk_route(path))
