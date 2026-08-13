"""Permission-aware APIs for the metadata-driven Retail ERP foundation.

Only features explicitly classified by ``universal.registry`` can reach these
methods.  Frappe documents and controllers remain authoritative for reads,
writes, validation, workflows and document state transitions.
"""

from __future__ import annotations

import json
import shutil
from copy import deepcopy
from typing import Any
from urllib.parse import quote, urlencode

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate

from my_store_ui.universal.registry import (
	ALL_GENERATED_DOCTYPES,
	SUPPORTED_FIELD_TYPES,
	feature_is_permitted,
	get_feature,
	get_generated_feature,
	get_registry_records,
)


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_LINK_RESULTS = 20
LINK_RESULT_LIMITS = {"Role": 100, "Role Profile": 100}
MAX_TIMELINE_ROWS = 30
SAFE_FILTER_OPERATORS = {"=", "!=", ">", ">=", "<", "<=", "like", "not like", "in", "not in", "between", "is"}
LAYOUT_FIELDS = {"Section Break", "Column Break", "Tab Break"}
NUMERIC_FIELDS = {"Currency", "Float", "Int", "Percent", "Duration", "Rating"}

# Frappe's Desk User form hides the raw roles table and replaces it with its
# JavaScript RoleEditor. Vue never executes Desk client scripts, so this one
# server-owned adapter exposes only that table to authorised user managers.
# "enabled" is read-only in Desk (toggled by Desk JS); we re-expose it so user
# managers can deactivate/reactivate accounts. Frappe's own User.validate still
# blocks disabling Administrator or the last System Manager.
# Role Profile has the identical shape -- its "roles" table is read_only+hidden
# behind a "roles_html" RoleEditor widget -- so without this a Role Profile could
# be created but never given any roles.
SPECIAL_WRITABLE_FIELDS = {
	"User": {"roles", "enabled"},
	"Role Profile": {"roles"},
}

# Privileged, doctype-scoped fields surfaced as write-only inputs on the form:
# accepted on create/update but never read back into detail views. "new_password"
# lets a user manager set or reset a login password directly (essential when no
# outgoing email account is configured to deliver welcome/reset links).
WRITE_ONLY_INPUT_FIELDS = {"User": ("new_password",)}

# SMJ imports and resells finished goods; it manufactures nothing and
# subcontracts nothing. ERPNext ships the buying documents with the production
# fields inline anyway -- BOM, exploded items, finished-good item, WIP composite
# asset, subcontracting -- and on a 60-column item row they are pure noise that
# invites a wrong entry.
#
# Removed from every surface (add form, edit form, detail view) rather than only
# from the add form: a field nobody in this business should ever fill has no
# reason to reappear the moment a document is reopened. They stay on the DocType,
# so ERPNext's own controllers are untouched and a future subcontracting build
# only has to delete lines from here.
# "supplied_items" is the raw material a subcontractor is issued against a
# subcontracted order. It is always empty here and is dropped whole.

# --- Buying item rows -------------------------------------------------
# ERPNext ships ~74 columns on a purchase item row. A buyer here types six
# of them (item, qty, uom, rate, warehouse, and occasionally a discount);
# everything below is either a value the controller recomputes on every
# save, a mirror of the same number in company currency (LKR is the company
# currency, so the mirror is always identical), or a workflow this business
# does not run. Dropping them from the form does not change a single posted
# figure -- the controller still calculates and stores them.
# A second pass, after seeing a real invoice being typed. What a buyer actually
# decides on a line is: which product, how many, what price, where it goes.
# Everything here is either fetched from the Item master and shown back at them,
# or a total the controller computes, or a link only a mapper ever fills.
_BUYING_ROW_FETCHED = frozenset({
	# Fetched from the Item and displayed read-back: the Item link already
	# identifies the product, and the description is a paragraph of catalogue
	# text taking a third of the row.
	"item_name", "description",
	# Purchase UOM: every correct row in this site's history bought the item in
	# its own stock UOM. Leaving the field editable let "Carton" be picked for an
	# item with no Carton conversion defined, which silently records 200 cartons
	# as 200 pieces. Without the field, qty always means stock units.
	"uom",
	# Pricing scaffolding. The buyer types the Rate they are paying; the list
	# price and the two discount fields only ever restate it, and Discount Amount
	# cannot even be typed (the controller recomputes it from the percentage).
	"price_list_rate", "discount_percentage", "discount_amount",
	# No Item carries a tax template; VAT comes from the document-level Purchase
	# Taxes and Charges table.
	"item_tax_template",
	# update_stock is forced on, so the controller always posts to the warehouse's
	# stock account. There is nothing left to choose.
	"expense_account",
	# Serial and batch: no Item on this site is serial-tracked, and batch
	# tracking is off. These three only ever sat empty.
	"serial_and_batch_bundle", "use_serial_batch_fields", "batch_no",
	# Filled by the mapper when an invoice is raised from an order or receipt,
	# never typed. The Linked Documents panel already shows the relationship.
	"purchase_order", "purchase_receipt", "purchase_invoice",
})

_BUYING_ROW_NOISE = frozenset({
	# Company-currency mirrors of the field right above them.
	"base_price_list_rate", "base_rate", "base_amount", "base_net_rate", "base_net_amount",
	"base_rate_with_margin",
	# Selling-style margin machinery on a buying document.
	"margin_type", "margin_rate_or_amount", "rate_with_margin", "distributed_discount_amount",
	"pricing_rules", "stock_uom_rate",
	# Net-of-tax figures the controller derives from rate and the tax table.
	"net_rate", "net_amount",
	# UOM conversion: every item is bought in its own stock UOM (0 rows in
	# this site's history use a conversion factor other than 1), so these
	# three always read 1 / the stock UOM / the same qty again.
	"conversion_factor", "stock_uom", "stock_qty",
	# Rejected-goods flow: never used here; damaged stock goes back through
	# a Purchase Return. Without a rejected qty, received qty always equals
	# accepted qty.
	"received_qty", "rejected_qty", "rejected_warehouse",
	"rejected_serial_and_batch_bundle", "rejected_serial_no",
	# No item on this site uses serial numbers.
	"serial_no",
	# Read-only copies of Item-master data, shown on the product page.
	"product_bundle", "brand", "item_group", "image",
	# Costing internals recomputed on submit.
	"valuation_rate", "sales_incoming_rate", "item_tax_amount",
	"landed_cost_voucher_amount", "rm_supp_cost", "item_tax_rate",
	# No Item is flagged as a fixed asset.
	"is_fixed_asset", "asset_location", "asset_category",
	# No Item uses deferred expense recognition.
	"deferred_expense_account", "enable_deferred_expense",
	"service_start_date", "service_end_date", "service_stop_date",
	# India-only tax withholding; the company country is Sri Lanka.
	"apply_tds",
	# Drop-shipping and internal transfers are not part of this trade.
	"delivered_by_supplier", "from_warehouse",
	# Shipping weight lives on the Item, not on every invoice line.
	"weight_per_unit", "total_weight", "weight_uom",
	# One cost centre, no projects.
	"project", "cost_center",
	# Free-goods handling: never used.
	"is_free_item", "allow_zero_valuation_rate",
	# Print layout control.
	"page_break",
	# Internal row-id back-references. The human-readable parent links
	# (purchase_order / purchase_receipt) are deliberately kept.
	"po_detail", "pr_detail", "purchase_invoice_item", "sales_invoice_item",
	"purchase_receipt_item", "purchase_order_item",
})

OUT_OF_CONTEXT_FIELDS = {
	# "raw_material_details" / "raw_materials_supplied" are the section headers that
	# wrapped the table above; without them the form would show an empty heading.
	"Purchase Order": {
		"is_subcontracted", "is_old_subcontracting_flow", "set_reserve_warehouse",
		"supplied_items", "raw_material_details",
	},
	"Purchase Receipt": {
		"is_subcontracted", "is_old_subcontracting_flow", "subcontracting_receipt",
		"supplied_items", "raw_material_details",
	},
	"Purchase Invoice": {
		"is_subcontracted", "is_old_subcontracting_flow", "supplied_items",
		"raw_materials_supplied",
		# Always on, enforced by my_store_ui.purchase_stock.force_update_stock.
		# A checkbox that cannot be changed only invites someone to try.
		"update_stock",
	},
	"Purchase Order Item": _BUYING_ROW_NOISE | _BUYING_ROW_FETCHED | {
		"bom", "include_exploded_items", "production_plan", "production_plan_item",
		"production_plan_sub_assembly_item", "fg_item", "fg_item_qty",
		"subcontracted_quantity", "wip_composite_asset", "manufacturer", "manufacturer_part_no",
		"against_blanket_order", "blanket_order", "blanket_order_rate", "quality_inspection",
		# Buying starts at the Purchase Order here, so the upstream request and
		# quotation links can never be populated.
		"material_request", "material_request_item", "supplier_quotation", "supplier_quotation_item",
		# Drop-ship links (supplier ships straight to the customer) and derived
		# progress figures.
		"sales_order", "sales_order_item", "sales_order_packed_item", "returned_qty", "billed_amt",
	},
	"Purchase Receipt Item": _BUYING_ROW_NOISE | _BUYING_ROW_FETCHED | {
		"bom", "include_exploded_items", "wip_composite_asset", "subcontracting_receipt_item",
		"manufacturer", "manufacturer_part_no", "quality_inspection",
		"against_blanket_order", "blanket_order", "blanket_order_rate",
		"material_request", "material_request_item",
		# Sample retention is a QA practice SMJ does not run; the rest are
		# derived progress figures, drop-ship links, or features not in use
		# (putaway rules, provisional accounting).
		"retain_sample", "sample_quantity", "received_stock_qty", "returned_qty",
		"amount_difference_with_purchase_invoice", "billed_amt",
		"return_qty_from_rejected_warehouse", "delivery_note_item", "putaway_rule",
		"provisional_expense_account", "sales_order", "sales_order_item", "schedule_date",
	},
	"Purchase Invoice Item": _BUYING_ROW_NOISE | _BUYING_ROW_FETCHED | {
		"bom", "include_exploded_items", "wip_composite_asset",
		"manufacturer", "manufacturer_part_no", "quality_inspection",
		"material_request", "material_request_item",
	},
	# --- Purchase tax rows -------------------------------------------------
	# Same story: the company-currency mirrors, the per-row cost centre/project
	# split, the India withholding flag and the POS "paid amount" flag are all
	# noise on a nine-line VAT/duty table. "Reference Row #" goes with the two
	# "On Previous Row" charge types, which are removed from the Type dropdown
	# in RESTRICTED_SELECT_OPTIONS below.
	"Purchase Taxes and Charges": {
		"row_id", "included_in_paid_amount", "is_tax_withholding_account",
		"cost_center", "project", "account_currency",
		"tax_amount_after_discount_amount", "base_tax_amount", "base_total",
		"base_tax_amount_after_discount_amount", "item_wise_tax_detail",
	},
	# --- Selling side: Blanket Order is a committed-price supply agreement SMJ
	# does not trade on, so its three item columns are noise on every quote/order.
	"Sales Order Item": {"against_blanket_order", "blanket_order", "blanket_order_rate"},
	"Quotation Item": {"against_blanket_order", "blanket_order", "blanket_order_rate"},
	# --- Stock Entry: everything below belongs to Manufacture / Repack /
	# Subcontracting purposes, none of which SMJ can select any more.
	"Stock Entry": {
		"work_order", "job_card", "subcontracting_order", "source_stock_entry",
		"bom_info_section", "from_bom", "use_multi_level_bom", "bom_no", "fg_completed_qty",
		"section_break_7qsm", "process_loss_percentage", "process_loss_qty",
	},
	"Stock Entry Detail": {"quality_inspection", "subcontracted_item", "bom_no", "job_card_item"},
	# --- Pick List: "Material Transfer for Manufacture" picking and its
	# finished-good quantity field.
	"Pick List": {"work_order", "for_qty"},
	# --- Serial No records the Work Order that produced the unit; SMJ's serials
	# always arrive from a supplier.
	"Serial No": {"work_order"},
	# --- Company's "Manufacturing" section holds one production-costing account.
	"Company": {"manufacturing_section", "default_operating_cost_account"},
	# --- A Batch of purchased goods is never "produced", so the produce/produced
	# quantities go. manufacturing_date stays (it is the date printed on the
	# goods by the supplier) and is relabelled below.
	"Batch": {"manufacturing_section", "column_break_23", "qty_to_produce", "produced_qty"},
}

# Labels ERPNext writes from a manufacturer's point of view. The field is kept
# because the data is meaningful to a reseller; only the wording changes.
FIELD_LABEL_OVERRIDES = {
	("Company", "stock_tab"): _("Stock"),
	("Batch", "manufacturing_date"): _("Production Date"),
}

# Defaults ERPNext ships that do not match how this business works. Applied to
# the values the add form prefills, so the common case needs no thought.
FIELD_DEFAULT_OVERRIDES = {}

# ERPNext ships production purposes/types inside shared Select fields. Dropping
# the whole field would break the document, so the options are filtered down to
# the ones this business can legitimately choose. Enforced on read (the form
# never offers them) and on write (the API refuses them).
RESTRICTED_SELECT_OPTIONS = {
	("Stock Entry", "purpose"): ("Material Issue", "Material Receipt", "Material Transfer"),
	("Stock Entry Type", "purpose"): ("Material Issue", "Material Receipt", "Material Transfer"),
	("Pick List", "purpose"): ("Material Transfer", "Delivery"),
	("Asset Capitalization", "capitalization_method"): ("Create a new composite asset",),
	# The two "On Previous Row ..." charge types need the Reference Row # column,
	# which is dropped from the tax table above. Every tax row this site has ever
	# posted is "On Net Total".
	("Purchase Taxes and Charges", "charge_type"): ("Actual", "On Net Total", "On Item Quantity"),
}

# Curated "essentials only" field order for the CREATE form of noisy doctypes.
# The full field set is still returned for editing; the frontend applies this
# subset (in order) only when adding a new record, to keep onboarding simple.
SIMPLE_CREATE_FIELDS = {
	"User": ("username", "new_password", "roles", "role_profile_name", "email", "first_name", "last_name", "enabled"),
	# Supplier flows through the universal generated engine, so its curated add
	# form lives here. Customer and Item use the custom entity forms
	# (services/entity_schemas.py + form_schemas.py), which are already curated and
	# sectioned, so they are intentionally not configured here.
	"Supplier": (
		"supplier_name", "supplier_group", "supplier_type", "default_currency", "default_price_list",
		"payment_terms", "tax_id", "tax_category", "image",
	),
	"Role Profile": ("role_profile", "roles"),
	# --- Curated add forms for the documents ACCOUNT CREATION.docx calls out ----
	# Each keeps the business fields the wholesale workflow needs and drops the
	# corporate-level ERPNext fields. Everything omitted still exists on the
	# DocType and remains editable on the detail view; only the ADD form is
	# trimmed, and ERPNext's own defaults fill the rest.
	"Lead": (
		"lead_name", "company_name", "status", "source", "email_id", "mobile_no", "phone",
		"territory", "city", "country", "lead_owner",
	),
	"Quotation": (
		"quotation_to", "party_name", "company", "transaction_date", "valid_till",
		"order_type", "currency", "selling_price_list", "items", "taxes_and_charges",
		"taxes", "tc_name", "terms",
	),
	"Purchase Order": (
		"supplier", "company", "transaction_date", "schedule_date", "currency",
		"buying_price_list", "set_warehouse", "items", "taxes_and_charges", "taxes",
		"payment_terms_template", "tc_name", "terms",
	),
	"Purchase Receipt": (
		"supplier", "company", "posting_date", "set_warehouse", "supplier_delivery_note",
		"currency", "buying_price_list", "items", "taxes_and_charges", "taxes",
	),
	"Purchase Invoice": (
		"supplier", "company", "posting_date", "due_date", "bill_no", "bill_date",
		"currency", "buying_price_list", "set_warehouse", "items",
		"taxes_and_charges", "taxes", "payment_terms_template",
	),
	# Payment Entry is deliberately absent: it is served by the custom entity
	# engine (services/form_schemas.py, key "payment_entries"), which already
	# curates it down to 23 sectioned fields, so an entry here would never be read.
	# Stock Entry is the "Stock Transfer" of the Retail ERP vocabulary.
	"Stock Entry": (
		"stock_entry_type", "company", "posting_date", "from_warehouse", "to_warehouse",
		"items", "remarks",
	),
	"Warehouse": (
		"warehouse_name", "company", "parent_warehouse", "is_group", "warehouse_type",
		"phone_no", "mobile_no", "address_line_1", "city", "state", "pin",
	),
}

