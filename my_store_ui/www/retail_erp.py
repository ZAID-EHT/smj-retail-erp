from __future__ import annotations

import json
from pathlib import Path

import frappe


no_cache = 1


def _asset_context() -> tuple[str, str, str]:
	root = Path(frappe.get_app_path("my_store_ui", "public", "frontend"))
	manifest_path = root / ".vite" / "manifest.json"
	if manifest_path.exists():
		manifest = json.loads(manifest_path.read_text())
		entry = manifest.get("src/main.js") or next((item for item in manifest.values() if item.get("isEntry")), {})
		javascript = entry.get("file")
		styles = (entry.get("css") or [manifest.get("style.css", {}).get("file")])[0]
		if javascript and styles:
			version = Path(javascript).stem.rsplit("-", 1)[-1]
			return (
				f"/assets/my_store_ui/frontend/{javascript}",
				f"/assets/my_store_ui/frontend/{styles}",
				version,
			)
	return (
		"/assets/my_store_ui/frontend/retail-erp.js",
		"/assets/my_store_ui/frontend/retail-erp.css",
		frappe.utils.get_build_version(),
	)


SMJ_LOGO = "/assets/my_store_ui/images/smj-logo.png"

# The browser tab text, sitting next to the favicon.
APP_TITLE = "SMJ ERP"


def get_context(context):
	javascript, stylesheet, version = _asset_context()
	company = frappe.defaults.get_global_default("company")
	company_logo = frappe.db.get_value("Company", company, "company_logo") if company else None
	context.no_cache = 1
	context.title = APP_TITLE
	context.retail_javascript = javascript
	context.retail_stylesheet = stylesheet
	context.retail_asset_version = version
	context.retail_brand = company or frappe.get_website_settings("app_name") or "Retail ERP"
	# A company that has uploaded its own logo keeps it; otherwise the SMJ mark is
	# the brand, not the generic product placeholder that used to fall through here
	# and leave the shell showing a stock house icon.
	context.retail_logo = company_logo or SMJ_LOGO
	context.retail_bootstrap = {
		"basePath": "/retail-erp/",
		"brand": context.retail_brand,
		"logo": context.retail_logo,
		"assetVersion": version,
	}
	return context
