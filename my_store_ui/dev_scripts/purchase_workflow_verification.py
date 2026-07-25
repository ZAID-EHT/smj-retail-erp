"""Phase 5 — Purchase Order data audit + end-to-end purchasing verification (staging-only).

Two independent entry points:

  bench --site staging.local execute my_store_ui.dev_scripts.purchase_workflow_verification.audit
  bench --site staging.local execute my_store_ui.dev_scripts.purchase_workflow_verification.run

`audit()` is read-only. It compares the required Purchase Order surface against the
*installed* ERPNext v15 metadata and against what the universal engine actually
exposes (`_readable_fields` / `_writable_fields`), so nothing is guessed.

`run()` drives the whole purchasing chain through standard ERPNext controllers:
  Material Request -> Request for Quotation -> Supplier Quotation -> Purchase Order
  -> Purchase Receipt (partial, then remainder) -> Purchase Invoice (partial billing)
  -> Payment Entry (advance + partial) -> Purchase Return -> Debit Note
  -> Landed Cost Voucher -> Goods In Transit
No Stock Ledger / GL / Payment Ledger / Bin row is ever written directly.

Everything created is tracked and removed by `cleanup()` unless `keep=True`.
"""

from __future__ import annotations

import frappe
from frappe.utils import add_days, flt, nowdate

from my_store_ui.universal.api import (
	MAPPED_ACTIONS,
	_permlevels,
	_readable_fields,
	_writable_fields,
)

COMPANY = "SMJ Retail ERP"
WAREHOUSE = "Main Warehouse - SMJ"
TRANSIT_WAREHOUSE = "Goods In Transit - SMJ"
ITEM = "SMJ-PURCHASE-TEST-ITEM"
SUPPLIER = "SMJ Purchase Test Supplier"


# ---------------------------------------------------------------------------
# Required surface (from the Phase 5 requirement list). Fieldnames are the real
# ERPNext v15 ones; `audit()` reports anything the installed metadata does not
# have rather than assuming these are correct.
# ---------------------------------------------------------------------------

PO_HEADER_REQUIRED = {
	"supplier": "Supplier",
	"supplier_name": "Supplier name",
	"company": "Company",
	"currency": "Currency",
	"conversion_rate": "Conversion rate",
	"buying_price_list": "Buying Price List",
	"price_list_currency": "Price List currency",
	"plc_conversion_rate": "Price List conversion rate",
	"transaction_date": "Transaction date",
	"schedule_date": "Required-by / schedule date",
	"supplier_address": "Supplier address",
	"contact_person": "Supplier contact",
	"shipping_address": "Shipping address",
	"billing_address": "Billing address",
	"project": "Project",
	"cost_center": "Cost Center",
	"payment_terms_template": "Payment Terms",
	"payment_schedule": "Payment schedule",
	"taxes_and_charges": "Taxes and Charges template",
	"taxes": "Taxes table",
	"tc_name": "Terms template",
	"terms": "Terms and conditions",
	"apply_tds": "Apply tax withholding",
	"status": "Status",
}

# Supplier Group and the source-document links are fetched/held per row rather
# than on the PO header in v15; audited where they really live.
PO_HEADER_FETCHED = {"supplier_group": "Supplier Group"}

PO_ITEM_REQUIRED = {
	"item_code": "Item Code",
	"item_name": "Item Name",
	"description": "Description",
	"qty": "Quantity",
	"stock_uom": "Stock UOM",
	"uom": "Purchase UOM",
	"conversion_factor": "Conversion factor",
	"rate": "Rate",
	"price_list_rate": "Price List rate",
	"discount_percentage": "Discount %",
	"discount_amount": "Discount amount",
	"warehouse": "Warehouse",
	"schedule_date": "Schedule date",
	"expense_account": "Expense account",
	"cost_center": "Cost Center",
	"project": "Project",
	"item_tax_template": "Tax template",
	"amount": "Amount",
	"base_amount": "Base amount",
	"received_qty": "Received quantity",
	"billed_amt": "Billed amount",
	"stock_qty": "Stock quantity",
	"material_request": "Material Request link",
	"material_request_item": "Material Request row link",
	"supplier_quotation": "Supplier Quotation link",
	"supplier_quotation_item": "Supplier Quotation row link",
}