# Fields that are mandatory ON THE ADD FORM, overriding the DocType's own reqd
# flags (applied by the frontend only when adding). For User we want username +
# password + role to be the only required inputs; email/first_name are optional
# and synthesised server-side from the username when left blank.
SIMPLE_CREATE_REQUIRED = {
	"User": ("username", "new_password", "roles"),
	# Keep the genuinely ERPNext-required fields required on the add form.
	"Supplier": ("supplier_name", "supplier_group"),
	# A Role Profile with no roles is useless, so require at least the table.
	"Role Profile": ("role_profile", "roles"),
	# Only what ERPNext genuinely needs to save; the rest is optional on the add
	# form and validated by the controller on submit.
	"Lead": ("lead_name",),
	"Quotation": ("quotation_to", "party_name", "company", "transaction_date"),
	"Purchase Order": ("supplier", "company", "transaction_date", "schedule_date"),
	"Purchase Receipt": ("supplier", "company", "posting_date"),
	"Purchase Invoice": ("supplier", "company", "posting_date"),
	"Stock Entry": ("stock_entry_type", "company"),
	"Warehouse": ("warehouse_name", "company"),
}

# Fixed server-owned mappings. The browser sends only these symbolic action
# keys; dotted Python methods are never accepted from a request.
MAPPED_ACTIONS = {
	"Quotation": {
		"make_sales_order": {"label": _("Create Sales Order"), "target": "Sales Order", "method": "quotation_sales_order"},
		"make_sales_invoice": {"label": _("Create Sales Invoice"), "target": "Sales Invoice", "method": "quotation_sales_invoice"},
	},
	"Stock Entry": {
		"make_stock_in_entry": {"label": _("End Transit"), "target": "Stock Entry", "method": "stock_entry_end_transit"},
		"create_sample_retention_stock_entry": {"label": _("Create Sample Retention Stock Entry"), "target": "Stock Entry", "method": "stock_entry_sample_retention"},
	},
	"Prospect": {
		"make_customer": {"label": _("Create Customer"), "target": "Customer", "method": "prospect_customer"},
		"make_opportunity": {"label": _("Create Opportunity"), "target": "Opportunity", "method": "prospect_opportunity"},
	},
	"Pick List": {
		"create_delivery_note": {"label": _("Create Delivery Note"), "target": "Delivery Note", "method": "pick_list_delivery_note"},
		"create_stock_entry": {"label": _("Create Stock Entry"), "target": "Stock Entry", "method": "pick_list_stock_entry"},
	},
	"Purchase Order": {
		"make_purchase_receipt": {"label": _("Create Purchase Receipt"), "target": "Purchase Receipt", "method": "purchase_order_receipt"},
		"make_purchase_invoice": {"label": _("Create Purchase Invoice"), "target": "Purchase Invoice", "method": "purchase_order_invoice"},
		"make_inter_company_sales_order": {"label": _("Create Inter Company Sales Order"), "target": "Sales Order", "method": "purchase_order_inter_company_sales_order"},
		"payment": {"label": _("Create Payment Entry"), "target": "Payment Entry", "method": "make_payment_entry_generic"},
	},
	"Purchase Receipt": {
		"make_purchase_invoice": {"label": _("Create Purchase Invoice"), "target": "Purchase Invoice", "method": "purchase_receipt_invoice"},
		"make_purchase_return": {"label": _("Create Purchase Return"), "target": "Purchase Receipt", "method": "purchase_receipt_return"},
		"make_lcv": {"label": _("Create Landed Cost Voucher"), "target": "Landed Cost Voucher", "method": "purchase_receipt_lcv"},
		"make_inter_company_delivery_note": {"label": _("Create Inter Company Delivery Note"), "target": "Delivery Note", "method": "purchase_receipt_inter_company_delivery_note"},
		"make_purchase_return_against_rejected_warehouse": {"label": _("Return Rejected Items"), "target": "Purchase Receipt", "method": "purchase_receipt_rejected_return"},
		"make_stock_entry": {"label": _("Create Stock Entry"), "target": "Stock Entry", "method": "purchase_receipt_stock_entry"},
	},
	"Purchase Invoice": {
		"make_payment_entry": {"label": _("Create Payment Entry"), "target": "Payment Entry", "method": "purchase_invoice_payment"},
		"make_debit_note": {"label": _("Create Debit Note"), "target": "Purchase Invoice", "method": "purchase_invoice_debit_note"},
		"make_inter_company_sales_invoice": {"label": _("Create Inter Company Sales Invoice"), "target": "Sales Invoice", "method": "purchase_invoice_inter_company_sales_invoice"},
		"make_purchase_receipt": {"label": _("Create Purchase Receipt"), "target": "Purchase Receipt", "method": "purchase_invoice_purchase_receipt"},
		"make_stock_entry": {"label": _("Create Stock Entry"), "target": "Stock Entry", "method": "purchase_invoice_stock_entry"},
		# Same doctype-agnostic make_lcv(doctype, docname) Purchase Receipt uses.
		"make_lcv": {"label": _("Create Landed Cost Voucher"), "target": "Landed Cost Voucher", "method": "purchase_receipt_lcv"},
	},
	"Journal Entry": {
		"make_reverse_journal_entry": {"label": _("Reverse Journal Entry"), "target": "Journal Entry", "method": "journal_entry_reverse"},
		"make_inter_company_journal_entry": {"label": _("Create Inter Company Journal Entry"), "target": "Journal Entry", "method": "journal_entry_inter_company", "requires_parameters": ["company"]},
	},
	"Invoice Discounting": {
		"create_disbursement_entry": {"label": _("Disburse Loan"), "target": "Journal Entry", "method": "invoice_discounting_disbursement"},
		"close_loan": {"label": _("Close Loan"), "target": "Journal Entry", "method": "invoice_discounting_close_loan"},
	},
	"Payment Request": {
		"make_payment_entry": {"label": _("Create Payment Entry"), "target": "Payment Entry", "method": "payment_request_payment_entry"},
	},
	"Share Transfer": {
		"make_jv_entry": {"label": _("Create Journal Entry"), "target": "Journal Entry", "method": "share_transfer_journal_entry"},
	},
	"Opportunity": {
		"make_quotation": {"label": _("Create Quotation"), "target": "Quotation", "method": "opportunity_quotation"},
		"make_quotation": {"label": _("Create Quotation"), "target": "Quotation", "method": "lead_quotation"},
	},
	"Dunning": {
		"payment": {"label": _("Create Payment Entry"), "target": "Payment Entry", "method": "make_payment_entry_generic"},
	},
}


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _parse(value: Any, expected: type, label: str):
	if isinstance(value, str):
		try:
			value = json.loads(value)
		except (TypeError, ValueError):
			frappe.throw(_("{0} must be valid JSON.").format(label), frappe.ValidationError)
	if not isinstance(value, expected):
		frappe.throw(_("{0} has an invalid format.").format(label), frappe.ValidationError)
	return value


def _permlevels(meta, permission: str) -> set[int]:
	try:
		return {cint(value) for value in meta.get_permlevel_access(permission, user=frappe.session.user)}
	except Exception:
		return {0}


def _readable_fields(meta, levels: set[int] | None = None) -> list:
	levels = _permlevels(meta, "read") if levels is None else levels
	# Applied here rather than at each call site so a field dropped for this
	# business is gone from the add form, the edit form and the detail view alike.
	suppressed = OUT_OF_CONTEXT_FIELDS.get(meta.name, frozenset())
	return [
		field for field in meta.fields
		if field.fieldtype in SUPPORTED_FIELD_TYPES
		and cint(field.permlevel) in levels
		and field.fieldname not in suppressed
	]


def _is_privileged_user_manager() -> bool:
	return frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()


def _write_only_inputs(meta) -> list:
	"""Write-only inputs (e.g. a password) exposed to privileged user managers.

	These bypass the SUPPORTED_FIELD_TYPES / read-only gating precisely because
	they are never surfaced on read paths — only accepted on create/update.
	"""
	if not _is_privileged_user_manager():
		return []
	return [field for name in WRITE_ONLY_INPUT_FIELDS.get(meta.name, ()) if (field := meta.get_field(name))]


def _writable_fields(meta, levels: set[int] | None = None) -> list:
	levels = _permlevels(meta, "write") if levels is None else levels
	special = SPECIAL_WRITABLE_FIELDS.get(meta.name, set()) if _is_privileged_user_manager() else set()
	suppressed = OUT_OF_CONTEXT_FIELDS.get(meta.name, frozenset())
	fields = [
		field for field in meta.fields
		if field.fieldtype in SUPPORTED_FIELD_TYPES
		and field.fieldtype not in LAYOUT_FIELDS | {"HTML", "Button"}
		and (field.fieldname in special or (not field.read_only and not field.hidden))
		and cint(field.permlevel) in levels
		# Not writable either: a field this business never fills must not be
		# settable through the API just because it is absent from the form.
		and field.fieldname not in suppressed
	]
	seen = {field.fieldname for field in fields}
	for field in _write_only_inputs(meta):
		if field.fieldname not in seen:
			fields.append(field)
			seen.add(field.fieldname)
	return fields


def _permissions(doctype: str, doc=None) -> dict:
	meta = frappe.get_meta(doctype)
	def allowed(ptype: str) -> bool:
		return bool(frappe.has_permission(doctype, ptype, doc=doc))
	return {
		"can_read": allowed("read"), "can_create": allowed("create"), "can_write": allowed("write"),
		"can_delete": allowed("delete"), "can_submit": bool(meta.is_submittable and allowed("submit")), "can_cancel": bool(meta.is_submittable and allowed("cancel")),
		"can_print": allowed("print"), "can_email": allowed("email"), "can_export": allowed("export"),
	}


def _permitted_select_options(doctype: str, fieldname: str, values: list[str]) -> list[str]:
	allowed = RESTRICTED_SELECT_OPTIONS.get((doctype, fieldname))
	return [value for value in values if value in allowed] if allowed else values


def _safe_options(field) -> Any:
	if field.fieldtype == "Select":
		values = [value for value in (field.options or "").splitlines() if value]
		return _permitted_select_options(field.parent, field.fieldname, values)
	if field.fieldtype in {"Link", "Table", "Table MultiSelect"}:
		return field.options
	if field.fieldtype == "Dynamic Link":
		return field.options
	return None


def _field_definition(field, *, writable: set[str], depth: int = 0) -> dict:
	definition = {
		"fieldname": field.fieldname, "label": field.label or field.fieldname,
		"fieldtype": field.fieldtype, "required": bool(field.reqd),
		"read_only": bool(field.fieldname not in writable),
		"hidden": bool(field.hidden and field.fieldname not in writable),
		"default": field.default, "options": _safe_options(field), "description": field.description,
		"precision": field.precision, "length": field.length, "permlevel": cint(field.permlevel),
		"depends_on": field.depends_on, "mandatory_depends_on": field.mandatory_depends_on,
		"read_only_depends_on": field.read_only_depends_on, "fetch_from": field.fetch_from,
		"fetch_if_empty": bool(field.fetch_if_empty), "non_negative": bool(field.non_negative),
		"unique": bool(field.unique), "unsupported_client_behavior": False,
	}
	relabelled = FIELD_LABEL_OVERRIDES.get((field.parent, field.fieldname))
	if relabelled:
		definition["label"] = relabelled
	# Button handlers and arbitrary client expressions are never executed by Vue.
	if field.fieldtype == "Button" or any(
		isinstance(definition.get(key), str) and definition[key].strip().startswith("eval:")
		for key in ("depends_on", "mandatory_depends_on", "read_only_depends_on")
	):
		definition["unsupported_client_behavior"] = True
	if field.parent == "User" and field.fieldname == "role_profile_name":
		definition["label"] = _("Role Profile (optional)")
		definition["description"] = _("Choose a saved Role Profile bundle, or assign individual roles in the Roles Assigned table below.")
	if field.parent == "User" and field.fieldname == "roles":
		definition["label"] = _("Roles Assigned")
		definition["description"] = _("Add individual permitted roles for this user. Role Profile selections may replace these roles during standard User validation.")
	if field.parent == "User" and field.fieldname == "enabled":
		definition["label"] = _("Account Enabled")
		definition["description"] = _("Turn off to immediately revoke this user's access. Re-enable to restore it.")
	if field.parent == "Role Profile" and field.fieldname == "roles":
		definition["label"] = _("Roles In This Profile")
		definition["description"] = _("Every user assigned this profile receives these roles.")
	if field.parent == "User" and field.fieldname == "new_password":
		definition["label"] = _("Set Password (optional)")
		definition["description"] = _("Set or reset this user's login password directly. Leave blank to keep the current password or rely on the welcome email.")
	if field.fieldtype in {"Table", "Table MultiSelect"} and field.options and depth == 0:
		child_meta = frappe.get_meta(field.options)
		# Child DocTypes do not carry standalone DocPerm rows. Their fields
		# inherit the current user's parent DocType permlevel access.
		parent_meta = frappe.get_meta(field.parent)
		child_read_levels = _permlevels(parent_meta, "read")
		child_write_levels = _permlevels(parent_meta, "write")
		child_write = {item.fieldname for item in _writable_fields(child_meta, child_write_levels)}
		definition["child_fields"] = [
			_field_definition(item, writable=child_write, depth=1)
			for item in _readable_fields(child_meta, child_read_levels)
			if item.fieldtype not in LAYOUT_FIELDS | {"Table", "Table MultiSelect", "Button", "HTML"}
		]
	return definition


def _metadata(feature: str) -> tuple[dict, Any, list, set[str]]:
	record = get_generated_feature(feature)
	meta = frappe.get_meta(record["doctype"])
	readable = _readable_fields(meta)
	writable = {field.fieldname for field in _writable_fields(meta)}
	return record, meta, readable, writable


def _public_feature(record: dict) -> dict:
	return {key: deepcopy(value) for key, value in record.items() if key not in {"required_permissions", "source_location"}}


def _record_route(record: dict, name: str | None = None, suffix: str | None = None) -> str:
	"""Return the registered clean route, retaining /generated as compatibility."""
	base = record.get("route") or record.get("list_route") or f"/generated/{record['route_key']}"
	if name:
		base = f"{base.rstrip('/')}/{quote(name, safe='')}"
	if suffix:
		base = f"{base.rstrip('/')}/{suffix}"
	return base


@frappe.whitelist(methods=["GET"])
def get_feature_registry(module: str | None = None, implementation_type: str | None = None, start: int = 0, page_length: int = 50):
	_require_login()
	page_length = min(max(cint(page_length) or 50, 1), 100)
	start = max(cint(start), 0)
	allowed_types = {"custom", "generated", "generated_provisional", "special"}
	if implementation_type and implementation_type not in allowed_types:
		frappe.throw(_("Unsupported implementation type."), frappe.ValidationError)
	records = [
		record for record in get_registry_records()
		if record.get("user_facing") and record.get("implementation_type") in allowed_types and (not module or record.get("module") == module)
		and (not implementation_type or record.get("implementation_type") == implementation_type)
		and feature_is_permitted(record)
	]
	return {"records": [_public_feature(record) for record in records[start:start + page_length]], "total": len(records), "start": start, "page_length": page_length}


@frappe.whitelist(methods=["GET"])
def get_feature_definition(feature: str):
	_require_login()
	record = get_feature(feature)
	if not feature_is_permitted(record):
		frappe.throw(_("Feature is not available."), frappe.PermissionError)
	return _public_feature(record)


