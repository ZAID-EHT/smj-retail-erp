"""Guarded audit + safe-default migration for existing Products and Customers.

Modes: inspect (read-only counts), dry_run (per-record issue list, no writes),
apply (only deterministic safe defaults), verify. Never invents credit values or
BR numbers; never enables batch tracking on a stocked Item (that is a manual
migration); refuses site1.local and unknown sites.
"""

from __future__ import annotations

import frappe
from frappe.model.naming import make_autoname
from frappe.utils import flt

ALLOWED = {"staging.local", "financeqa.local", "freshrelease.local"}
SKU_SERIES = "5.###"
DEFAULT_PRICE_CATEGORY = "Retail Price List"
NON_CREDIT = "Non-Credit Customer"


def _guard():
	if frappe.local.site == "site1.local":
		raise RuntimeError("refusing: site1.local is protected")
	if frappe.local.site not in ALLOWED:
		raise RuntimeError(f"refusing: {frappe.local.site!r} not allowlisted")


def _product_issues() -> list[dict]:
	issues = []
	for it in frappe.get_all("Item", filters={"disabled": 0}, fields=["name", "item_code", "custom_sku", "item_group",
	                         "has_batch_no", "is_stock_item", "custom_product_size", "custom_product_material"],
	                         limit_page_length=0):
		flags = []
		if not it.custom_sku:
			flags.append("missing_sku")
		if not it.item_group:
			flags.append("missing_category")
		if not it.custom_product_size:
			flags.append("missing_size")
		if not it.custom_product_material:
			flags.append("missing_material")
		if it.is_stock_item and not it.has_batch_no:
			flags.append("not_batch_managed")  # manual migration only
		# duplicate item prices (same item/list/uom, no party)
		dup = frappe.db.sql(
			"""SELECT price_list, COUNT(*) c FROM `tabItem Price`
			   WHERE item_code=%s AND IFNULL(customer,'')='' AND IFNULL(supplier,'')=''
			   GROUP BY price_list, IFNULL(uom,'') HAVING c > 1""", it.name)
		if dup:
			flags.append("duplicate_item_prices")
		if flags:
			issues.append({"item": it.name, "flags": flags})
	return issues


def _customer_issues() -> list[dict]:
	issues = []
	for c in frappe.get_all("Customer", fields=["name", "customer_name", "default_price_list",
	                        "custom_credit_type"], limit_page_length=0):
		flags = []
		if not c.default_price_list:
			flags.append("missing_price_category")
		if not c.custom_credit_type:
			flags.append("missing_payment_type")
		has_contact = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": c.name, "parenttype": "Contact"}, limit_page_length=1)
		has_addr = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": c.name, "parenttype": "Address"}, limit_page_length=1)
		if not has_contact:
			flags.append("missing_contact")
		if not has_addr:
			flags.append("missing_address")
		if flags:
			issues.append({"customer": c.name, "flags": flags})
	return issues


def _outstanding(customer) -> float:
	try:
		from erpnext.selling.doctype.customer.customer import get_customer_outstanding
		company = frappe.defaults.get_global_default("company")
		return flt(get_customer_outstanding(customer, company)) if company else 0.0
	except Exception:
		return 0.0


def inspect() -> dict:
	_guard()
	frappe.set_user("Administrator")
	prod = _product_issues()
	cust = _customer_issues()
	result = {
		"mode": "inspect", "site": frappe.local.site,
		"products_total": frappe.db.count("Item", {"disabled": 0}),
		"products_with_issues": len(prod),
		"customers_total": frappe.db.count("Customer"),
		"customers_with_issues": len(cust),
	}
	print(frappe.as_json(result))
	return result


def dry_run() -> dict:
	_guard()
	frappe.set_user("Administrator")
	prod = _product_issues()
	cust = _customer_issues()
	safe = {"product_sku": [], "customer_price_category": [], "customer_payment_type": []}
	manual = {"product_not_batch_managed": [], "product_duplicate_prices": [],
	          "customer_missing_contact": [], "customer_missing_address": []}
	for p in prod:
		if "missing_sku" in p["flags"]:
			safe["product_sku"].append(p["item"])
		if "not_batch_managed" in p["flags"]:
			manual["product_not_batch_managed"].append(p["item"])
		if "duplicate_item_prices" in p["flags"]:
			manual["product_duplicate_prices"].append(p["item"])
	for c in cust:
		if "missing_price_category" in c["flags"]:
			safe["customer_price_category"].append(c["customer"])
		if "missing_payment_type" in c["flags"] and _outstanding(c["customer"]) <= 0:
			safe["customer_payment_type"].append(c["customer"])
		if "missing_contact" in c["flags"]:
			manual["customer_missing_contact"].append(c["customer"])
		if "missing_address" in c["flags"]:
			manual["customer_missing_address"].append(c["customer"])
	result = {"mode": "dry_run", "safe_defaults": {k: len(v) for k, v in safe.items()},
	          "manual_review": {k: len(v) for k, v in manual.items()},
	          "safe_detail": safe, "manual_detail": manual}
	print(frappe.as_json(result))
	return result


def apply() -> dict:
	"""Apply ONLY deterministic safe defaults. Never batch-enables stocked items."""
	_guard()
	frappe.set_user("Administrator")
	plan = dry_run()
	applied = {"sku": 0, "price_category": 0, "payment_type": 0}
	for item in plan["safe_detail"]["product_sku"]:
		if not frappe.db.get_value("Item", item, "custom_sku"):
			frappe.db.set_value("Item", item, "custom_sku", make_autoname(SKU_SERIES))
			applied["sku"] += 1
	for cust in plan["safe_detail"]["customer_price_category"]:
		if not frappe.db.get_value("Customer", cust, "default_price_list"):
			frappe.db.set_value("Customer", cust, "default_price_list", DEFAULT_PRICE_CATEGORY)
			applied["price_category"] += 1
	for cust in plan["safe_detail"]["customer_payment_type"]:
		if not frappe.db.get_value("Customer", cust, "custom_credit_type") and _outstanding(cust) <= 0:
			frappe.db.set_value("Customer", cust, "custom_credit_type", NON_CREDIT)
			applied["payment_type"] += 1
	frappe.db.commit()
	result = {"mode": "apply", "applied": applied, "note": "batch tracking and missing contacts/addresses are manual"}
	print(frappe.as_json(result))
	return result


def verify() -> dict:
	_guard()
	frappe.set_user("Administrator")
	remaining = dry_run()
	print(frappe.as_json({"mode": "verify", "remaining_safe": remaining["safe_defaults"]}))
	return remaining