PO_TOTALS_REQUIRED = {
	"total_qty": "Total quantity",
	"net_total": "Net total",
	"base_net_total": "Base net total",
	"total_taxes_and_charges": "Taxes",
	"base_total_taxes_and_charges": "Base taxes",
	"apply_discount_on": "Additional discount on",
	"additional_discount_percentage": "Additional discount %",
	"discount_amount": "Additional discount amount",
	"grand_total": "Grand total",
	"base_grand_total": "Base grand total",
	"rounding_adjustment": "Rounding adjustment",
	"rounded_total": "Rounded total",
	"base_rounded_total": "Base rounded total",
	"advance_paid": "Advance paid",
	"per_received": "% received",
	"per_billed": "% billed",
}

# Every purchasing mapping the requirement calls for, as (source, action key).
REQUIRED_MAPPINGS = (
	("Material Request", "make_request_for_quotation"),
	("Material Request", "make_supplier_quotation"),
	("Material Request", "make_purchase_order"),
	("Request for Quotation", "make_supplier_quotation"),
	("Supplier Quotation", "make_purchase_order"),
	("Supplier Quotation", "make_purchase_invoice"),
	("Purchase Order", "make_purchase_receipt"),
	("Purchase Order", "make_purchase_invoice"),
	("Purchase Order", "payment"),
	("Purchase Receipt", "make_purchase_invoice"),
	("Purchase Receipt", "make_purchase_return"),
	("Purchase Receipt", "make_lcv"),
	("Purchase Invoice", "make_payment_entry"),
	("Purchase Invoice", "make_debit_note"),
)


def _exposure(doctype: str, parent_doctype: str | None = None) -> tuple[dict, set[str], set[str]]:
	"""Readable/writable fieldnames exactly as the universal engine computes them.

	Child DocTypes carry no DocPerm rows of their own, so `_field_definition`
	resolves a child table's permlevel access from its **parent**. The audit must
	use the same model or every child field looks unexposed.
	"""
	meta = frappe.get_meta(doctype)
	levels_source = frappe.get_meta(parent_doctype) if parent_doctype else meta
	read_levels = _permlevels(levels_source, "read")
	write_levels = _permlevels(levels_source, "write")
	readable = {field.fieldname for field in _readable_fields(meta, read_levels)}
	writable = {field.fieldname for field in _writable_fields(meta, write_levels)}
	return meta, readable, writable


def _audit_group(title: str, doctype: str, required: dict, parent_doctype: str | None = None) -> dict:
	meta, readable, writable = _exposure(doctype, parent_doctype)
	rows, missing, not_readable = [], [], []
	for fieldname, label in required.items():
		field = meta.get_field(fieldname)
		if not field:
			missing.append(fieldname)
			rows.append({"fieldname": fieldname, "requirement": label, "present": False})
			continue
		if fieldname not in readable:
			not_readable.append(fieldname)
		rows.append({
			"fieldname": fieldname, "requirement": label, "present": True,
			"fieldtype": field.fieldtype, "label": field.label,
			"reqd": bool(field.reqd), "read_only": bool(field.read_only), "hidden": bool(field.hidden),
			"readable": fieldname in readable, "writable": fieldname in writable,
		})
	print(f"\n--- {title} ({doctype}) — {len(rows)} required fields ---")
	for row in rows:
		if not row["present"]:
			print(f"  MISSING   {row['fieldname']:<32} ({row['requirement']})")
			continue
		flags = "".join((
			"R" if row["readable"] else "-",
			"W" if row["writable"] else "-",
			"*" if row["reqd"] else " ",
		))
		print(f"  [{flags}] {row['fieldname']:<32} {row['fieldtype']:<16} {row['label']}")
	print(f"  => missing: {missing or 'none'}")
	print(f"  => present but not exposed for read: {not_readable or 'none'}")
	return {"doctype": doctype, "rows": rows, "missing": missing, "not_readable": not_readable}