@frappe.whitelist(methods=["GET"])
def get_doctype_metadata(feature: str):
	_require_login()
	record, meta, readable, writable = _metadata(feature)
	# Write-only inputs (e.g. a password) never appear on read paths, so append
	# them to the rendered form fields explicitly. They carry no default value.
	readable_names = {field.fieldname for field in readable}
	form_fields = readable + [field for field in _write_only_inputs(meta) if field.fieldname not in readable_names]
	# Essentials-only ordering the frontend applies when ADDING a record. Only
	# includes fields the user can actually see/write on this form.
	form_field_names = {field.fieldname for field in form_fields}
	simple_create_fields = [name for name in SIMPLE_CREATE_FIELDS.get(meta.name, ()) if name in form_field_names]
	simple_create_required = [name for name in SIMPLE_CREATE_REQUIRED.get(meta.name, ()) if name in form_field_names]
	defaults = {}
	if frappe.has_permission(meta.name, "create"):
		new_doc = frappe.new_doc(meta.name)
		for field in readable:
			if field.fieldtype not in LAYOUT_FIELDS | {"Table", "Table MultiSelect", "Button", "HTML"} and new_doc.get(field.fieldname) is not None:
				defaults[field.fieldname] = new_doc.get(field.fieldname)
		for (doctype, fieldname), value in FIELD_DEFAULT_OVERRIDES.items():
			if doctype == meta.name and fieldname in {field.fieldname for field in readable}:
				defaults[fieldname] = value
	return {
		"feature": _public_feature(record), "doctype": meta.name, "label": meta.get("label") or meta.name,
		"title_field": meta.title_field or "name", "image_field": meta.image_field,
		"is_submittable": bool(meta.is_submittable), "is_tree": bool(meta.is_tree), "is_single": bool(meta.issingle),
		"track_changes": bool(meta.track_changes), "search_fields": [value.strip() for value in (meta.search_fields or "").split(",") if value.strip()],
		"fields": [_field_definition(field, writable=writable) for field in form_fields],
		"simple_create_fields": simple_create_fields,
		"simple_create_required": simple_create_required,
		"defaults": defaults,
		"permissions": _permissions(meta.name),
		"client_script_policy": "not_executed",
		"presentation": record.get("presentation") or {},
	}


def _list_fields(meta, readable: list) -> list[str]:
	available = {field.fieldname: field for field in readable if field.fieldtype not in LAYOUT_FIELDS | {"Table", "Table MultiSelect", "Button", "HTML"}}
	preferred = ["name", meta.title_field, "status", "workflow_state", "disabled", "company", "modified"]
	result = []
	for fieldname in preferred + list(available):
		if fieldname and fieldname not in result and (fieldname == "name" or fieldname in available):
			result.append(fieldname)
		if len(result) >= 8:
			break
	return result or ["name", "modified"]


def _available_list_fields(readable: list) -> list:
	return [field for field in readable if field.fieldtype not in LAYOUT_FIELDS | {"Table", "Table MultiSelect", "Button", "HTML", "Text Editor", "Code", "Long Text", "Text"} and not field.hidden]


@frappe.whitelist(methods=["GET"])
def get_list_configuration(feature: str):
	_require_login()
	record, meta, readable, _writable = _metadata(feature)
	available = _available_list_fields(readable)
	available_names = {field.fieldname for field in available} | {"name", "modified"}
	presentation = record.get("presentation") or {}
	requested_defaults = presentation.get("default_columns") or []
	fields = [fieldname for fieldname in requested_defaults if fieldname in available_names]
	if not fields:
		fields = _list_fields(meta, readable)
	if "name" not in fields:
		fields.insert(0, "name")
	field_map = {field.fieldname: field for field in readable}
	all_columns = [{"fieldname": name, "label": (field_map[name].label if name in field_map else "ID" if name == "name" else name.title()), "fieldtype": (field_map[name].fieldtype if name in field_map else "Datetime" if name == "modified" else "Data"), "options": _safe_options(field_map[name]) if name in field_map else None} for name in ["name", *[field.fieldname for field in available], "modified"] if name not in {"creation", "owner", "modified_by"}]
	# Deduplicate metadata fields that overlap standard fields.
	all_columns = list({column["fieldname"]: column for column in all_columns}.values())
	filter_fields = [_field_definition(field, writable=set()) for field in readable if field.fieldtype in {"Link", "Select", "Date", "Datetime", "Check"} and not field.hidden]
	filter_map = {field["fieldname"]: field for field in filter_fields}
	main_filters = [filter_map[name] for name in presentation.get("main_filters", []) if name in filter_map][:5]
	if not main_filters:
		main_filters = filter_fields[:5]
	main_names = {field["fieldname"] for field in main_filters}
	return {
		"feature": _public_feature(record), "doctype": meta.name,
		"columns": [{
			"fieldname": name,
			"label": field_map[name].label if name in field_map else "ID" if name == "name" else "Modified" if name == "modified" else name.replace("_", " ").title(),
			"fieldtype": field_map[name].fieldtype if name in field_map else "Datetime" if name == "modified" else "Data",
		} for name in fields],
		"all_columns": all_columns, "default_columns": fields,
		"filter_fields": filter_fields, "main_filters": main_filters,
		"more_filters": [field for field in filter_fields if field["fieldname"] not in main_names],
		"sortable_fields": [column["fieldname"] for column in all_columns], "default_sort": {"field": "modified", "order": "desc"},
		"title_field": meta.title_field or "name", "permissions": _permissions(meta.name),
		"presentation": presentation,
	}


def _validated_filters(filters: Any, meta, readable_names: set[str]) -> list:
	if not filters:
		return []
	filters = _parse(filters, list, "Filters")
	result = []
	for item in filters:
		if not isinstance(item, list) or len(item) != 3:
			frappe.throw(_("Invalid filter."), frappe.ValidationError)
		fieldname, operator, value = item
		if fieldname not in readable_names or str(operator).lower() not in SAFE_FILTER_OPERATORS:
			frappe.throw(_("Unsupported filter."), frappe.ValidationError)
		result.append([fieldname, str(operator).lower(), value])
	return result


@frappe.whitelist(methods=["GET", "POST"])
def get_document_list(feature: str, search: str = "", filters: Any = None, columns: Any = None, sort_field: str = "modified", sort_order: str = "desc", page: int = 1, page_size: int = DEFAULT_PAGE_SIZE):
	_require_login()
	record, meta, readable, _writable = _metadata(feature)
	if not frappe.has_permission(meta.name, "read"):
		frappe.throw(_("Feature is not available."), frappe.PermissionError)
	available_columns = {field.fieldname for field in _available_list_fields(readable)} | {"name", "modified"}
	if columns:
		columns = _parse(columns, list, "Columns")
		if not columns or len(columns) > 12 or any(not isinstance(field, str) or field not in available_columns for field in columns):
			frappe.throw(_("Unsupported column selection."), frappe.ValidationError)
		columns = list(dict.fromkeys(columns))
	else:
		columns = [column["fieldname"] for column in get_list_configuration(feature)["columns"]]
	readable_names = {field.fieldname for field in readable} | {"name", "modified"}
	filterable_names = {
		field.fieldname for field in readable
		if field.fieldtype in {"Link", "Select", "Date", "Datetime", "Check"} and not field.hidden
	}
	if sort_field not in available_columns or sort_order.lower() not in {"asc", "desc"}:
		frappe.throw(_("Unsupported sort selection."), frappe.ValidationError)
	query_filters = _validated_filters(filters, meta, filterable_names)
	or_filters = []
	search = (search or "").strip()[:140]
	if search:
		searchable = ["name", meta.title_field] + [value.strip() for value in (meta.search_fields or "").split(",") if value.strip()]
		or_filters = [[fieldname, "like", f"%{search}%"] for fieldname in dict.fromkeys(searchable) if fieldname in readable_names]
	page = max(cint(page), 1)
	page_size = min(max(cint(page_size) or DEFAULT_PAGE_SIZE, 1), MAX_PAGE_SIZE)
	args = {"filters": query_filters, "or_filters": or_filters}
	count = frappe.get_list(meta.name, fields=["count(name) as total"], limit_page_length=1, **args)
	total = cint(count[0].total) if count else 0
	rows = frappe.get_list(meta.name, fields=columns, order_by=f"`tab{meta.name}`.`{sort_field}` {sort_order.lower()}", limit_start=(page - 1) * page_size, limit_page_length=page_size, **args)
	configuration = get_list_configuration(feature)
	column_map = {column["fieldname"]: column for column in configuration["all_columns"]}
	for column in configuration["columns"]:
		column_map.setdefault(column["fieldname"], column)
	# Default columns come from _list_fields, which may include a valid but
	# text/hidden field that _available_list_fields (all_columns) omits. Fall
	# back to a synthesised column so any servable DocType renders safely.
	readable_by_name = {field.fieldname: field for field in readable}
	def _column_for(name: str) -> dict:
		if name in column_map:
			return column_map[name]
		field = readable_by_name.get(name)
		return {
			"fieldname": name,
			"label": (field.label if field and field.label else "ID" if name == "name" else "Modified" if name == "modified" else name.replace("_", " ").title()),
			"fieldtype": (field.fieldtype if field else "Datetime" if name == "modified" else "Data"),
		}
	return {"feature": _public_feature(record), "records": rows, "columns": [_column_for(name) for name in columns], "permissions": _permissions(meta.name), "pagination": {"page": page, "page_size": page_size, "total": total, "pages": max((total + page_size - 1) // page_size, 1)}}


def _visible_doc(doc, meta, readable: list) -> dict:
	result = {"name": doc.name, "doctype": doc.doctype, "docstatus": doc.docstatus, "creation": doc.creation, "modified": doc.modified, "owner": doc.owner, "modified_by": doc.modified_by}
	for field in readable:
		if field.fieldtype in LAYOUT_FIELDS | {"Button", "HTML"}:
			continue
		value = doc.get(field.fieldname)
		if field.fieldtype in {"Table", "Table MultiSelect"}:
			allowed = {child["fieldname"] for child in _field_definition(field, writable=set()).get("child_fields", [])}
			result[field.fieldname] = [{key: row.get(key) for key in allowed if row.get(key) is not None} | {"name": row.name, "idx": row.idx} for row in (value or [])]
		else:
			result[field.fieldname] = value
	return result


def _get_permitted_doc(doctype: str, name: str, permission: str = "read"):
	# Single DocTypes (frappe.get_meta(doctype).issingle) live in the
	# key-value `tabSingles` table, not a normal doctype table — frappe.get_list
	# raises ProgrammingError against them. There is always exactly one
	# record, named after the doctype itself, so "existence" reduces to a
	# straight permission check; frappe.get_doc(doctype, doctype) never fails
	# for a real Single DocType.
	if frappe.get_meta(doctype).issingle:
		doc = frappe.get_doc(doctype, doctype)
		if not frappe.has_permission(doctype, permission, doc=doc):
			frappe.throw(_("Record was not found or is unavailable."), frappe.PermissionError)
		return doc
	# get_list applies match conditions first, avoiding an existence oracle.
	visible = frappe.get_list(doctype, filters={"name": name}, pluck="name", limit_page_length=1)
	if not visible:
		frappe.throw(_("Record was not found or is unavailable."), frappe.DoesNotExistError)
	doc = frappe.get_doc(doctype, name)
	if not frappe.has_permission(doctype, permission, doc=doc):
		frappe.throw(_("Record was not found or is unavailable."), frappe.PermissionError)
	return doc


@frappe.whitelist(methods=["GET"])
def get_document_detail(feature: str, name: str):
	_require_login()
	record, meta, readable, writable = _metadata(feature)
	doc = _get_permitted_doc(meta.name, name)
	return {"feature": _public_feature(record), "metadata": get_doctype_metadata(feature), "document": _visible_doc(doc, meta, readable), "permissions": _permissions(meta.name, doc=doc), "actions": [*_available_actions(meta, doc), *_available_workflow_actions(doc)], "route": _record_route(record, doc.name)}


def _coerce_value(field, value):
	if value is None:
		return None
	if field.fieldtype == "Check":
		return cint(value)
	if field.fieldtype in NUMERIC_FIELDS:
		value = flt(value)
		if field.non_negative and value < 0:
			frappe.throw(_("{0} cannot be negative.").format(field.label), frappe.ValidationError)
		return value
	if field.fieldtype == "Date" and value:
		return str(getdate(value))
	if field.fieldtype == "Select":
		# _permitted_select_options also strips the production-only choices, so a
		# purpose this business cannot pick on the form cannot be posted either.
		permitted = _permitted_select_options(
			field.parent, field.fieldname,
			[item for item in (field.options or "").splitlines() if item],
		)
		if value not in permitted:
			frappe.throw(_("Invalid value for {0}.").format(field.label), frappe.ValidationError)
	if field.fieldtype == "Link" and value:
		if not frappe.has_permission(field.options, "read") or not frappe.get_list(field.options, filters={"name": value}, pluck="name", limit_page_length=1):
			frappe.throw(_("Invalid or unavailable {0}.").format(field.label), frappe.ValidationError)
	if isinstance(value, str):
		return value[: cint(field.length) or 100000]
	return value


def _validate_dynamic_links(meta, clean: dict, existing=None) -> None:
	for field in meta.fields:
		if field.fieldtype != "Dynamic Link" or not clean.get(field.fieldname):
			continue
		target_doctype = clean.get(field.options) or (existing.get(field.options) if existing else None)
		if not target_doctype or not frappe.db.exists("DocType", target_doctype) or not frappe.has_permission(target_doctype, "read"):
			frappe.throw(_("Invalid or unavailable {0} type.").format(field.label), frappe.ValidationError)
		if not frappe.get_list(target_doctype, filters={"name": clean[field.fieldname]}, pluck="name", limit_page_length=1):
			frappe.throw(_("Invalid or unavailable {0}.").format(field.label), frappe.ValidationError)


def _clean_payload(meta, payload: Any, existing=None) -> dict:
	payload = _parse(payload, dict, "Document")
	writable = {field.fieldname: field for field in _writable_fields(meta)}
	# A client legitimately echoes back fields it cannot write: totals the
	# controller calculates (amount, base_rate), and fields dropped from the form
	# for this business that a browser tab opened before the change still knows
	# about. None of them can reach the document -- only `writable` keys are
	# applied below -- so refusing the whole save over one is pure obstruction.
	#
	# The guard that matters is the other one: a key that is not a field on this
	# DocType at all (owner, parent, docstatus, permissions) is a mass-assignment
	# attempt and is still rejected, by name.
	unknown = {key for key in payload if key not in writable and meta.get_field(key) is None}
	if unknown:
		frappe.throw(_("Unsupported field: {0}").format(", ".join(sorted(unknown))), frappe.ValidationError)
	clean = {}
	for fieldname, value in payload.items():
		field = writable.get(fieldname)
		if field is None:
			continue
		if field.fieldtype in {"Table", "Table MultiSelect"}:
			if not isinstance(value, list):
				frappe.throw(_("{0} must contain rows.").format(field.label), frappe.ValidationError)
			child_meta = frappe.get_meta(field.options)
			child_write = {
				child.fieldname: child
				for child in _writable_fields(child_meta, _permlevels(meta, "write"))
			}
			rows = []
			for row in value:
				if not isinstance(row, dict):
					frappe.throw(_("{0} must contain rows.").format(field.label), frappe.ValidationError)
				stray = {
					key for key in row
					if key not in child_write and key not in {"name", "idx"}
					and child_meta.get_field(key) is None
				}
				if stray:
					frappe.throw(
						_("Unsupported field on {0}: {1}").format(field.label, ", ".join(sorted(stray))),
						frappe.ValidationError,
					)
				clean_row = {key: _coerce_value(child_write[key], item) for key, item in row.items() if key in child_write}
				_validate_dynamic_links(child_meta, clean_row)
				rows.append(clean_row)
			clean[fieldname] = rows
		else:
			clean[fieldname] = _coerce_value(field, value)
	_validate_dynamic_links(meta, clean, existing)
	return clean


def _apply_user_create_defaults(doc) -> None:
	"""Let user managers create accounts by username alone.

	Frappe requires email (the User's unique id) and first_name, but the Add User
	form treats those as optional. When left blank we synthesise them from the
	username so username + password + role are the only mandatory inputs.
	"""
	username = (doc.get("username") or "").strip()
	if not doc.get("email"):
		if not username:
			frappe.throw(_("A username or an email is required."), frappe.ValidationError)
		domain = frappe.conf.get("user_default_email_domain") or frappe.local.site or "example.com"
		doc.email = f"{username}@{domain}"
	if not (doc.get("first_name") or "").strip():
		doc.first_name = username or (doc.email or "").split("@", 1)[0]


def _guard_self_lockout(doc) -> None:
	"""A user manager must not be able to lock themselves out.

	Frappe's own `check_enable_disable` protects only Administrator and Guest, so
	disabling your own account -- or dropping your own System Manager role -- would
	otherwise succeed and leave nobody able to undo it from this UI. `enabled` and
	`roles` are re-exposed as writable by SPECIAL_WRITABLE_FIELDS, so this guard is
	what keeps that re-exposure safe.
	"""
	if doc.name != frappe.session.user:
		return
	if not cint(doc.get("enabled")):
		frappe.throw(
			_("You cannot disable your own account. Ask another System Manager to do it."),
			frappe.PermissionError,
		)
	if "System Manager" not in frappe.get_roles(doc.name):
		return
	# A role profile can also grant the role, so check what the save would leave.
	prospective = {row.role for row in doc.get("roles", []) if row.role}
	if doc.get("role_profile_name"):
		prospective |= {
			row.role for row in frappe.get_all(
				"Has Role",
				filters={"parent": doc.get("role_profile_name"), "parenttype": "Role Profile"},
				fields=["role"],
			) if row.role
		}
	if "System Manager" not in prospective:
		frappe.throw(
			_("You cannot remove your own System Manager role. Ask another System Manager to do it."),
			frappe.PermissionError,
		)


@frappe.whitelist(methods=["POST"])
def create_document(feature: str, values: Any):
	_require_login()
	record = get_generated_feature(feature, "create")
	meta = frappe.get_meta(record["doctype"])
	if not frappe.has_permission(meta.name, "create"):
		frappe.throw(_("You cannot create this record."), frappe.PermissionError)
	doc = frappe.new_doc(meta.name)
	doc.update(_clean_payload(meta, values))
	if meta.name == "User":
		_apply_user_create_defaults(doc)
	doc.insert()
	return {"name": doc.name, "route": _record_route(record, doc.name), "modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def update_document(feature: str, name: str, values: Any, modified: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	meta = frappe.get_meta(record["doctype"])
	doc = _get_permitted_doc(meta.name, name, "write")
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it. Refresh before saving."), frappe.TimestampMismatchError)
	doc.update(_clean_payload(meta, values, doc))
	if meta.name == "User":
		_guard_self_lockout(doc)
	doc.save()
	return {"name": doc.name, "route": _record_route(record, doc.name), "modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def delete_document(feature: str, name: str, modified: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name, "delete")
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it. Refresh before deleting."), frappe.TimestampMismatchError)
	frappe.delete_doc(doc.doctype, doc.name)
	return {"deleted": True, "route": _record_route(record)}


def _available_actions(meta, doc) -> list[dict]:
	actions = []
	if doc.docstatus == 0 and meta.is_submittable and frappe.has_permission(meta.name, "submit", doc=doc):
		actions.append({"action": "submit", "label": _("Submit"), "destructive": False})
	if doc.docstatus == 1 and frappe.has_permission(meta.name, "cancel", doc=doc):
		actions.append({"action": "cancel", "label": _("Cancel"), "destructive": True})
	if doc.docstatus == 2 and meta.is_submittable and frappe.has_permission(meta.name, "create"):
		actions.append({"action": "amend", "label": _("Amend"), "destructive": False})
	if doc.docstatus == 0 and frappe.has_permission(meta.name, "delete", doc=doc):
		actions.append({"action": "delete", "label": _("Delete"), "destructive": True})
	if frappe.has_permission(meta.name, "create"):
		actions.append({"action": "duplicate", "label": _("Duplicate"), "destructive": False})
	if meta.allow_rename and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "rename", "label": _("Rename"), "destructive": False, "requires_parameters": ["new_name"]})
	if doc.doctype == "Opportunity" and doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.status == "Open":
			actions.append({"action": "close", "label": _("Close"), "destructive": False})
		else:
			actions.append({"action": "reopen", "label": _("Reopen"), "destructive": False})
	if doc.doctype == "Supplier" and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "resume" if doc.on_hold else "hold", "label": _("Resume") if doc.on_hold else _("Hold"), "destructive": False})
	if doc.doctype == "Stock Entry" and doc.docstatus == 1 and doc.add_to_transit and doc.purpose == "Material Transfer" and flt(doc.per_transferred) < 100 and frappe.has_permission("Stock Entry", "create"):
		actions.append({"action": "make_stock_in_entry", "label": _("End Transit"), "destructive": False, "mapping_target": "Stock Entry"})
	if doc.doctype in {"Quotation", "Opportunity"} and doc.docstatus == 0 and doc.status not in {"Ordered", "Converted", "Lost"} and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "set_as_lost", "label": _("Set as Lost"), "destructive": True, "requires_parameters": ["lost_reasons"]})
	if doc.doctype == "Purchase Invoice" and doc.docstatus == 1 and doc.update_stock and frappe.has_permission("Landed Cost Voucher", "create"):
		actions.append({"action": "make_lcv", "label": _("Create Landed Cost Voucher"), "destructive": False, "mapping_target": "Landed Cost Voucher"})
	if doc.doctype == "Supplier" and frappe.has_permission("GL Entry", "read"):
		actions.append({"action": "accounting_ledger", "label": _("Accounting Ledger"), "destructive": False})
		actions.append({"action": "accounts_payable", "label": _("Accounts Payable"), "destructive": False})
	if doc.doctype == "Purchase Order" and doc.docstatus == 1 and frappe.has_permission(meta.name, "submit", doc=doc):
		if doc.status == "On Hold":
			actions.append({"action": "resume", "label": _("Resume"), "destructive": False})
		elif doc.status in {"Closed", "Delivered"}:
			actions.append({"action": "reopen", "label": _("Reopen"), "destructive": False})
		else:
			actions.extend([
				{"action": "hold", "label": _("Hold"), "destructive": False, "requires_parameters": ["reason_for_hold"]},
				{"action": "close", "label": _("Close"), "destructive": True},
			])
	if doc.doctype == "Purchase Receipt" and doc.docstatus == 1 and frappe.has_permission(meta.name, "submit", doc=doc):
		if doc.status == "Closed":
			actions.append({"action": "reopen", "label": _("Reopen"), "destructive": False})
		elif doc.status != "Cancelled":
			actions.append({"action": "close", "label": _("Close"), "destructive": True})
	if doc.doctype == "Lead" and frappe.has_permission("Opportunity", "create"):
		actions.append({"action": "make_opportunity", "label": _("Create Opportunity"), "destructive": False, "mapping_target": "Opportunity"})
	if doc.doctype == "Opportunity" and frappe.has_permission("Customer", "create"):
		actions.append({"action": "make_customer", "label": _("Create Customer"), "destructive": False, "mapping_target": "Customer"})
	# Chart of Accounts admin actions (account.js) - real erpnext controller
	# methods, matched by exact scanner action key.
	if doc.doctype == "Account":
		actions.append({"action": "chart_of_accounts", "label": _("Chart of Accounts"), "destructive": False})
		if not cint(doc.is_group) and frappe.has_permission("GL Entry", "read"):
			actions.append({"action": "general_ledger", "label": _("General Ledger"), "destructive": False})
		if frappe.has_permission(meta.name, "write", doc=doc) and doc.parent_account:
			if cint(doc.is_group):
				actions.append({"action": "convert_to_non_group", "label": _("Convert to Non-Group"), "destructive": False})
			else:
				actions.append({"action": "convert_to_group", "label": _("Convert to Group"), "destructive": False})
			actions.append({"action": "merge_account", "label": _("Merge Account"), "destructive": True, "requires_parameters": ["new_account"]})
			actions.append({"action": "update_account_name_number", "label": _("Update Account Name / Number"), "destructive": False, "requires_parameters": ["account_name", "account_number"]})
	if doc.doctype == "Cost Center":
		actions.append({"action": "chart_of_cost_centers", "label": _("Chart of Cost Centers"), "destructive": False})
		if frappe.has_permission("Budget", "read"):
			actions.append({"action": "budget", "label": _("Budget"), "destructive": False})
		if frappe.has_permission(meta.name, "write", doc=doc):
			if cint(doc.is_group):
				actions.append({"action": "convert_to_non_group", "label": _("Convert to Non-Group"), "destructive": False})
			else:
				actions.append({"action": "convert_to_group", "label": _("Convert to Group"), "destructive": False})
			actions.append({"action": "update_cost_center_name_number", "label": _("Update Cost Center Name / Number"), "destructive": False, "requires_parameters": ["cost_center_name", "cost_center_number"]})
	# Ledger navigation shortcuts (journal_entry.js / period_closing_voucher.js /
	# warehouse.js) - pure navigation to the already-routed General Ledger
	# report with prefilled filters; no document is created or changed.
	if doc.doctype == "Journal Entry" and doc.docstatus > 0 and frappe.has_permission("GL Entry", "read"):
		actions.append({"action": "ledger", "label": _("Ledger"), "destructive": False})
	if doc.doctype == "Period Closing Voucher" and doc.docstatus > 0 and frappe.has_permission("GL Entry", "read"):
		actions.append({"action": "ledger", "label": _("Ledger"), "destructive": False})
	if doc.doctype == "Warehouse" and not cint(doc.is_group):
		if frappe.has_permission("GL Entry", "read") and frappe.db.exists("Account", {"warehouse": doc.name, "company": doc.company}):
			actions.append({"action": "general_ledger", "label": _("General Ledger"), "destructive": False})
		if frappe.has_permission("Stock Ledger Entry", "read"):
			actions.append({"action": "stock_balance", "label": _("Stock Balance"), "destructive": False})
	if doc.doctype == "Batch" and frappe.has_permission("Stock Ledger Entry", "read"):
		actions.append({"action": "view_ledger", "label": _("View Ledger"), "destructive": False})
	if doc.doctype == "Batch" and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "recalculate_batch_qty", "label": _("Recalculate Batch Qty"), "destructive": False})
	if doc.doctype == "Serial No" and frappe.has_permission("Stock Ledger Entry", "read"):
		actions.append({"action": "view_ledgers", "label": _("View Ledgers"), "destructive": False})
	# Pick List stock-reservation controls (pick_list.js) - real doc-bound
	# whitelisted methods (Stock Reservation Entry only, no Bin/Stock Ledger
	# Entry writes; reservation never reduces physical stock). Reproduces the
	# same enable_stock_reservation gate erpnext's own onload() applies.
	if doc.doctype == "Pick List" and doc.docstatus == 1 and doc.status != "Completed":
		if doc.purpose == "Delivery" and doc.status == "Open" and frappe.has_permission("Stock Reservation Entry", "write"):
			reservation_enabled = bool(frappe.get_cached_value("Stock Settings", None, "enable_stock_reservation"))
			if reservation_enabled and doc.has_unreserved_stock():
				actions.append({"action": "create_stock_reservation_entries", "label": _("Reserve"), "destructive": False})
			if doc.has_reserved_stock():
				actions.append({"action": "cancel_stock_reservation_entries", "label": _("Unreserve"), "destructive": True})
				actions.append({"action": "reserved_stock", "label": _("Reserved Stock"), "destructive": False})
		if frappe.has_permission(meta.name, "write", doc=doc):
			actions.append({"action": "update_current_stock", "label": _("Update Current Stock"), "destructive": False})
	# Company-level shortcuts (company.js) - navigation to the already-routed
	# Account/Cost Center trees, pre-filtered by this company.
	if doc.doctype == "Company":
		if frappe.has_permission("Cost Center", "read"):
			actions.append({"action": "cost_centers", "label": _("Cost Centers"), "destructive": False})
		if frappe.has_permission("Account", "read"):
			actions.append({"action": "chart_of_accounts", "label": _("Chart of Accounts"), "destructive": False})
	# Exchange Rate Revaluation's own idempotency check (check_journal_entry_condition)
	# gates the button in erpnext's own Desk UI - reproduced here so the
	# action is only offered when erpnext itself would offer it.
	if doc.doctype == "Exchange Rate Revaluation" and doc.docstatus == 1 and frappe.has_permission("Journal Entry", "create"):
		if doc.check_journal_entry_condition():
			actions.append({"action": "make_jv_entries", "label": _("Journal Entries"), "destructive": False})
	if doc.doctype == "Dunning" and doc.docstatus == 1 and doc.status == "Unresolved" and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "resolve", "label": _("Resolve"), "destructive": False})
	# Process Period Closing Voucher background-job controls
	# (process_period_closing_voucher.js Start/Pause/Resume buttons).
	# "cancel_pcv_processing" is not a separate button - it is erpnext's own
	# on_cancel() hook, already triggered by the standard "cancel" lifecycle
	# action (GENERIC_LIFECYCLE_ACTIONS) once this doctype is routed.
	if doc.doctype == "Purchase Invoice" and not doc.is_return and doc.docstatus == 1 and flt(doc.outstanding_amount) != 0 and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.on_hold:
			actions.append({"action": "change_release_date", "label": _("Change Release Date"), "destructive": False, "requires_parameters": ["release_date"]})
			actions.append({"action": "unblock_invoice", "label": _("Unblock Invoice"), "destructive": False})
		else:
			actions.append({"action": "block_invoice", "label": _("Block Invoice"), "destructive": True, "requires_parameters": ["release_date"]})
	if doc.doctype == "Process Period Closing Voucher" and doc.docstatus == 1 and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.status == "Queued":
			actions.append({"action": "start_pcv_processing", "label": _("Start"), "destructive": False})
		elif doc.status == "Running":
			actions.append({"action": "pause_pcv_processing", "label": _("Pause"), "destructive": False})
		elif doc.status == "Paused":
			actions.append({"action": "resume_pcv_processing", "label": _("Resume"), "destructive": False})
	# Buying document tools. Each symbolic key below maps to a fixed ERPNext
	# controller call in run_document_action; no method path comes from Vue.
	if doc.doctype == "Purchase Order" and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.docstatus == 0:
			actions.extend([
				{"action": "update_rate_as_per_last_purchase", "label": _("Update Rate as per Last Purchase"), "destructive": False},
			])
		elif doc.docstatus == 1:
			if any(cint(row.delivered_by_supplier) for row in doc.get("items") or []) and doc.status != "Delivered":
				actions.append({"action": "delivered", "label": _("Mark Delivered"), "destructive": False})
			if doc.status not in {"Closed", "Delivered"} and flt(doc.per_received) < 100 and flt(doc.per_billed) < 100 and doc.can_update_items():
				actions.append({"action": "update_items", "label": _("Update Items"), "destructive": False, "requires_parameters": ["items_json"]})
	if doc.doctype == "Supplier" and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "get_supplier_group_details", "label": _("Get Supplier Group Details"), "destructive": False})
		if cint(frappe.db.get_single_value("Accounts Settings", "enable_common_party_accounting")) and frappe.has_permission("Party Link", "create") and frappe.has_permission("Customer", "read"):
			actions.append({"action": "link_with_customer", "label": _("Link with Customer"), "destructive": False, "requires_parameters": ["customer"]})
	# Accounts tools discovered in the standard form scripts. The client receives
	# only symbolic action keys; every branch is fixed below and permission checked.
	if doc.doctype == "Accounting Dimension" and doc.get("document_type") and frappe.has_permission(doc.document_type, "read"):
		actions.append({"action": "show_0", "label": _("Show {0}").format(doc.document_type), "destructive": False})
	if doc.doctype == "Bank Account" and doc.get("integration_id") and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "unlink_external_integrations", "label": _("Unlink External Integrations"), "destructive": True})
	if doc.doctype == "Bank Reconciliation Tool" and frappe.has_permission("Bank Statement Import", "create"):
		actions.append({"action": "upload_bank_statement", "label": _("Upload Bank Statement"), "destructive": False})
	if doc.doctype == "Bank Statement Import":
		if doc.get("status") == "Partial Success":
			actions.append({"action": "export_errored_rows", "label": _("Export Errored Rows"), "destructive": False})
		if "Success" in str(doc.get("status") or "") and doc.get("reference_doctype") and frappe.has_permission(doc.reference_doctype, "read"):
			actions.append({"action": "go_to_0_list", "label": _("Open Imported Records"), "destructive": False})
		if doc.get("status"):
			actions.append({"action": "export_import_log", "label": _("Export Import Log"), "destructive": False})
	if doc.doctype == "Cheque Print Template":
		existing_format = frappe.db.exists("Print Format", doc.name)
		can_update_format = existing_format and frappe.has_permission("Print Format", "write", doc=existing_format)
		if can_update_format or (not existing_format and frappe.has_permission("Print Format", "create")):
			actions.append({"action": "create_or_update_cheque_print_format", "label": _("Create or Update Cheque Print Format"), "destructive": False})
	if doc.doctype == "Dunning" and doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "fetch_overdue_payments", "label": _("Fetch Overdue Payment"), "destructive": False, "requires_parameters": ["source_name"]})
	if doc.doctype == "Invoice Discounting":
		if doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc):
			actions.append({"action": "get_invoices", "label": _("Get Invoices"), "destructive": False, "requires_parameters": ["filters_json"]})
		if doc.docstatus > 0:
			actions.append({"action": "accounting_ledger", "label": _("Accounting Ledger"), "destructive": False})
	if doc.doctype == "Payment Order" and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.docstatus == 0:
			actions.append({"action": "payment_request", "label": _("Get Payment Request"), "destructive": False, "requires_parameters": ["source_name"]})
		elif doc.docstatus == 1 and doc.get("payment_order_type") == "Payment Request" and frappe.has_permission("Journal Entry", "create"):
			actions.append({"action": "make_payment_records", "label": _("Create Journal Entries"), "destructive": True, "requires_parameters": ["supplier"]})
	if doc.doctype == "Payment Request" and doc.docstatus == 1 and frappe.has_permission(meta.name, "write", doc=doc):
		if (
			doc.payment_request_type == "Inward"
			and doc.payment_channel != "Phone"
			and doc.status not in {"Initiated", "Paid"}
			and frappe.has_permission(meta.name, "email", doc=doc)
		):
			actions.append({"action": "resend_payment_email", "label": _("Resend Payment Email"), "destructive": False})
	if doc.doctype == "Subscription" and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.get("status") == "Cancelled":
			actions.append({"action": "restart_subscription", "label": _("Restart Subscription"), "destructive": True})
		else:
			actions.extend([
				{"action": "fetch_subscription_updates", "label": _("Fetch Subscription Updates"), "destructive": False},
				{"action": "force_fetch_subscription_updates", "label": _("Force-Fetch Subscription Updates"), "destructive": False},
				{"action": "cancel_subscription", "label": _("Cancel Subscription"), "destructive": True},
			])
	if doc.doctype == "Shareholder" and doc.get("folio_no"):
		if frappe.db.exists("Report", "Share Balance") and frappe.has_permission("Report", "read", doc="Share Balance"):
			actions.append({"action": "share_balance", "label": _("Share Balance"), "destructive": False})
		if frappe.db.exists("Report", "Share Ledger") and frappe.has_permission("Report", "read", doc="Share Ledger"):
			actions.append({"action": "share_ledger", "label": _("Share Ledger"), "destructive": False})
	if doc.doctype == "Process Statement Of Accounts":
		actions.append({"action": "download", "label": _("Download Statements"), "destructive": False})
		if frappe.has_permission(meta.name, "email", doc=doc) and frappe.has_permission(meta.name, "write", doc=doc):
			actions.append({"action": "send_emails", "label": _("Send Statement Emails"), "destructive": False})
	if doc.doctype == "Pick List":
		if doc.docstatus == 0 and doc.purpose == "Delivery" and frappe.has_permission(meta.name, "write", doc=doc):
			actions.append({"action": "get_items", "label": _("Get Items from Sales Order"), "destructive": False, "requires_parameters": ["source_name"]})
	if (
		doc.doctype == "Purchase Receipt" and doc.docstatus == 1 and doc.status != "Closed"
		and any(flt(row.sample_quantity) for row in doc.get("items") or [])
		and frappe.has_permission("Stock Entry", "create")
	):
		actions.append({"action": "retention_stock_entry", "label": _("Create Retention Stock Entry"), "destructive": False})
	if doc.doctype == "Purchase Receipt" and doc.docstatus > 0 and frappe.has_permission("Asset Movement", "read"):
		actions.append({"action": "asset_movement", "label": _("Asset Movements"), "destructive": False})
	if doc.doctype == "Inventory Dimension" and frappe.has_permission(meta.name, "delete", doc=doc):
		actions.append({"action": "delete_dimension", "label": _("Delete Dimension"), "destructive": True})
	if doc.doctype == "Item Group":
		actions.append({"action": "item_group_tree", "label": _("Item Group Tree"), "destructive": False})
		if frappe.has_permission("Item", "read"):
			actions.append({"action": "items", "label": _("Items"), "destructive": False})
	if doc.doctype == "Price List" and frappe.has_permission("Item Price", "read"):
		actions.append({"action": "add_edit_prices", "label": _("Add / Edit Prices"), "destructive": False})
	if (
		doc.doctype == "Serial and Batch Bundle" and doc.docstatus == 0 and doc.item_code
		and doc.type_of_transaction == "Inward" and frappe.has_permission(meta.name, "write", doc=doc)
		and (not cint(doc.has_serial_no) or frappe.has_permission("Serial No", "create"))
		and (not cint(doc.has_batch_no) or frappe.has_permission("Batch", "create"))
	):
		required = ["csv_file"] if cint(doc.has_batch_no) else ["serial_nos"]
		actions.append({"action": "make_0", "label": _("Add Serial / Batch Numbers"), "destructive": False, "requires_parameters": required})
	if doc.doctype == "Stock Reconciliation" and doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "fetch_items_from_warehouse", "label": _("Fetch Items from Warehouse"), "destructive": False, "requires_parameters": ["warehouse"]})
	if doc.doctype == "Stock Entry":
		if doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc):
			if any(cint(row.allow_alternative_item) for row in doc.get("items") or []):
				actions.append({"action": "alternate_item", "label": _("Select Alternate Items"), "destructive": False, "requires_parameters": ["items_json"]})
			if doc.purpose == "Material Issue":
				actions.append({"action": "expired_batches", "label": _("Get Expired Batches"), "destructive": False})
			actions.extend([
				{"action": "purchase_invoice", "label": _("Get Items from Purchase Invoice"), "destructive": False, "requires_parameters": ["source_name"]},
				{"action": "transit_entry", "label": _("Get Items from Transit Entry"), "destructive": False, "requires_parameters": ["source_name"]},
			])
		if doc.docstatus == 1 and flt(doc.per_transferred) > 0:
			actions.append({"action": "received_stock_entries", "label": _("Received Stock Entries"), "destructive": False})
	if doc.doctype == "Campaign" and frappe.has_permission("Lead", "read"):
		actions.append({"action": "view_leads", "label": _("View Leads"), "destructive": False})
	if doc.doctype == "Delivery Trip":
		if doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc) and frappe.has_permission("Delivery Note", "read"):
			actions.append({"action": "delivery_note", "label": _("Get Stops from Delivery Note"), "destructive": False, "requires_parameters": ["source_name"]})
		if frappe.has_permission("Delivery Note", "read"):
			actions.append({"action": "delivery_notes", "label": _("View Delivery Notes"), "destructive": False})
		can_notify = (
			doc.docstatus == 1 and bool(doc.get("delivery_stops"))
			and frappe.has_permission(meta.name, "email", doc=doc)
			and all(not row.delivery_note or frappe.has_permission("Delivery Note", "read", doc=row.delivery_note) for row in doc.get("delivery_stops") or [])
		)
		if can_notify:
			actions.append({"action": "notify_customers_via_email", "label": _("Notify Customers via Email"), "destructive": True})
	if doc.doctype == "Installation Note" and doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc) and frappe.has_permission("Delivery Note", "read"):
		actions.append({"action": "from_delivery_note", "label": _("Get Items from Delivery Note"), "destructive": False, "requires_parameters": ["source_name"]})
	if doc.doctype == "Lead" and frappe.has_permission(meta.name, "write", doc=doc):
		if frappe.has_permission("Prospect", "write"):
			actions.append({"action": "add_to_prospect", "label": _("Add to Prospect"), "destructive": False, "requires_parameters": ["prospect"]})
		if frappe.has_permission("Prospect", "create") or frappe.has_permission("Contact", "create"):
			actions.append({"action": "create_prospect_and_contact", "label": _("Create Prospect / Contact"), "destructive": False, "requires_parameters": ["options_json"]})
	if doc.doctype == "Opportunity" and doc.docstatus == 0 and doc.currency and doc.company and frappe.has_permission(meta.name, "write", doc=doc):
		from erpnext import get_company_currency
		if get_company_currency(doc.company) != doc.currency:
			actions.append({"action": "fetch_latest_exchange_rate", "label": _("Fetch Latest Exchange Rate"), "destructive": False})
	if doc.doctype == "Quotation" and doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc) and frappe.has_permission("Opportunity", "read"):
		actions.append({"action": "opportunity", "label": _("Get Items from Opportunity"), "destructive": False, "requires_parameters": ["source_name"]})
	if doc.doctype == "Quotation" and doc.docstatus == 1 and doc.status not in {"Lost", "Ordered"} and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "update_items", "label": _("Update Items"), "destructive": False, "requires_parameters": ["items_json"]})
	if doc.doctype in {"Maintenance Schedule", "Maintenance Visit"} and doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc) and frappe.has_permission("Sales Order", "read"):
		actions.append({"action": "sales_order", "label": _("Get Items from Sales Order"), "destructive": False, "requires_parameters": ["source_name"]})
	is_system_manager = frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()
	if doc.doctype == "Company":
		if frappe.has_permission("Sales Taxes and Charges Template", "read"):
			actions.append({"action": "sales_tax_template", "label": _("Sales Tax Templates"), "destructive": False})
		if frappe.has_permission("Purchase Taxes and Charges Template", "read"):
			actions.append({"action": "purchase_tax_template", "label": _("Purchase Tax Templates"), "destructive": False})
		if frappe.has_permission(meta.name, "write", doc=doc):
			actions.append({"action": "create_tax_template", "label": _("Create Default Tax Templates"), "destructive": False})
		if is_system_manager and frappe.has_permission(meta.name, "write", doc=doc) and frappe.has_permission("Transaction Deletion Record", "create"):
			actions.append({
				"action": "delete_transactions", "label": _("Delete Company Transactions"), "destructive": True,
				"requires_parameters": ["company_name", "current_password"],
			})
	if doc.doctype == "Email Digest" and is_system_manager:
		actions.append({"action": "view_now", "label": _("Preview Digest"), "destructive": False})
		if frappe.has_permission(meta.name, "email", doc=doc):
			actions.append({"action": "send_now", "label": _("Send Now"), "destructive": True})
	if (
		doc.doctype == "Employee" and not doc.user_id and doc.prefered_email
		and frappe.has_permission(meta.name, "write", doc=doc) and frappe.has_permission("User", "create")
	):
		actions.append({"action": "create_user", "label": _("Create User"), "destructive": False})
	if doc.doctype == "Contact":
		if doc.get("phone_nos"):
			actions.append({"action": "call", "label": _("Call"), "destructive": False})
		if not doc.user and doc.email_id and frappe.has_permission(meta.name, "write", doc=doc) and frappe.has_permission("User", "create"):
			actions.append({"action": "invite_as_user", "label": _("Invite as User"), "destructive": False})
	if doc.doctype == "Print Format":
		if doc.print_format_for == "DocType" and not cint(doc.custom_format) and frappe.has_permission(meta.name, "write", doc=doc):
			actions.append({"action": "edit_format", "label": _("Edit Format"), "destructive": False})
		if doc.print_format_for == "DocType" and doc.doc_type and frappe.has_permission("Customize Form", "write"):
			actions.append({"action": "set_as_default", "label": _("Set as Default"), "destructive": False})
	if doc.doctype == "Print Style" and is_system_manager:
		actions.append({"action": "print_settings", "label": _("Print Settings"), "destructive": False})
	for key, mapping in MAPPED_ACTIONS.get(doc.doctype, {}).items():
		if key in {item["action"] for item in actions}:
			continue
		# ERPNext mapped transaction methods require submitted source documents;
		# CRM conversions operate on their normal saved draft state.
		if doc.doctype not in {"Lead", "Opportunity", "Prospect"} and doc.docstatus != 1:
			continue
		if doc.doctype == "Purchase Order":
			if key == "make_inter_company_sales_order" and (not cint(doc.is_internal_supplier) or doc.inter_company_order_reference):
				continue
		if doc.doctype == "Invoice Discounting":
			if key == "create_disbursement_entry" and doc.status != "Sanctioned":
				continue
			if key == "close_loan" and doc.status != "Disbursed":
				continue
		if doc.doctype == "Journal Entry" and key == "make_inter_company_journal_entry" and (
			doc.voucher_type != "Inter Company Journal Entry" or doc.inter_company_journal_entry_reference
		):
			continue
		if doc.doctype == "Payment Request" and key == "make_payment_entry" and not (
			doc.payment_request_type == "Outward" and doc.status in {"Initiated", "Partially Paid"}
		):
			continue
		if doc.doctype == "Pick List":
			if (
				doc.status == "Completed"
				or (key == "create_delivery_note" and doc.purpose != "Delivery")
				or (key == "create_stock_entry" and (doc.purpose == "Delivery" or frappe.db.exists("Stock Entry", {"pick_list": doc.name})))
			):
				continue
		if doc.doctype == "Purchase Receipt" and key == "make_inter_company_delivery_note" and (not cint(doc.is_internal_supplier) or doc.inter_company_reference):
			continue
		if doc.doctype == "Stock Entry":
			if key == "create_sample_retention_stock_entry" and not (doc.purpose == "Material Receipt" and any(flt(row.sample_quantity) for row in doc.get("items") or [])):
				continue
		if frappe.has_permission(mapping["target"], "create"):
			actions.append({
				"action": key, "label": mapping["label"], "destructive": False,
				"mapping_target": mapping["target"],
				"requires_parameters": mapping.get("requires_parameters") or [],
			})
	return actions