def _audit_lifecycle() -> dict:
	meta = frappe.get_meta("Purchase Order")
	result = {
		"is_submittable": bool(meta.is_submittable),
		"allow_amend": bool(meta.is_submittable),
		"allow_copy": not bool(meta.get("allow_copy")),
		"print_formats": frappe.get_all("Print Format", filters={"doc_type": "Purchase Order", "disabled": 0}, pluck="name"),
		"active_workflow": frappe.db.get_value("Workflow", {"document_type": "Purchase Order", "is_active": 1}, "name"),
	}
	print("\n--- Lifecycle ---")
	for key, value in result.items():
		print(f"  {key}: {value}")
	return result


def _audit_mappings() -> dict:
	print("\n--- Mappings registered in MAPPED_ACTIONS ---")
	present, missing = [], []
	for source, action in REQUIRED_MAPPINGS:
		mapping = MAPPED_ACTIONS.get(source, {}).get(action)
		if mapping:
			present.append((source, action, mapping["target"], mapping["method"]))
			print(f"  OK      {source:<22} {action:<42} -> {mapping['target']}")
		else:
			missing.append((source, action))
			print(f"  MISSING {source:<22} {action}")
	print(f"  => missing mappings: {missing or 'none'}")
	return {"present": present, "missing": missing}


def audit() -> dict:
	"""Read-only Purchase Order field / lifecycle / mapping audit."""
	frappe.set_user("Administrator")
	print("=" * 78)
	print("PURCHASE ORDER DATA AUDIT — installed ERPNext v15 metadata vs universal engine")
	print("=" * 78)
	result = {
		"header": _audit_group("Header & supplier information", "Purchase Order", PO_HEADER_REQUIRED),
		"item": _audit_group("Item table", "Purchase Order Item", PO_ITEM_REQUIRED, parent_doctype="Purchase Order"),
		"totals": _audit_group("Totals", "Purchase Order", PO_TOTALS_REQUIRED),
		"fetched": _audit_group("Fetched / related", "Supplier", PO_HEADER_FETCHED),
		"lifecycle": _audit_lifecycle(),
		"mappings": _audit_mappings(),
	}
	gaps = (
		result["header"]["missing"] + result["item"]["missing"] + result["totals"]["missing"]
		+ [f"{s}:{a}" for s, a in result["mappings"]["missing"]]
	)
	print("\n" + "=" * 78)
	print(f"AUDIT RESULT: {'PASS — no gaps' if not gaps else 'GAPS: ' + ', '.join(gaps)}")
	print("=" * 78)
	result["gaps"] = gaps
	return result


# ---------------------------------------------------------------------------
# End-to-end chain
# ---------------------------------------------------------------------------

_created: list[tuple[str, str]] = []


def _track(doc):
	_created.append((doc.doctype, doc.name))
	return doc


def _insert(payload: dict, submit: bool = True):
	doc = frappe.get_doc(payload)
	doc.insert(ignore_permissions=True)
	_track(doc)
	if submit:
		doc.submit()
		doc.reload()
	return doc


def _fixtures() -> None:
	if not frappe.db.exists("Supplier", SUPPLIER):
		_insert({
			"doctype": "Supplier", "supplier_name": SUPPLIER,
			"supplier_group": frappe.get_all("Supplier Group", filters={"is_group": 0}, pluck="name")[0],
			"supplier_type": "Company", "default_currency": "LKR",
		}, submit=False)
	if not frappe.db.exists("Item", ITEM):
		_insert({
			"doctype": "Item", "item_code": ITEM, "item_name": "SMJ Purchase Test Item",
			"item_group": frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0],
			"stock_uom": "Nos", "is_stock_item": 1, "is_purchase_item": 1,
			"item_defaults": [{"company": COMPANY, "default_warehouse": WAREHOUSE}],
		}, submit=False)