def _run_mapped_action(doc, action: str, parameters: dict):
	mapping = MAPPED_ACTIONS[doc.doctype][action]
	if not frappe.has_permission(mapping["target"], "create"):
		frappe.throw(_("You cannot create the mapped document."), frappe.PermissionError)
	method = mapping["method"]
	if method == "quotation_sales_order":
		from erpnext.selling.doctype.quotation.quotation import make_sales_order
		target = make_sales_order(doc.name)
	elif method == "quotation_sales_invoice":
		from erpnext.selling.doctype.quotation.quotation import make_sales_invoice
		target = make_sales_invoice(doc.name)
	elif method == "purchase_order_receipt":
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		target = make_purchase_receipt(doc.name)
	elif method == "purchase_order_invoice":
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_invoice
		target = make_purchase_invoice(doc.name)
	elif method == "purchase_order_inter_company_sales_order":
		from erpnext.buying.doctype.purchase_order.purchase_order import make_inter_company_sales_order
		target = make_inter_company_sales_order(doc.name)
	elif method == "purchase_receipt_invoice":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
		target = make_purchase_invoice(doc.name)
	elif method == "purchase_receipt_return":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return
		target = make_purchase_return(doc.name)
	elif method == "purchase_receipt_lcv":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_lcv
		target = frappe.get_doc(make_lcv(doc.doctype, doc.name))
	elif method == "purchase_receipt_inter_company_delivery_note":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_inter_company_delivery_note
		target = make_inter_company_delivery_note(doc.name)
	elif method == "purchase_receipt_rejected_return":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return_against_rejected_warehouse
		target = make_purchase_return_against_rejected_warehouse(doc.name)
	elif method == "purchase_receipt_stock_entry":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_stock_entry
		target = make_stock_entry(doc.name)
	elif method == "stock_entry_end_transit":
		from erpnext.stock.doctype.stock_entry.stock_entry import make_stock_in_entry
		target = make_stock_in_entry(doc.name)
	elif method == "stock_entry_sample_retention":
		from erpnext.stock.doctype.stock_entry.stock_entry import move_sample_to_retention_warehouse
		target = move_sample_to_retention_warehouse(doc.company, [row.as_dict() for row in doc.get("items") or []])
		if not target:
			frappe.throw(_("No item has a sample quantity available for retention."), frappe.ValidationError)
		target = frappe.get_doc(target)
	elif method == "pick_list_delivery_note":
		from erpnext.stock.doctype.pick_list.pick_list import create_delivery_note
		target = create_delivery_note(doc.name)
	elif method == "pick_list_stock_entry":
		from erpnext.stock.doctype.pick_list.pick_list import create_stock_entry
		target = frappe.get_doc(create_stock_entry(doc.as_dict()))
	elif method == "purchase_invoice_debit_note":
		from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_debit_note
		target = make_debit_note(doc.name)
	elif method == "purchase_invoice_inter_company_sales_invoice":
		from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_inter_company_sales_invoice
		target = make_inter_company_sales_invoice(doc.name)
	elif method == "purchase_invoice_purchase_receipt":
		from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_purchase_receipt
		target = make_purchase_receipt(doc.name)
	elif method == "purchase_invoice_stock_entry":
		from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_stock_entry
		target = make_stock_entry(doc.name)
	elif method == "journal_entry_reverse":
		from erpnext.accounts.doctype.journal_entry.journal_entry import make_reverse_journal_entry
		target = make_reverse_journal_entry(doc.name)
	elif method == "journal_entry_inter_company":
		company = _permitted_source("Company", parameters.get("company"))
		if company == doc.company:
			frappe.throw(_("Choose another permitted Company."), frappe.ValidationError)
		from erpnext.accounts.doctype.journal_entry.journal_entry import make_inter_company_journal_entry
		target = frappe.get_doc(make_inter_company_journal_entry(doc.name, doc.voucher_type, company))
	elif method == "invoice_discounting_disbursement":
		target = doc.create_disbursement_entry()
	elif method == "invoice_discounting_close_loan":
		target = doc.close_loan()
	elif method == "payment_request_payment_entry":
		from erpnext.accounts.doctype.payment_request.payment_request import make_payment_entry
		target = frappe.get_doc(make_payment_entry(doc.name))
	elif method == "share_transfer_journal_entry":
		if doc.transfer_type == "Transfer":
			account = payment_account = doc.equity_or_liability_account
			credit_type, credit_party = "Shareholder", doc.to_shareholder
			debit_type, debit_party = "Shareholder", doc.from_shareholder
		elif doc.transfer_type == "Issue":
			account, payment_account = doc.asset_account, doc.equity_or_liability_account
			credit_type, credit_party, debit_type, debit_party = "Shareholder", doc.to_shareholder, "", ""
		else:
			account, payment_account = doc.equity_or_liability_account, doc.asset_account
			credit_type, credit_party, debit_type, debit_party = "", "", "Shareholder", doc.from_shareholder
		from erpnext.accounts.doctype.share_transfer.share_transfer import make_jv_entry
		target = frappe.get_doc(make_jv_entry(
			doc.company, account, doc.amount, payment_account,
			credit_type, credit_party, debit_type, debit_party,
		))
	elif method == "purchase_invoice_payment":
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		target = get_payment_entry(doc.doctype, doc.name)
	elif method == "make_payment_entry_generic":
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		target = get_payment_entry(doc.doctype, doc.name)
	elif method == "opportunity_quotation":
		from erpnext.crm.doctype.opportunity.opportunity import make_quotation
		target = make_quotation(doc.name)
	elif method == "lead_customer":
		from erpnext.crm.doctype.lead.lead import make_customer
		target = make_customer(doc.name)
	elif method == "lead_quotation":
		from erpnext.crm.doctype.lead.lead import make_quotation
		target = make_quotation(doc.name)
	elif method == "prospect_customer":
		from erpnext.crm.doctype.prospect.prospect import make_customer
		target = make_customer(doc.name)
	elif method == "prospect_opportunity":
		from erpnext.crm.doctype.prospect.prospect import make_opportunity
		target = make_opportunity(doc.name)
	else:
		frappe.throw(_("Mapped action is not available."), frappe.PermissionError)
	target.insert()
	target_record = get_feature(frappe.scrub(target.doctype).replace("_", "-"))
	return {
		"name": target.name, "doctype": target.doctype, "docstatus": target.docstatus,
		"modified": target.modified, "route": _record_route(target_record, target.name, "edit"),
	}


def _permitted_source(doctype: str, name: str):
	name = str(name or "").strip()
	if not name or not frappe.has_permission(doctype, "read"):
		frappe.throw(_("Source record is not available."), frappe.PermissionError)
	if not frappe.get_list(doctype, filters={"name": name}, pluck="name", limit_page_length=1):
		frappe.throw(_("Source record is not available."), frappe.PermissionError)
	return name


def _copy_child_values(row) -> dict:
	values = row.as_dict(no_nulls=False)
	for key in {"name", "parent", "parenttype", "parentfield", "idx", "docstatus", "doctype", "creation", "modified", "owner", "modified_by"}:
		values.pop(key, None)
	return values


def _update_transaction_items(doc, items_json) -> None:
	items = _parse(items_json, list, "Items")
	allowed = {
		"docname", "item_code", "item_name", "qty", "rate", "uom", "conversion_factor",
		"schedule_date", "fg_item", "fg_item_qty", "idx",
	}
	clean = []
	for row in items:
		if not isinstance(row, dict) or set(row) - allowed:
			frappe.throw(_("Unsupported item update field."), frappe.ValidationError)
		clean.append({key: value for key, value in row.items() if key in allowed})
	from erpnext.controllers.accounts_controller import update_child_qty_rate
	update_child_qty_rate(doc.doctype, json.dumps(clean), doc.name)


def _populate_invoice_discounting(doc, filters_json) -> None:
	filters = _parse(filters_json, dict, "Invoice filters")
	allowed = {"customer", "from_date", "to_date", "min_amount", "max_amount"}
	if set(filters) - allowed:
		frappe.throw(_("Unsupported invoice filter."), frappe.ValidationError)
	from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import get_invoices
	rows = get_invoices(json.dumps({key: value for key, value in filters.items() if key in allowed}))[:MAX_PAGE_SIZE]
	names = [row.get("sales_invoice") for row in rows if row.get("sales_invoice")]
	visible = set(frappe.get_list(
		"Sales Invoice", filters={"name": ["in", names]}, pluck="name",
		limit_page_length=MAX_PAGE_SIZE,
	)) if names else set()
	existing = {row.sales_invoice for row in doc.get("invoices") or [] if row.sales_invoice}
	for row in rows:
		if row.get("sales_invoice") in visible and row.get("sales_invoice") not in existing:
			doc.append("invoices", row)
	doc.save()


def _replace_stock_entry_alternatives(doc, items_json) -> None:
	requested = _parse(items_json, list, "Alternate items")
	children = {row.name: row for row in doc.get("items") or []}
	for values in requested:
		if not isinstance(values, dict) or set(values) - {"docname", "alternate_item"}:
			frappe.throw(_("Unsupported alternate-item field."), frappe.ValidationError)
		row = children.get(str(values.get("docname") or ""))
		alternate = str(values.get("alternate_item") or "").strip()
		if not row or not alternate or not cint(row.allow_alternative_item):
			frappe.throw(_("Alternate item selection is not valid."), frappe.ValidationError)
		_permitted_source("Item", alternate)
		direct = frappe.db.exists("Item Alternative", {"item_code": row.item_code, "alternative_item_code": alternate})
		reverse = frappe.db.exists("Item Alternative", {"item_code": alternate, "alternative_item_code": row.item_code, "two_way": 1})
		if not direct and not reverse:
			frappe.throw(_("Selected item is not an approved alternative."), frappe.ValidationError)
		row.original_item = row.item_code
		row.item_code = alternate
	doc.save()


def _populate_stock_reconciliation(doc, parameters: dict) -> None:
	warehouse = _permitted_source("Warehouse", parameters.get("warehouse"))
	item_code = _permitted_source("Item", parameters.get("item_code")) if parameters.get("item_code") else None
	from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import get_items
	rows = get_items(
		warehouse, doc.posting_date, doc.posting_time, doc.company,
		item_code=item_code, ignore_empty_stock=cint(parameters.get("ignore_empty_stock")),
	)
	if not rows:
		frappe.throw(_("No permitted stock rows were found."), frappe.ValidationError)
	doc.set("items", [])
	for row in rows[:MAX_PAGE_SIZE]:
		row = frappe._dict(row)
		row.qty = row.qty or 0
		row.valuation_rate = row.valuation_rate or 0
		doc.append("items", row)
	doc.save()


@frappe.whitelist()
def download_bank_statement_import_file(name: str, kind: str):
	_require_login()
	doc = _get_permitted_doc("Bank Statement Import", name)
	if kind == "errors":
		if doc.status != "Partial Success":
			frappe.throw(_("No errored rows are available."), frappe.ValidationError)
		doc.export_errored_rows()
		return None
	if kind == "log":
		return doc.download_import_log()
	frappe.throw(_("Unsupported export type."), frappe.ValidationError)


@frappe.whitelist(methods=["GET"])
def download_process_statement(name: str):
	_require_login()
	_get_permitted_doc("Process Statement Of Accounts", name)
	from erpnext.accounts.doctype.process_statement_of_accounts.process_statement_of_accounts import download_statements
	return download_statements(name)


def _available_workflow_actions(doc) -> list[dict]:
	from frappe.model.workflow import get_transitions, get_workflow_name
	if not get_workflow_name(doc.doctype):
		return []
	return [
		{"action": row.action, "label": row.action, "destructive": False, "kind": "workflow", "next_state": row.next_state}
		for row in (get_transitions(doc) or [])
	]


@frappe.whitelist(methods=["GET"])
def get_document_actions(feature: str, name: str):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	return {"actions": [*_available_actions(doc.meta, doc), *_available_workflow_actions(doc)], "modified": doc.modified, "docstatus": doc.docstatus}