def _step(label: str, fn):
	try:
		out = fn()
		print(f"  PASS  {label}: {out}")
		return {"step": label, "status": "PASS", "detail": str(out)}
	except Exception as exc:  # noqa: BLE001 - report, then keep the chain going
		frappe.db.rollback()
		print(f"  FAIL  {label}: {type(exc).__name__}: {exc}")
		return {"step": label, "status": "FAIL", "detail": f"{type(exc).__name__}: {exc}"}


def run(keep: int = 0) -> dict:
	"""Drive the full purchasing chain on staging and report each step."""
	frappe.set_user("Administrator")
	_created.clear()
	results: list[dict] = []
	docs: dict[str, object] = {}
	print("=" * 78)
	print("END-TO-END PURCHASING CHAIN (staging.local)")
	print("=" * 78)
	_fixtures()
	qty, rate = 20.0, 500.0
	schedule = add_days(nowdate(), 7)

	def material_request():
		docs["mr"] = _insert({
			"doctype": "Material Request", "material_request_type": "Purchase",
			"company": COMPANY, "transaction_date": nowdate(), "schedule_date": schedule,
			"items": [{"item_code": ITEM, "qty": qty, "warehouse": WAREHOUSE, "schedule_date": schedule, "uom": "Nos"}],
		})
		return docs["mr"].name

	def rfq():
		from erpnext.stock.doctype.material_request.material_request import make_request_for_quotation
		doc = make_request_for_quotation(docs["mr"].name)
		doc.transaction_date = nowdate()
		doc.schedule_date = schedule
		doc.append("suppliers", {"supplier": SUPPLIER})
		doc.message_for_supplier = "Please quote."
		doc.insert(ignore_permissions=True)
		_track(doc)
		doc.submit()
		docs["rfq"] = doc
		return doc.name

	def supplier_quotation():
		from erpnext.buying.doctype.request_for_quotation.request_for_quotation import (
			make_supplier_quotation_from_rfq,
		)
		doc = make_supplier_quotation_from_rfq(docs["rfq"].name, for_supplier=SUPPLIER)
		for row in doc.items:
			row.rate = rate
		doc.insert(ignore_permissions=True)
		_track(doc)
		doc.submit()
		docs["sq"] = doc
		return f"{doc.name} grand_total={flt(doc.grand_total)}"

	def purchase_order():
		from erpnext.buying.doctype.supplier_quotation.supplier_quotation import make_purchase_order
		doc = make_purchase_order(docs["sq"].name)
		doc.schedule_date = schedule
		for row in doc.items:
			row.schedule_date = schedule
			row.warehouse = WAREHOUSE
		doc.insert(ignore_permissions=True)
		_track(doc)
		doc.submit()
		doc.reload()
		docs["po"] = doc
		linked = doc.items[0].get("material_request") or "-"
		return (f"{doc.name} qty={flt(doc.total_qty)} grand_total={flt(doc.grand_total)} "
			f"sq_link={doc.items[0].get('supplier_quotation')} mr_link={linked}")

	def advance_payment():
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		pe = get_payment_entry("Purchase Order", docs["po"].name, party_amount=2000.0)
		pe.reference_no, pe.reference_date = "SMJ-ADV-1", nowdate()
		pe.insert(ignore_permissions=True)
		_track(pe)
		pe.submit()
		docs["po"].reload()
		return f"{pe.name} advance_paid={flt(docs['po'].advance_paid)}"

	def partial_receipt():
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		pr = make_purchase_receipt(docs["po"].name)
		for row in pr.items:
			row.qty = 12.0
			row.warehouse = WAREHOUSE
		pr.insert(ignore_permissions=True)
		_track(pr)
		pr.submit()
		docs["pr1"] = pr
		docs["po"].reload()
		return f"{pr.name} received=12 per_received={flt(docs['po'].per_received)}%"

	def remaining_receipt():
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		pr = make_purchase_receipt(docs["po"].name)
		for row in pr.items:
			row.warehouse = WAREHOUSE
		pr.insert(ignore_permissions=True)
		_track(pr)
		pr.submit()
		docs["pr2"] = pr
		docs["po"].reload()
		return f"{pr.name} remaining_qty={flt(pr.items[0].qty)} per_received={flt(docs['po'].per_received)}%"

	def partial_billing():
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
		pi = make_purchase_invoice(docs["pr1"].name)
		pi.set_posting_time = 1
		pi.posting_date = nowdate()
		pi.bill_no, pi.bill_date = "SMJ-BILL-1", nowdate()
		pi.insert(ignore_permissions=True)
		_track(pi)
		pi.submit()
		docs["pi"] = pi
		docs["po"].reload()
		return (f"{pi.name} grand_total={flt(pi.grand_total)} outstanding={flt(pi.outstanding_amount)} "
			f"po_per_billed={flt(docs['po'].per_billed)}%")

	def partial_supplier_payment():
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		pe = get_payment_entry("Purchase Invoice", docs["pi"].name)
		half = flt(docs["pi"].outstanding_amount) / 2
		pe.paid_amount = pe.received_amount = half
		for row in pe.references:
			row.allocated_amount = half
		pe.reference_no, pe.reference_date = "SMJ-PAY-1", nowdate()
		pe.insert(ignore_permissions=True)
		_track(pe)
		pe.submit()
		docs["pi"].reload()
		return f"{pe.name} paid={flt(pe.paid_amount)} pi_outstanding={flt(docs['pi'].outstanding_amount)}"

	def purchase_return():
		from erpnext.controllers.sales_and_purchase_return import make_return_doc
		ret = make_return_doc("Purchase Receipt", docs["pr1"].name)
		for row in ret.items:
			row.qty = -2.0
			row.received_qty = -2.0
			row.warehouse = WAREHOUSE
		ret.insert(ignore_permissions=True)
		_track(ret)
		ret.submit()
		docs["ret"] = ret
		return f"{ret.name} is_return={ret.is_return} qty={flt(ret.items[0].qty)}"

	def debit_note():
		from erpnext.controllers.sales_and_purchase_return import make_return_doc
		dn = make_return_doc("Purchase Invoice", docs["pi"].name)
		dn.insert(ignore_permissions=True)
		_track(dn)
		dn.submit()
		return f"{dn.name} is_return={dn.is_return} grand_total={flt(dn.grand_total)}"

	def landed_cost_voucher():
		from erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher import LandedCostVoucher  # noqa: F401
		lcv = frappe.get_doc({
			"doctype": "Landed Cost Voucher", "company": COMPANY, "posting_date": nowdate(),
			"purchase_receipts": [{
				"receipt_document_type": "Purchase Receipt", "receipt_document": docs["pr2"].name,
				"supplier": SUPPLIER, "grand_total": flt(docs["pr2"].grand_total),
			}],
			"taxes": [{
				"description": "Freight", "expense_account": frappe.db.get_value(
					"Company", COMPANY, "default_expense_account"
				) or frappe.get_all("Account", filters={"company": COMPANY, "is_group": 0, "root_type": "Expense"}, pluck="name")[0],
				"amount": 800.0,
			}],
		})
		lcv.get_items_from_purchase_receipts()
		lcv.insert(ignore_permissions=True)
		_track(lcv)
		lcv.submit()
		return f"{lcv.name} applied_charges={flt(lcv.total_taxes_and_charges)}"

	def goods_in_transit():
		se = _insert({
			"doctype": "Stock Entry", "stock_entry_type": "Material Transfer", "company": COMPANY,
			"items": [{
				"item_code": ITEM, "qty": 3.0, "uom": "Nos",
				"s_warehouse": WAREHOUSE, "t_warehouse": TRANSIT_WAREHOUSE,
			}],
		})
		return f"{se.name} transit_qty=3 -> {TRANSIT_WAREHOUSE}"

	def cancellation_and_amendment():
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		po2 = _insert({
			"doctype": "Purchase Order", "supplier": SUPPLIER, "company": COMPANY,
			"transaction_date": nowdate(), "schedule_date": schedule,
			"items": [{"item_code": ITEM, "qty": 5.0, "rate": rate, "warehouse": WAREHOUSE, "schedule_date": schedule, "uom": "Nos"}],
		})
		po2.cancel()
		amended = frappe.copy_doc(po2)
		amended.amended_from = po2.name
		amended.docstatus = 0
		amended.insert(ignore_permissions=True)
		_track(amended)
		amended.submit()
		make_purchase_receipt(amended.name)  # amended doc is mappable
		return f"cancelled={po2.name} amended={amended.name} status={amended.status}"

	for label, fn in (
		("Material Request created", material_request),
		("MR -> Request for Quotation", rfq),
		("RFQ -> Supplier Quotation", supplier_quotation),
		("SQ -> Purchase Order", purchase_order),
		("PO -> Payment Entry (supplier advance)", advance_payment),
		("PO -> Purchase Receipt (partial 12/20)", partial_receipt),
		("PO -> Purchase Receipt (remaining 8/20)", remaining_receipt),
		("PR -> Purchase Invoice (partial billing)", partial_billing),
		("PI -> Payment Entry (partial, outstanding payable)", partial_supplier_payment),
		("PR -> Purchase Return", purchase_return),
		("PI -> Debit Note", debit_note),
		("PR -> Landed Cost Voucher", landed_cost_voucher),
		("Goods In Transit transfer", goods_in_transit),
		("PO cancellation + amendment", cancellation_and_amendment),
	):
		results.append(_step(label, fn))
		frappe.db.commit()

	passed = sum(1 for row in results if row["status"] == "PASS")
	print("\n" + "=" * 78)
	print(f"CHAIN RESULT: {passed}/{len(results)} steps PASS")
	for row in results:
		if row["status"] == "FAIL":
			print(f"  FAILED: {row['step']} -> {row['detail']}")
	print("=" * 78)
	print(f"Documents created ({len(_created)}):")
	for doctype, name in _created:
		print(f"  {doctype}: {name}")

	if not int(keep or 0):
		cleanup()
	return {"steps": results, "passed": passed, "total": len(results), "created": list(_created)}


def cleanup() -> None:
	"""Cancel and delete everything this script created, newest first."""
	print("\n--- cleanup ---")
	for doctype, name in reversed(_created):
		try:
			if not frappe.db.exists(doctype, name):
				continue
			doc = frappe.get_doc(doctype, name)
			if doc.docstatus == 1:
				doc.cancel()
			frappe.delete_doc(doctype, name, force=True, ignore_permissions=True, delete_permanently=True)
			frappe.db.commit()
		except Exception as exc:  # noqa: BLE001 - report and keep cleaning
			frappe.db.rollback()
			print(f"  could not remove {doctype} {name}: {type(exc).__name__}: {exc}")
	for doctype, name in (("Item", ITEM), ("Supplier", SUPPLIER)):
		try:
			if frappe.db.exists(doctype, name):
				frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
				frappe.db.commit()
		except Exception as exc:  # noqa: BLE001
			frappe.db.rollback()
			print(f"  could not remove {doctype} {name}: {type(exc).__name__}: {exc}")
	print("  cleanup done")