@frappe.whitelist(methods=["POST"])
def run_document_action(feature: str, name: str, action: str, modified: str | None = None, parameters: Any = None):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	allowed = {item["action"] for item in _available_actions(doc.meta, doc)}
	if action not in allowed:
		frappe.throw(_("Action is not available."), frappe.PermissionError)
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it. Refresh before continuing."), frappe.TimestampMismatchError)
	parameters = _parse(parameters or {}, dict, "Action parameters")
	if action == "submit":
		doc.submit()
	elif action == "cancel":
		doc.cancel()
	elif action == "delete":
		frappe.delete_doc(doc.doctype, doc.name)
		return {"deleted": True, "route": _record_route(record)}
	elif action == "duplicate":
		copy = frappe.copy_doc(doc, ignore_no_copy=False)
		copy.docstatus = 0
		copy.insert()
		doc = copy
	elif action == "amend":
		amendment = frappe.copy_doc(doc, ignore_no_copy=False)
		amendment.amended_from = doc.name
		amendment.docstatus = 0
		amendment.insert()
		doc = amendment
	elif action == "rename":
		new_name = str(parameters.get("new_name") or "").strip()
		if not new_name or len(new_name) > 140 or any(character in new_name for character in ("/", "\x00")):
			frappe.throw(_("A valid new name is required."), frappe.ValidationError)
		from frappe.model.rename_doc import rename_doc
		new_name = rename_doc(doc=doc, new=new_name)
		doc = frappe.get_doc(doc.doctype, new_name)
	elif action in {"close", "reopen"} and doc.doctype == "Opportunity":
		doc.status = "Closed" if action == "close" else "Open"
		if action == "reopen" and doc.meta.has_field("lost_reasons"):
			doc.set("lost_reasons", [])
		doc.save()
	elif action in {"hold", "resume"} and doc.doctype == "Supplier":
		doc.on_hold = 0 if action == "resume" else 1
		doc.hold_type = "" if action == "resume" else (doc.hold_type or "All")
		doc.save()
	elif action == "make_opportunity" and doc.doctype == "Lead":
		from erpnext.crm.doctype.lead.lead import make_opportunity
		target = make_opportunity(doc.name)
		target.insert()
		target_record = get_generated_feature("opportunity")
		return {"name": target.name, "doctype": target.doctype, "docstatus": target.docstatus, "modified": target.modified, "route": _record_route(target_record, target.name)}
	elif action == "make_customer" and doc.doctype == "Opportunity":
		from erpnext.crm.doctype.opportunity.opportunity import make_customer
		target = make_customer(doc.name)
		target.insert()
		return {"name": target.name, "doctype": target.doctype, "docstatus": target.docstatus, "modified": target.modified, "route": f"/sales/customers/{quote(target.name, safe='')}"}
	elif action == "chart_of_accounts" and doc.doctype == "Account":
		return {"route": "/retail-erp/finance/chart-of-accounts"}
	elif action == "chart_of_cost_centers" and doc.doctype == "Cost Center":
		return {"route": "/retail-erp/finance/cost-centers"}
	elif action == "budget" and doc.doctype == "Cost Center":
		return {"route": "/retail-erp/finance/budget"}
	elif action == "chart_of_accounts" and doc.doctype == "Company":
		return {"route": f"/retail-erp/finance/chart-of-accounts?{urlencode({'company': doc.name}, quote_via=quote)}"}
	elif action == "cost_centers" and doc.doctype == "Company":
		return {"route": f"/retail-erp/finance/cost-centers?{urlencode({'company': doc.name}, quote_via=quote)}"}
	elif action == "general_ledger" and doc.doctype in {"Account", "Warehouse"}:
		account = doc.name if doc.doctype == "Account" else frappe.db.get_value("Account", {"warehouse": doc.name, "company": doc.company}, "name")
		if not account:
			frappe.throw(_("No linked account found for General Ledger."), frappe.ValidationError)
		fiscal_year = frappe.defaults.get_user_default("fiscal_year") or frappe.defaults.get_global_default("fiscal_year")
		fiscal_year_dates = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"]) if fiscal_year else None
		from_date, to_date = fiscal_year_dates or (None, None)
		# quote_via=quote (not the default quote_plus) so the frontend's
		# route.query (decodeURIComponent-based, does not decode "+" as
		# space) reads these values back correctly.
		params = urlencode({k: v for k, v in {"account": account, "company": doc.company, "from_date": from_date, "to_date": to_date}.items() if v}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('General Ledger')}?{params}"}
	elif action == "ledger" and doc.doctype == "Journal Entry":
		params = urlencode({"voucher_no": doc.name, "company": doc.company, "from_date": str(doc.posting_date), "to_date": getdate().isoformat()}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('General Ledger')}?{params}"}
	elif action == "ledger" and doc.doctype == "Period Closing Voucher":
		params = urlencode({"voucher_no": doc.name, "company": doc.company, "from_date": str(doc.period_start_date), "to_date": str(doc.period_end_date)}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('General Ledger')}?{params}"}
	elif action == "stock_balance" and doc.doctype == "Warehouse":
		params = urlencode({"warehouse": doc.name, "company": doc.company}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('Stock Balance')}?{params}"}
	elif action == "view_ledger" and doc.doctype == "Batch":
		params = urlencode({"batch_no": doc.name}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('Stock Ledger')}?{params}"}
	elif action == "recalculate_batch_qty" and doc.doctype == "Batch":
		doc.recalculate_batch_qty()
		doc.reload()
	elif action in {"hold", "resume", "close", "reopen"} and doc.doctype == "Purchase Order":
		from erpnext.buying.doctype.purchase_order.purchase_order import update_status
		if action == "hold":
			reason = str(parameters.get("reason_for_hold") or "").strip()
			if not reason:
				frappe.throw(_("A reason for hold is required."), frappe.ValidationError)
			doc.add_comment("Comment", _("Reason for hold: {0}").format(reason[:500]))
		status = {"hold": "On Hold", "resume": "Draft", "close": "Closed", "reopen": "Submitted"}[action]
		update_status(status, doc.name)
		doc.reload()
	elif action == "delivered" and doc.doctype == "Purchase Order":
		from erpnext.buying.doctype.purchase_order.purchase_order import update_status
		update_status("Delivered", doc.name)
		doc.reload()
	elif action == "update_rate_as_per_last_purchase" and doc.doctype == "Purchase Order":
		doc.get_last_purchase_rate()
		doc.save()
	elif action == "update_items" and doc.doctype in {"Purchase Order", "Quotation"}:
		_update_transaction_items(doc, parameters.get("items_json"))
		doc.reload()
	elif action == "view_leads" and doc.doctype == "Campaign":
		return {"route": f"/retail-erp/crm/leads?{urlencode({'campaign_name': doc.name}, quote_via=quote)}"}
	elif action == "delivery_note" and doc.doctype == "Delivery Trip":
		source = _permitted_source("Delivery Note", parameters.get("source_name"))
		from erpnext.stock.doctype.delivery_note.delivery_note import make_delivery_trip
		target = make_delivery_trip(source, target_doc=doc)
		target.save()
		doc = target
	elif action == "delivery_notes" and doc.doctype == "Delivery Trip":
		names = [row.delivery_note for row in doc.get("delivery_stops") or [] if row.delivery_note]
		visible = frappe.get_list("Delivery Note", filters={"name": ["in", names]}, pluck="name", limit_page_length=MAX_PAGE_SIZE) if names else []
		return {"route": f"/retail-erp/sales/delivery-notes?{urlencode({'name': ','.join(visible)}, quote_via=quote)}"}
	elif action == "notify_customers_via_email" and doc.doctype == "Delivery Trip":
		from erpnext.stock.doctype.delivery_trip.delivery_trip import notify_customers
		notify_customers(doc.name)
		doc.reload()
	elif action == "from_delivery_note" and doc.doctype == "Installation Note":
		source = _permitted_source("Delivery Note", parameters.get("source_name"))
		from erpnext.stock.doctype.delivery_note.delivery_note import make_installation_note
		target = make_installation_note(source, target_doc=doc)
		target.save()
		doc = target
	elif action == "add_to_prospect" and doc.doctype == "Lead":
		prospect = _permitted_source("Prospect", parameters.get("prospect"))
		if not frappe.has_permission("Prospect", "write", doc=prospect):
			frappe.throw(_("You cannot update this Prospect."), frappe.PermissionError)
		if frappe.db.exists("Prospect Lead", {"parent": prospect, "lead": doc.name}):
			frappe.throw(_("This Lead is already linked to the Prospect."), frappe.ValidationError)
		from erpnext.crm.doctype.lead.lead import add_lead_to_prospect
		add_lead_to_prospect(doc.name, prospect)
		doc.reload()
	elif action == "create_prospect_and_contact" and doc.doctype == "Lead":
		options = _parse(parameters.get("options_json"), dict, "Prospect and Contact options")
		if set(options) - {"create_contact", "create_prospect", "prospect_name"}:
			frappe.throw(_("Unsupported Prospect or Contact option."), frappe.ValidationError)
		create_contact = cint(options.get("create_contact"))
		create_prospect = cint(options.get("create_prospect"))
		if not create_contact and not create_prospect:
			frappe.throw(_("Select Prospect, Contact, or both."), frappe.ValidationError)
		if create_contact and not frappe.has_permission("Contact", "create"):
			frappe.throw(_("You cannot create Contacts."), frappe.PermissionError)
		if create_prospect and not frappe.has_permission("Prospect", "create"):
			frappe.throw(_("You cannot create Prospects."), frappe.PermissionError)
		if create_prospect and not str(options.get("prospect_name") or doc.company_name or "").strip():
			frappe.throw(_("Prospect name is required."), frappe.ValidationError)
		doc.create_prospect_and_contact({
			"create_contact": create_contact, "create_prospect": create_prospect,
			"prospect_name": str(options.get("prospect_name") or "").strip(),
		})
		doc.reload()
	elif action == "fetch_latest_exchange_rate" and doc.doctype == "Opportunity":
		from erpnext import get_company_currency
		from erpnext.setup.utils import get_exchange_rate
		rate = get_exchange_rate(doc.currency, get_company_currency(doc.company), doc.transaction_date)
		if not rate:
			frappe.throw(_("No exchange rate is available for this date."), frappe.ValidationError)
		doc.conversion_rate = rate
		doc.save()
	elif action == "opportunity" and doc.doctype == "Quotation":
		source = _permitted_source("Opportunity", parameters.get("source_name"))
		from erpnext.crm.doctype.opportunity.opportunity import make_quotation
		target = make_quotation(source, target_doc=doc)
		target.save()
		doc = target
	elif action == "sales_order" and doc.doctype in {"Maintenance Schedule", "Maintenance Visit"}:
		source = _permitted_source("Sales Order", parameters.get("source_name"))
		if doc.doctype == "Maintenance Schedule":
			from erpnext.selling.doctype.sales_order.sales_order import make_maintenance_schedule
			target = make_maintenance_schedule(source, target_doc=doc)
		else:
			from erpnext.selling.doctype.sales_order.sales_order import make_maintenance_visit
			target = make_maintenance_visit(source, target_doc=doc)
		if not target:
			frappe.throw(_("A completed maintenance document already exists for this Sales Order."), frappe.ValidationError)
		target.save()
		doc = target
	elif action in {"sales_tax_template", "purchase_tax_template"} and doc.doctype == "Company":
		destination = "sales-taxes-and-charges-template" if action == "sales_tax_template" else "purchase-taxes-and-charges-template"
		return {"route": f"/retail-erp/finance/{destination}?{urlencode({'company': doc.name}, quote_via=quote)}"}
	elif action == "create_tax_template" and doc.doctype == "Company":
		doc.create_default_tax_template()
		doc.reload()
	elif action == "delete_transactions" and doc.doctype == "Company":
		company_name = str(parameters.get("company_name") or "").strip()
		password = str(parameters.get("current_password") or "")
		if company_name != doc.name:
			frappe.throw(_("Enter the exact Company name to confirm deletion."), frappe.ValidationError)
		if not password:
			frappe.throw(_("Your current password is required."), frappe.AuthenticationError)
		from frappe.core.doctype.user.user import verify_password
		verify_password(password)
		from erpnext.setup.doctype.company.company import create_transaction_deletion_request
		create_transaction_deletion_request(doc.name)
		return {"route": "/retail-erp/admin/companies", "queued": True}
	elif action == "view_now" and doc.doctype == "Email Digest":
		from frappe.utils import strip_html
		message = strip_html(doc.get_msg_html() or "")
		return {"message": message[:12000] or _("The digest contains no content.")}
	elif action == "send_now" and doc.doctype == "Email Digest":
		doc.send()
		return {"name": doc.name, "sent": True}
	elif action == "create_user" and doc.doctype == "Employee":
		from erpnext.setup.doctype.employee.employee import create_user
		user = create_user(doc.name, email=doc.prefered_email)
		doc.reload()
		return {"name": doc.name, "created": user, "route": f"/retail-erp/admin/users/{quote(user, safe='')}"}
	elif action == "call" and doc.doctype == "Contact":
		phones = sorted(
			(row for row in doc.get("phone_nos") or [] if row.phone),
			key=lambda row: (cint(row.is_primary_mobile_no), cint(row.is_primary_phone)), reverse=True,
		)
		if not phones:
			frappe.throw(_("This Contact has no phone number."), frappe.ValidationError)
		return {"external_url": f"tel:{quote(str(phones[0].phone), safe='+*#()- ')}"}
	elif action == "invite_as_user" and doc.doctype == "Contact":
		from frappe.contacts.doctype.contact.contact import invite_user
		user = invite_user(doc.name)
		doc.reload()
		return {"name": doc.name, "created": user, "route": f"/retail-erp/admin/users/{quote(user, safe='')}"}
	elif action == "edit_format" and doc.doctype == "Print Format":
		return {"route": _record_route(record, doc.name, "edit")}
	elif action == "set_as_default" and doc.doctype == "Print Format":
		from frappe.printing.doctype.print_format.print_format import make_default
		make_default(doc.name)
		doc.reload()
	elif action == "print_settings" and doc.doctype == "Print Style":
		return {"route": "/retail-erp/admin/print-settings"}
	elif action == "get_supplier_group_details" and doc.doctype == "Supplier":
		doc.get_supplier_group_details()
		doc.reload()
	elif action == "link_with_customer" and doc.doctype == "Supplier":
		customer = _permitted_source("Customer", parameters.get("customer"))
		from erpnext.accounts.doctype.party_link.party_link import create_party_link
		target = create_party_link("Supplier", doc.name, customer)
		target_record = get_generated_feature("party-link")
		return {"name": target.name, "doctype": target.doctype, "route": _record_route(target_record, target.name)}
	elif action == "show_0" and doc.doctype == "Accounting Dimension":
		target_record = get_feature(frappe.scrub(doc.document_type).replace("_", "-"))
		return {"route": _record_route(target_record)}
	elif action == "unlink_external_integrations" and doc.doctype == "Bank Account":
		doc.integration_id = None
		doc.save()
	elif action == "upload_bank_statement" and doc.doctype == "Bank Reconciliation Tool":
		from erpnext.accounts.doctype.bank_statement_import.bank_statement_import import upload_bank_statement
		target = upload_bank_statement(company=doc.company, bank_account=doc.bank_account)
		target.insert()
		target_record = get_generated_feature("bank-statement-import")
		return {"name": target.name, "doctype": target.doctype, "route": _record_route(target_record, target.name, "edit")}
	elif action in {"export_errored_rows", "export_import_log"} and doc.doctype == "Bank Statement Import":
		query = urlencode({"name": doc.name, "kind": "errors" if action == "export_errored_rows" else "log"}, quote_via=quote)
		return {"download_url": f"/api/method/my_store_ui.universal.api.download_bank_statement_import_file?{query}"}
	elif action == "go_to_0_list" and doc.doctype == "Bank Statement Import":
		target_record = get_feature(frappe.scrub(doc.reference_doctype).replace("_", "-"))
		return {"route": _record_route(target_record)}
	elif action == "create_or_update_cheque_print_format" and doc.doctype == "Cheque Print Template":
		from erpnext.accounts.doctype.cheque_print_template.cheque_print_template import create_or_update_cheque_print_format
		target = create_or_update_cheque_print_format(doc.name)
		target_record = get_generated_feature("print-format")
		return {"name": target.name, "doctype": target.doctype, "route": _record_route(target_record, target.name, "edit")}
	elif action == "fetch_overdue_payments" and doc.doctype == "Dunning":
		source = _permitted_source("Sales Invoice", parameters.get("source_name"))
		from erpnext.accounts.doctype.sales_invoice.sales_invoice import create_dunning
		target = create_dunning(source, target_doc=doc)
		target.save()
		doc = target
	elif action == "get_invoices" and doc.doctype == "Invoice Discounting":
		_populate_invoice_discounting(doc, parameters.get("filters_json"))
		doc.reload()
	elif action == "accounting_ledger" and doc.doctype == "Invoice Discounting":
		params = urlencode({"voucher_no": doc.name, "from_date": doc.posting_date, "to_date": getdate().isoformat(), "company": doc.company}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('General Ledger')}?{params}"}
	elif action == "payment_request" and doc.doctype == "Payment Order":
		source = _permitted_source("Payment Request", parameters.get("source_name"))
		from erpnext.accounts.doctype.payment_request.payment_request import make_payment_order
		target = make_payment_order(source, target_doc=doc)
		target.save()
		doc = target
	elif action == "make_payment_records" and doc.doctype == "Payment Order":
		supplier = _permitted_source("Supplier", parameters.get("supplier"))
		if supplier not in {row.supplier for row in doc.get("references") or [] if row.supplier}:
			frappe.throw(_("Supplier is not present in this Payment Order."), frappe.ValidationError)
		from erpnext.accounts.doctype.payment_order.payment_order import make_payment_records
		make_payment_records(doc.name, supplier, parameters.get("mode_of_payment") or None)
		doc.reload()
	elif action == "resend_payment_email" and doc.doctype == "Payment Request":
		doc.send_email()
		doc.reload()
	elif action in {"cancel_subscription", "restart_subscription", "fetch_subscription_updates", "force_fetch_subscription_updates"} and doc.doctype == "Subscription":
		if action == "cancel_subscription":
			doc.cancel_subscription()
		elif action == "restart_subscription":
			doc.restart_subscription()
		elif action == "force_fetch_subscription_updates":
			doc.force_fetch_subscription_updates()
		else:
			doc.process()
		doc.reload()
	elif action in {"share_balance", "share_ledger"} and doc.doctype == "Shareholder":
		report = "Share Balance" if action == "share_balance" else "Share Ledger"
		params = urlencode({"shareholder": doc.name}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote(report)}?{params}"}
	elif action == "download" and doc.doctype == "Process Statement Of Accounts":
		query = urlencode({"name": doc.name}, quote_via=quote)
		return {"download_url": f"/api/method/my_store_ui.universal.api.download_process_statement?{query}"}
	elif action == "send_emails" and doc.doctype == "Process Statement Of Accounts":
		from erpnext.accounts.doctype.process_statement_of_accounts.process_statement_of_accounts import send_emails
		queued = send_emails(doc.name)
		return {"name": doc.name, "doctype": doc.doctype, "queued": bool(queued)}
	elif action == "get_items" and doc.doctype == "Pick List":
		source = _permitted_source("Sales Order", parameters.get("source_name"))
		from erpnext.selling.doctype.sales_order.sales_order import create_pick_list
		target = create_pick_list(source, target_doc=doc)
		target.save()
		doc = target
	elif action == "retention_stock_entry" and doc.doctype == "Purchase Receipt":
		from erpnext.stock.doctype.stock_entry.stock_entry import move_sample_to_retention_warehouse
		target = move_sample_to_retention_warehouse(doc.company, [row.as_dict() for row in doc.get("items") or []])
		if not target:
			frappe.throw(_("No item has a sample quantity available for retention."), frappe.ValidationError)
		target = frappe.get_doc(target)
		target.insert()
		target_record = get_generated_feature("stock-entry")
		return {"name": target.name, "doctype": target.doctype, "route": _record_route(target_record, target.name, "edit")}
	elif action == "asset_movement" and doc.doctype == "Purchase Receipt":
		return {"route": f"/retail-erp/operations/asset-movements?{urlencode({'reference_name': doc.name}, quote_via=quote)}"}
	elif action == "delete_dimension" and doc.doctype == "Inventory Dimension":
		from erpnext.stock.doctype.inventory_dimension.inventory_dimension import delete_dimension
		delete_dimension(doc.name)
		return {"deleted": True, "route": "/retail-erp/inventory/inventory-dimensions"}
	elif action == "item_group_tree" and doc.doctype == "Item Group":
		return {"route": "/retail-erp/inventory/item-groups"}
	elif action == "items" and doc.doctype == "Item Group":
		return {"route": f"/retail-erp/inventory/products?{urlencode({'item_group': doc.name}, quote_via=quote)}"}
	elif action == "add_edit_prices" and doc.doctype == "Price List":
		return {"route": f"/retail-erp/inventory/item-prices?{urlencode({'price_list': doc.name}, quote_via=quote)}"}
	elif action == "make_0" and doc.doctype == "Serial and Batch Bundle":
		data = {"using_csv_file": 0}
		if cint(doc.has_batch_no):
			file_url = str(parameters.get("csv_file") or "").strip()
			files = frappe.get_list(
				"File", filters={"file_url": file_url}, fields=["name", "file_url"], limit_page_length=1,
			)
			if not files:
				frappe.throw(_("A permitted Serial / Batch CSV attachment is required."), frappe.ValidationError)
			data = {"using_csv_file": 1, "csv_file": files[0].file_url}
		else:
			serial_nos = str(parameters.get("serial_nos") or "").strip()
			if not serial_nos:
				frappe.throw(_("Serial numbers are required."), frappe.ValidationError)
			data["serial_nos"] = serial_nos
		doc.add_serial_batch(data)
		doc.save()
	elif action == "fetch_items_from_warehouse" and doc.doctype == "Stock Reconciliation":
		_populate_stock_reconciliation(doc, parameters)
		doc.reload()
	elif action == "alternate_item" and doc.doctype == "Stock Entry":
		_replace_stock_entry_alternatives(doc, parameters.get("items_json"))
		doc.reload()
	elif action == "expired_batches" and doc.doctype == "Stock Entry":
		from erpnext.stock.doctype.stock_entry.stock_entry import get_expired_batch_items
		rows = get_expired_batch_items() or []
		doc.set("items", [])
		for row in rows[:MAX_PAGE_SIZE]:
			row = frappe._dict(row)
			if not frappe.get_list("Item", filters={"name": row.item}, pluck="name", limit_page_length=1):
				continue
			if not frappe.get_list("Warehouse", filters={"name": row.warehouse}, pluck="name", limit_page_length=1):
				continue
			doc.append("items", {
				"item_code": row.item, "s_warehouse": row.warehouse, "qty": row.qty,
				"uom": row.stock_uom, "conversion_factor": 1, "batch_no": row.batch_no,
				"transfer_qty": row.qty,
			})
		if not doc.get("items"):
			frappe.throw(_("No permitted expired-batch stock was found."), frappe.ValidationError)
		doc.save()
	elif action in {"purchase_invoice", "transit_entry"} and doc.doctype == "Stock Entry":
		if action == "purchase_invoice":
			source = _permitted_source("Purchase Invoice", parameters.get("source_name"))
			from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_stock_entry
			target = make_stock_entry(source, target_doc=doc)
		else:
			source = _permitted_source("Stock Entry", parameters.get("source_name"))
			from erpnext.stock.doctype.stock_entry.stock_entry import make_stock_in_entry
			target = make_stock_in_entry(source, target_doc=doc)
		target.save()
		doc = target
	elif action == "received_stock_entries" and doc.doctype == "Stock Entry":
		return {"route": f"/retail-erp/inventory/stock-entries?{urlencode({'outgoing_stock_entry': doc.name}, quote_via=quote)}"}
	elif action == "accounting_ledger" and doc.doctype == "Supplier":
		params = urlencode({"party_type": "Supplier", "party": doc.name}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('General Ledger')}?{params}"}
	elif action == "accounts_payable" and doc.doctype == "Supplier":
		params = urlencode({"party": doc.name}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('Accounts Payable')}?{params}"}
	elif action == "set_as_lost" and doc.doctype in {"Quotation", "Opportunity"}:
		reasons_raw = str(parameters.get("lost_reasons") or "").strip()
		reason_doctype = "Quotation Lost Reason" if doc.doctype == "Quotation" else "Opportunity Lost Reason"
		lost_reasons_list = []
		for name in (part.strip() for part in reasons_raw.split(",")):
			if not name:
				continue
			if not frappe.db.exists(reason_doctype, name):
				frappe.throw(_("Unknown lost reason: {0}").format(name), frappe.ValidationError)
			lost_reasons_list.append({"lost_reason": name})
		if not lost_reasons_list:
			frappe.throw(_("At least one valid lost reason is required."), frappe.ValidationError)
		doc.declare_enquiry_lost(lost_reasons_list, [])
		doc.reload()
	elif action == "view_ledgers" and doc.doctype == "Serial No":
		params = urlencode({"item_code": doc.item_code, "serial_no": doc.name}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('Serial No Ledger')}?{params}"}
	elif action == "create_stock_reservation_entries" and doc.doctype == "Pick List":
		doc.create_stock_reservation_entries(notify=True)
		doc.reload()
	elif action == "cancel_stock_reservation_entries" and doc.doctype == "Pick List":
		doc.cancel_stock_reservation_entries(notify=True)
		doc.reload()
	elif action == "update_current_stock" and doc.doctype == "Pick List":
		doc.set_item_locations(save=True)
		doc.reload()
	elif action == "reserved_stock" and doc.doctype == "Pick List":
		# Reserved Stock hard-requires company/from_date/to_date
		# (reserved_stock.py::validate_filters) - erpnext's own pick_list.js
		# passes creation..max(locations.modified); today is an equally safe
		# upper bound and can never be < from_date.
		params = urlencode({
			"company": doc.company, "from_date": str(getdate(doc.creation)), "to_date": getdate().isoformat(),
			"from_voucher_type": "Pick List", "from_voucher_no": doc.name,
		}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('Reserved Stock')}?{params}"}
	elif action in {"convert_to_group", "convert_to_non_group"} and doc.doctype in {"Account", "Cost Center"}:
		if action == "convert_to_group":
			doc.convert_ledger_to_group()
		else:
			doc.convert_group_to_ledger()
		doc.reload()
	elif action == "merge_account" and doc.doctype == "Account":
		new_account = str(parameters.get("new_account") or "").strip()
		if not new_account or not frappe.db.exists("Account", new_account) or not frappe.has_permission("Account", "write", doc=new_account):
			frappe.throw(_("A valid target account is required."), frappe.ValidationError)
		from erpnext.accounts.doctype.account.account import merge_account
		new_name = merge_account(doc.name, new_account) or new_account
		return {"name": new_name, "route": _record_route(record, new_name)}
	elif action == "update_account_name_number" and doc.doctype == "Account":
		account_name = str(parameters.get("account_name") or "").strip()
		account_number = str(parameters.get("account_number") or "").strip()
		if not account_name:
			frappe.throw(_("Account name is required."), frappe.ValidationError)
		from erpnext.accounts.doctype.account.account import update_account_number
		new_name = update_account_number(doc.name, account_name, account_number) or doc.name
		return {"name": new_name, "route": _record_route(record, new_name)}
	elif action == "update_cost_center_name_number" and doc.doctype == "Cost Center":
		cc_name = str(parameters.get("cost_center_name") or "").strip()
		cc_number = str(parameters.get("cost_center_number") or "").strip()
		if not cc_name:
			frappe.throw(_("Cost center name is required."), frappe.ValidationError)
		from erpnext.accounts.utils import update_cost_center
		new_name = update_cost_center(doc.name, cc_name, cc_number, doc.company, 0) or doc.name
		return {"name": new_name, "route": _record_route(record, new_name)}
	elif action == "make_jv_entries" and doc.doctype == "Exchange Rate Revaluation":
		if not doc.check_journal_entry_condition():
			frappe.throw(_("Journal entries are already up to date for this revaluation."), frappe.ValidationError)
		result = doc.make_jv_entries()
		return {"name": doc.name, "docstatus": doc.docstatus, "modified": doc.modified, "route": _record_route(record, doc.name), "created": result}
	elif action == "resolve" and doc.doctype == "Dunning":
		doc.status = "Resolved"
		doc.save()
	elif action in {"close", "reopen"} and doc.doctype == "Purchase Receipt":
		doc.update_status("Closed" if action == "close" else "Submitted")
		doc.reload()
	elif action == "block_invoice" and doc.doctype == "Purchase Invoice":
		release_date = str(parameters.get("release_date") or "").strip()
		if not release_date:
			frappe.throw(_("A release date is required."), frappe.ValidationError)
		hold_comment = str(parameters.get("hold_comment") or "").strip() or None
		doc.block_invoice(hold_comment, release_date)
		doc.reload()
	elif action == "unblock_invoice" and doc.doctype == "Purchase Invoice":
		doc.unblock_invoice()
		doc.reload()
	elif action == "change_release_date" and doc.doctype == "Purchase Invoice":
		release_date = str(parameters.get("release_date") or "").strip()
		if not release_date:
			frappe.throw(_("A release date is required."), frappe.ValidationError)
		doc.db_set("release_date", release_date)
		doc.reload()
	elif action in {"start_pcv_processing", "pause_pcv_processing", "resume_pcv_processing"} and doc.doctype == "Process Period Closing Voucher":
		from erpnext.accounts.doctype.process_period_closing_voucher import process_period_closing_voucher as pcv_module
		getattr(pcv_module, action)(doc.name)
		doc.reload()
	elif action in MAPPED_ACTIONS.get(doc.doctype, {}):
		return _run_mapped_action(doc, action, parameters)
	return {"name": doc.name, "docstatus": doc.docstatus, "modified": doc.modified, "route": _record_route(record, doc.name)}


@frappe.whitelist(methods=["GET"])
def get_workflow_actions(feature: str, name: str):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	from frappe.model.workflow import get_transitions, get_workflow_name
	if not get_workflow_name(doc.doctype):
		return {"actions": []}
	return {"actions": [{"action": row.action, "next_state": row.next_state, "allowed": row.allowed} for row in (get_transitions(doc) or [])]}


@frappe.whitelist(methods=["POST"])
def run_workflow_action(feature: str, name: str, action: str, modified: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name, "write")
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it."), frappe.TimestampMismatchError)
	from frappe.model.workflow import apply_workflow, get_transitions, get_workflow_name
	if not get_workflow_name(doc.doctype):
		frappe.throw(_("Workflow action is not available."), frappe.PermissionError)
	if action not in {row.action for row in (get_transitions(doc) or [])}:
		frappe.throw(_("Workflow action is not available."), frappe.PermissionError)
	updated = apply_workflow(doc, action)
	return {"name": updated.name, "docstatus": updated.docstatus, "modified": updated.modified}


@frappe.whitelist(methods=["GET"])
def get_link_options(feature: str, fieldname: str, search: str = "", parent_fieldname: str | None = None, dynamic_doctype: str | None = None):
	_require_login()
	_record, meta, readable, _writable = _metadata(feature)
	field = meta.get_field(fieldname)
	if parent_fieldname:
		parent = meta.get_field(parent_fieldname)
		child_meta = frappe.get_meta(parent.options) if parent and parent.fieldtype in {"Table", "Table MultiSelect"} else None
		child_readable = {
			item.fieldname for item in _readable_fields(child_meta, _permlevels(meta, "read"))
		} if child_meta else set()
		field = child_meta.get_field(fieldname) if child_meta and fieldname in child_readable else None
	readable_names = {item.fieldname for item in readable}
	if not field or (not parent_fieldname and fieldname not in readable_names) or field.fieldtype not in {"Link", "Dynamic Link"} or not field.options:
		frappe.throw(_("Link field is not available."), frappe.PermissionError)
	target_doctype = field.options if field.fieldtype == "Link" else str(dynamic_doctype or "").strip()
	if field.fieldtype == "Dynamic Link":
		context_meta = frappe.get_meta(parent.options) if parent_fieldname and parent else meta
		type_field = context_meta.get_field(field.options)
		if not type_field or not target_doctype or not frappe.db.exists("DocType", target_doctype):
			frappe.throw(_("Link field is not available."), frappe.PermissionError)
		if type_field.fieldtype == "Select" and target_doctype not in [value for value in (type_field.options or "").splitlines() if value]:
			frappe.throw(_("Link field is not available."), frappe.PermissionError)
	if not frappe.has_permission(target_doctype, "read"):
		frappe.throw(_("Link field is not available."), frappe.PermissionError)
	meta_target = frappe.get_meta(target_doctype)
	search = (search or "").strip()[:140]
	search_fields = ["name", meta_target.title_field] + [value.strip() for value in (meta_target.search_fields or "").split(",") if value.strip()]
	or_filters = [
		[name, "like", f"%{search}%"]
		for name in dict.fromkeys(search_fields)
		if name and (name == "name" or meta_target.has_field(name))
	] if search else []
	fields = ["name"] + ([meta_target.title_field] if meta_target.title_field and meta_target.has_field(meta_target.title_field) else [])
	rows = frappe.get_list(
		target_doctype, fields=fields, or_filters=or_filters, order_by="modified desc",
		limit_page_length=LINK_RESULT_LIMITS.get(target_doctype, MAX_LINK_RESULTS),
	)
	return {"results": [{"value": row.name, "label": row.get(meta_target.title_field) or row.name} for row in rows]}


@frappe.whitelist(methods=["GET"])
def get_related_documents(feature: str, name: str):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	# The generic foundation exposes only permission-filtered Dynamic Link records.
	rows = frappe.get_list("Dynamic Link", filters={"link_doctype": doc.doctype, "link_name": doc.name}, fields=["parenttype", "parent"], limit_page_length=50)
	result = []
	seen = set()
	for row in rows:
		if row.parenttype in ALL_GENERATED_DOCTYPES and frappe.has_permission(row.parenttype, "read") and frappe.get_list(row.parenttype, filters={"name": row.parent}, pluck="name", limit_page_length=1):
			target = get_feature(frappe.scrub(row.parenttype).replace("_", "-"))
			result.append({"doctype": row.parenttype, "name": row.parent, "route": _record_route(target, row.parent)})
			seen.add((row.parenttype, row.parent))
	# Address and Contact store their outward links in their own Dynamic Link
	# child table.  Expose those same standard "Links" buttons only when the
	# target type is routed and the target document remains readable.
	for link in doc.get("links") or []:
		key = (link.link_doctype, link.link_name)
		if key in seen or link.link_doctype not in ALL_GENERATED_DOCTYPES:
			continue
		if not frappe.has_permission(link.link_doctype, "read") or not frappe.get_list(
			link.link_doctype, filters={"name": link.link_name}, pluck="name", limit_page_length=1,
		):
			continue
		target = get_feature(frappe.scrub(link.link_doctype).replace("_", "-"))
		result.append({"doctype": link.link_doctype, "name": link.link_name, "route": _record_route(target, link.link_name)})
		seen.add(key)
	return {"records": result}


@frappe.whitelist(methods=["GET"])
def get_dashboard_connections(feature: str, name: str):
	"""Generic "Connections" panel (the standard ERPNext Desk sidebar showing
	linked Purchase Orders / Sales Orders / Payment Entries / etc.), reusing
	each doctype's own `<doctype>_dashboard.py:get_data()` config — the exact
	same source frappe.desk.notifications.get_open_count reads — instead of
	hardcoding per-doctype link logic. Counts and record lists are computed
	here directly (not by calling get_open_count) so every linked doctype can
	be permission-rechecked and filtered down to only doctypes this app
	actually routes to, before any count or name is returned."""
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	meta = frappe.get_meta(doc.doctype)
	dashboard = meta.get_dashboard_data()
	non_standard = dashboard.get("non_standard_fieldnames") or {}
	internal_links = dashboard.get("internal_links") or {}
	default_fieldname = dashboard.get("fieldname") or frappe.scrub(doc.doctype)

	groups = []
	for group in dashboard.get("transactions") or []:
		items = []
		for linked_doctype in group.get("items") or []:
			if linked_doctype not in ALL_GENERATED_DOCTYPES or not frappe.has_permission(linked_doctype, "read"):
				continue
			linked_meta = frappe.get_meta(linked_doctype)
			names: list[str] = []
			if linked_doctype in internal_links:
				child_fieldname, link_fieldname = internal_links[linked_doctype]
				for row in doc.get(child_fieldname) or []:
					value = row.get(link_fieldname)
					if value and value not in names:
						names.append(value)
			else:
				fieldname = non_standard.get(linked_doctype) or default_fieldname
				if not linked_meta.has_field(fieldname):
					continue
				names = frappe.get_list(linked_doctype, filters={fieldname: doc.name}, pluck="name", limit_page_length=20)
			if not names:
				continue
			# Defend against stale/renamed references: only surface names that
			# still exist and are still readable.
			existing = set(frappe.get_list(linked_doctype, filters={"name": ["in", names]}, pluck="name", limit_page_length=len(names)))
			names = [n for n in names if n in existing]
			if not names:
				continue
			target = get_feature(frappe.scrub(linked_doctype).replace("_", "-"))
			items.append({
				"doctype": linked_doctype,
				"count": len(names),
				"records": [{"name": n, "route": _record_route(target, n)} for n in names[:5]],
			})
		if items:
			groups.append({"label": group.get("label"), "items": items})
	return {"groups": groups}


@frappe.whitelist(methods=["GET"])
def get_document_timeline(feature: str, name: str):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	rows = frappe.get_list("Comment", filters={"reference_doctype": doc.doctype, "reference_name": doc.name, "comment_type": ["in", ["Comment", "Info", "Edit"]]}, fields=["name", "comment_type", "content", "owner", "creation"], order_by="creation desc", limit_page_length=MAX_TIMELINE_ROWS)
	return {"records": rows}


@frappe.whitelist(methods=["GET"])
def get_print_formats(feature: str, name: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	if name:
		_get_permitted_doc(record["doctype"], name)
	if not frappe.has_permission(record["doctype"], "print"):
		frappe.throw(_("Print is not available."), frappe.PermissionError)
	formats = frappe.get_list("Print Format", filters={"doc_type": record["doctype"], "disabled": 0}, pluck="name", order_by="name asc")
	letterheads = []
	if frappe.has_permission("Letter Head", "read"):
		letterheads = frappe.get_list("Letter Head", filters={"disabled": 0}, fields=["name", "is_default"], order_by="is_default desc, name asc", limit_page_length=100)
	language = frappe.local.lang or frappe.db.get_default("lang") or "en"
	base = {"doctype": record["doctype"], "name": name or ""}
	return {
		"formats": ["Standard", *formats], "letterheads": letterheads,
		"languages": [{"value": language, "label": language}], "default_language": language,
		"print_url": f"/printview?{urlencode(base)}" if name else None,
		"pdf_url": f"/api/method/frappe.utils.print_format.download_pdf?{urlencode(base)}" if name else None,
		"pdf_environment": {"available": bool(shutil.which("wkhtmltopdf")), "generator": "wkhtmltopdf", "installation_required": not bool(shutil.which("wkhtmltopdf"))},
	}


def _special_definition(feature: str, expected_type: str) -> tuple[dict, Any]:
	record = get_feature(feature)
	if record.get("category") != expected_type or not feature_is_permitted(record):
		frappe.throw(_("Feature is not available."), frappe.PermissionError)
	name = record.get(expected_type) or record.get("feature_label")
	return record, name


@frappe.whitelist(methods=["GET"])
def get_report_definition(feature: str):
	_require_login()
	record, name = _special_definition(feature, "report")
	from frappe.desk.query_report import get_report_doc
	report = get_report_doc(name)
	return {"feature": _public_feature(record), "name": report.name, "report_type": report.report_type, "reference_doctype": report.ref_doctype, "prepared_report": bool(report.prepared_report), "custom_filters": report.get("custom_filters") or [], "client_filter_policy": "not_executed"}


@frappe.whitelist(methods=["POST"])
def run_report(feature: str, filters: Any = None):
	_require_login()
	record, name = _special_definition(feature, "report")
	from frappe.desk.query_report import run
	return run(name, filters=_parse(filters or {}, dict, "Filters"), ignore_prepared_report=False)


@frappe.whitelist(methods=["GET"])
def get_workspace_definition(feature: str):
	_require_login()
	record, name = _special_definition(feature, "workspace")
	workspace = frappe.get_doc("Workspace", name)
	# Workspace JSON can contain targets the user cannot read.  A later adapter
	# will resolve each block independently; never return raw content meanwhile.
	return {"feature": _public_feature(record), "name": workspace.name, "title": workspace.title, "module": workspace.module, "status": "permission_filtered_adapter_required"}


@frappe.whitelist(methods=["GET"])
def get_dashboard_definition(feature: str):
	_require_login()
	record = get_feature(feature)
	if record.get("category") not in {"dashboard", "dashboard_chart", "number_card"} or not feature_is_permitted(record):
		frappe.throw(_("Dashboard is not available."), frappe.PermissionError)
	return {"feature": _public_feature(record), "status": "special_adapter_required"}
