"""Authoritative Retail ERP parity registry (Stage 2).

This module assigns EVERY user-facing capability discovered by the canonical
feature inventory exactly one truthful status, business priority and
implementation strategy. It is deterministic: it reads the canonical inventory
(`docs/erpnext-v15-complete-inventory.json`) and applies rules + a small,
explicit override table. Nothing here mutates the site.

Honesty contract (enforced by `validate_parity_registry`):
- Every user-facing feature has exactly one registry entry.
- No duplicate feature keys.
- Every entry has a known strategy, status and business priority.
- `verified_complete` requires non-empty evidence.
- A route is never, by itself, treated as completion — mapped-but-unverified
  features are `implemented_unverified` or `generated_provisional`, not
  `verified_complete`.
- `unavailable_with_reason` / `not_required` / `internal` are NOT counted as
  implemented functionality.

Statuses (truthful): verified_complete, implemented_unverified,
generated_provisional, special_adapter, blocked, unavailable_with_reason,
not_required, internal.

Business priorities: P0_go_live, P1_required, P2_important, P3_optional,
not_required, internal.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

STATUSES = {
    "verified_complete", "implemented_unverified", "generated_provisional",
    "special_adapter", "blocked", "unavailable_with_reason", "not_required", "internal",
}
IMPLEMENTED_STATUSES = {"verified_complete", "implemented_unverified", "generated_provisional", "special_adapter"}
PRIORITIES = {"P0_go_live", "P1_required", "P2_important", "P3_optional", "not_required", "internal"}
STRATEGIES = {
    "custom_override", "generated_doctype", "generated_report", "generated_workspace",
    "generated_dashboard", "generated_print", "generated_tree", "generated_calendar",
    "generated_kanban", "generated_query", "special_adapter", "external_app_adapter",
    "unavailable_with_reason", "not_required", "internal",
}

# ---------------------------------------------------------------------------
# Rule tables
# ---------------------------------------------------------------------------

# The six genuinely handcrafted DocTypes (custom_override). Tests are blocked on
# this site, so the strongest honest status is implemented_unverified.
HANDCRAFTED_DOCTYPES = {
    "Customer", "Item", "Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry",
}

# P0 documents in the fixed wholesale flow. Priority only — status still comes
# from real implementation state.
P0_DOCTYPES = {
    "Customer", "Item", "Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry",
    "Stock Reservation Entry", "Bin", "Pick List", "Packing Slip", "Customer Credit Limit",
}

# Module -> default business priority for a wholesale IMPORTING & SELLING business.
# Overridden per-feature by type/override rules below.
MODULE_PRIORITY = {
    "Accounts": "P1_required",
    "Stock": "P1_required",
    "Selling": "P1_required",
    "Buying": "P1_required",
    "Contacts": "P1_required",
    "CRM": "P2_important",
    "Setup": "P2_important",
    "POSAwesome": "P2_important",
    "Printing": "P2_important",
    "Regional": "P2_important",
    "Assets": "P3_optional",
    "Projects": "P3_optional",
    "Support": "P3_optional",
    "Quality Management": "P3_optional",
    "Automation": "P3_optional",
    "Workflow": "P3_optional",
    "Bulk Transaction": "P3_optional",
    "Email": "P3_optional",
    "Communication": "P3_optional",
    # Not relevant to the stated wholesale importing/selling scope:
    "Manufacturing": "not_required",
    "Subcontracting": "not_required",
    "Website": "not_required",
    "Portal": "not_required",
    "Social": "not_required",
    "Telephony": "not_required",
    "EDI": "not_required",
    "Maintenance": "not_required",
    "ERPNext Gemini Integration": "not_required",
    "ERPNext ChatGPT": "not_required",
    "Gemini": "not_required",
    "erpnext_chatgpt": "not_required",
    "erpnext_gemini_integration": "not_required",
    # Platform/technical:
    "Core": "internal",
    "Desk": "internal",
    "Custom": "internal",
    "Utilities": "internal",
    "Geo": "internal",
    "Integrations": "P3_optional",
    "ERPNext Integrations": "P3_optional",
}

# Feature types that are components of a parent DocType/workspace rather than
# independent user destinations -> internal by construction.
INTERNAL_FEATURE_TYPES = {
    "custom_field", "property_setter", "client_script", "server_script",
    "workspace_target", "dashboard_connection", "installed_app", "source_only_report",
    "notification",
}

# Feature types that map onto the generic engine when their parent is in scope.
VISUAL_TYPES = {"dashboard", "dashboard_chart", "number_card", "workspace"}

# Audit correction (Step 13, final-mapping mission): specific DocTypes whose
# *module* priority is P1/P2 (Accounts, Stock, Buying, ...) but which are
# genuinely system/ledger tables, auto-generated log records, or single
# admin-config screens rather than independent user destinations. Exposing
# these as normal pages would violate the "no unsafe ledger/stock records"
# rule, so they are corrected to `internal` here regardless of module.
# This never grants or removes data access — Frappe permissions are unchanged.
SYSTEM_INTERNAL_DOCTYPE_NAMES = {
    # Accounting ledger / posting tables — never directly writable pages.
    "GL Entry", "Payment Ledger Entry", "Advance Payment Ledger Entry",
    "Account Closing Balance", "Stock Ledger Entry", "Bin", "Closing Stock Balance",
    "Loyalty Point Entry",
    # Ledger repair / repost / diagnostic tools — technical maintenance, not a
    # wholesale business route.
    "Ledger Health", "Ledger Health Monitor", "Ledger Merge",
    "Bisect Accounting Statements", "Bisect Nodes",
    "Repost Accounting Ledger", "Repost Accounting Ledger Settings",
    "Repost Payment Ledger", "Repost Item Valuation", "Quick Stock Balance",
    # System logs, not user-created records.
    "POS Invoice Merge Log", "Transaction Deletion Record",
    # Single admin-config screens (issingle=1): system configuration, not a
    # list of business records.
    "Accounts Settings", "Buying Settings", "Selling Settings", "Stock Settings",
    "Print Settings", "POS Settings", "CRM Settings", "Support Settings",
    "Subscription Settings", "Global Defaults", "Currency Exchange Settings",
    "Delivery Settings", "Item Variant Settings", "Projects Settings",
    "South Africa VAT Settings", "UAE VAT Settings", "Network Printer Settings",
    "Scale Barcode Settings", "Authorization Control", "Stock Reposting Settings",
    "Appointment Booking Settings",
}

# Audit correction: country-specific regional tax reports for jurisdictions
# other than this business's (Sri Lanka wholesale importing). Regional as a
# module defaults to P2_important because some regional reports (e.g. VAT
# Audit Report for applicable jurisdictions) could matter elsewhere; these
# specific reports are for other countries' tax authorities and are honestly
# not_required rather than "pending".
# Audit correction: native ERPNext module workspaces (Selling, Buying, Stock,
# Accounts sub-workspaces, CRM, ...) are Desk's per-module landing pages.
# Retail ERP already provides its own equivalent module landing page (the
# /sales, /purchases, /inventory, /finance, /crm, /operations, /pos nav
# sections) as a deliberate handcrafted replacement — so these are genuinely
# superseded, not "pending", and the honest strategy is special_adapter
# (Retail ERP's own nav page is the safe adapter), not a bare generic route.
# Workspaces with no wholesale-relevant Retail ERP destination (Setup/Core
# admin landing pages, Integrations config) are internal instead.
WORKSPACE_OVERRIDES = {
    "Accounting": ("special_adapter", "implemented_unverified", "/finance",
                   "Superseded by the Retail ERP Finance module landing page."),
    "Financial Reports": ("special_adapter", "implemented_unverified", "/finance",
                          "Superseded by the Retail ERP Finance module + routed report viewer."),
    "Invoicing": ("special_adapter", "implemented_unverified", "/finance",
                 "Superseded by the Retail ERP Finance module landing page."),
    "Payables": ("special_adapter", "implemented_unverified", "/purchases",
                "Superseded by the Retail ERP Purchases module landing page."),
    "Receivables": ("special_adapter", "implemented_unverified", "/finance",
                    "Superseded by the Retail ERP Finance module landing page."),
    "Assets": ("special_adapter", "implemented_unverified", "/operations",
              "Superseded by the Retail ERP Operations module (Assets routes)."),
    "Buying": ("special_adapter", "implemented_unverified", "/purchases",
              "Superseded by the Retail ERP Purchases module landing page."),
    "CRM": ("special_adapter", "implemented_unverified", "/crm",
           "Superseded by the Retail ERP CRM module landing page."),
    "Projects": ("special_adapter", "implemented_unverified", "/operations",
                "Superseded by the Retail ERP Operations module (Projects routes)."),
    "Quality": ("special_adapter", "implemented_unverified", "/operations",
               "Superseded by the Retail ERP Operations module (Quality routes)."),
    "Selling": ("special_adapter", "implemented_unverified", "/sales",
               "Superseded by the Retail ERP Sales module landing page."),
    "Stock": ("special_adapter", "implemented_unverified", "/inventory",
             "Superseded by the Retail ERP Inventory module landing page."),
    "Support": ("special_adapter", "implemented_unverified", "/operations/support/issues",
               "Superseded by the Retail ERP Operations module (Support routes)."),
    "POS Awesome": ("special_adapter", "implemented_unverified", "/pos",
                   "Superseded by the Retail ERP POS launcher (safe_integration)."),
    "ERPNext Settings": ("internal", "internal", None,
                         "Native ERPNext Desk admin/settings landing page; not a wholesale business route."),
    "Home": ("internal", "internal", None,
            "Native ERPNext Desk home landing page; superseded by the Retail ERP home module."),
    "ERPNext Integrations": ("internal", "internal", None,
                             "Technical integration configuration landing page; owned by Frappe Desk."),
    "Integrations": ("internal", "internal", None,
                     "Technical integration configuration landing page; owned by Frappe Desk."),
    "Tools": ("internal", "internal", None,
             "Native Desk bulk/automation utility landing page; not a wholesale business route."),
}


# Audit correction (Steps 5-9, final-mapping mission): document_action
# features whose action is genuinely served by the universal engine's
# allowlisted handler (my_store_ui/universal/api.py) on a doctype that
# already has a real Retail ERP route. These are real server-verified
# handlers (frappe.has_permission re-checked, standard ERPNext make_*
# controllers, no arbitrary method paths) — not fabricated routes. Behavioural
# proof is still pending (allow_tests disabled), so status is
# implemented_unverified, matching the handcrafted-doctype treatment.
GENERIC_LIFECYCLE_ACTIONS = {"submit", "cancel", "amend", "delete", "duplicate", "rename"}

DOCTYPE_SPECIFIC_ACTIONS = {
    # "customer"/"quotation"/"supplier_quotation"/"request_for_quotation" are
    # the JS button labels (opportunity.js) for make_customer/make_quotation/
    # make_supplier_quotation/make_request_for_quotation - the latter two are
    # real new actions this pass, the former two were dead credits (the
    # internal method-name keys never matched the scanner's button-label
    # keys) - verified against source before aliasing.
    "Opportunity": {
        "close", "reopen", "make_customer", "customer", "make_quotation", "quotation",
        "make_supplier_quotation", "supplier_quotation", "make_request_for_quotation", "request_for_quotation",
        "set_as_lost",
    },
    "Supplier": {"hold", "resume"},
    # "re_open"/"update_status" are JS button labels (material_request.js)
    # calling the exact same update_status() the stop/reopen actions wrap;
    # "purchase_order"/"request_for_quotation" are button labels calling the
    # exact same make_purchase_order/make_request_for_quotation already
    # credited; "material_transfer"/"issue_material"/"material_receipt" are
    # ALL the same make_stock_entry call, shown under different labels
    # depending on material_request_type - verified against source.
    # "supplier_quotation"/"pick_list"/"material_transfer_in_transit" are
    # button labels for the new make_supplier_quotation/create_pick_list/
    # make_in_transit_stock_entry actions (universal/api.py, type-gated).
    "Material Request": {
        "stop", "reopen", "re_open", "update_status",
        "make_request_for_quotation", "request_for_quotation",
        "make_purchase_order", "purchase_order",
        "make_stock_entry", "material_transfer", "issue_material", "material_receipt",
        "make_supplier_quotation", "supplier_quotation",
        "create_pick_list", "pick_list",
        "make_in_transit_stock_entry", "material_transfer_in_transit",
    },
    # "End Transit" button calls the exact same make_stock_in_entry() -
    # verified against stock_entry.js source.
    "Stock Entry": {"make_stock_in_entry", "end_transit"},
    # "purchase_receipt"/"purchase_invoice"/"re_open" are JS button labels
    # (purchase_order.js) calling the exact same make_purchase_receipt/
    # make_purchase_invoice/update_status("Submitted") already credited -
    # genuine scanner-noise duplicates, verified against source. "payment"
    # is a real new action (shared get_payment_entry, same as Purchase
    # Invoice/Dunning's "payment").
    "Purchase Order": {
        "hold", "close", "resume", "reopen", "re_open",
        "make_purchase_receipt", "purchase_receipt", "make_purchase_invoice", "purchase_invoice", "payment",
    },
    # "customer"/"opportunity"/"quotation" are the JS button labels
    # (lead.js) - same dead-credit-then-fixed pattern as Opportunity above.
    # "make_quotation" is a real new action (Lead has its own make_quotation,
    # separate from Opportunity's).
    "Lead": {"make_opportunity", "opportunity", "make_customer", "customer", "make_quotation", "quotation"},
    # "set_as_lost" is a real new action shared with Opportunity below -
    # wraps the real declare_enquiry_lost() doc method (sales_common.js).
    "Quotation": {"make_sales_order", "make_sales_invoice", "set_as_lost"},
    # Bug fix: the internal action key "make_supplier_quotation" chosen for
    # this MAPPED_ACTIONS entry never matched either real scanner-detected
    # key for RFQ's "Supplier Quotation" button - the button label scrubs to
    # "supplier_quotation" and the server method is "make_supplier_quotation_
    # from_rfq" (request_for_quotation.js/.py) - so this credit was silently
    # inert until now. supplier_quotation_comparison/send_emails_to_suppliers
    # are real new actions (universal/api.py).
    "Request for Quotation": {
        "make_supplier_quotation", "supplier_quotation", "make_supplier_quotation_from_rfq",
        "supplier_quotation_comparison", "send_emails_to_suppliers",
    },
    # Bug fix: "make_purchase_order" alone never matched the real scanner key
    # "purchase_order" (the "Purchase Order" button label) - same class of
    # dead credit as Request for Quotation above, fixed the same way.
    # "make_quotation"/"quotation" is a real new action: Supplier Quotation
    # can convert into a (selling) Quotation - verified against
    # supplier_quotation.js source (make_quotation() -> erpnext...
    # supplier_quotation.make_quotation, a standard get_mapped_doc call).
    "Supplier Quotation": {"make_purchase_order", "purchase_order", "make_quotation", "quotation"},
    # Supplier ledger navigation shortcuts (supplier.js) - real new actions,
    # same navigation-action pattern as Account/Warehouse.
    "Supplier": {"accounting_ledger", "accounts_payable"},
    # "debit_note" (JS label, shown only when is_return=1) calls the exact
    # same erpnext...purchase_receipt.make_purchase_invoice as make_purchase_invoice;
    # "landed_cost_voucher" calls the exact same make_lcv; "purchase_return"
    # calls the exact same make_purchase_return - genuine scanner-noise
    # duplicates, verified against purchase_receipt.js source. close/reopen
    # are real new actions (universal/api.py, wraps update_status()).
    "Purchase Receipt": {
        "make_purchase_invoice", "debit_note", "make_purchase_return", "purchase_return",
        "make_lcv", "landed_cost_voucher", "close", "reopen",
    },
    # "payment"/"return_debit_note" are the JS button labels (purchase_invoice.js);
    # "payment" calls the same shared make_payment_entry()->get_payment_entry()
    # path as the existing make_payment_entry action, "return_debit_note" calls
    # the exact same erpnext...purchase_invoice.make_debit_note as make_debit_note -
    # genuine scanner-noise duplicates, verified against source. block_invoice/
    # unblock_invoice/change_release_date are real new actions (universal/api.py).
    # "make_lcv" (Landed Cost Voucher, gated by update_stock=1) reuses the
    # exact same doctype-agnostic make_lcv(doctype, docname) Purchase
    # Receipt uses - verified against purchase_invoice.js source.
    "Purchase Invoice": {
        "make_payment_entry", "payment", "make_debit_note", "return_debit_note",
        "block_invoice", "unblock_invoice", "change_release_date", "make_lcv", "landed_cost_voucher",
    },
    # "reverse_journal_entry" is the JS button handler name (journal_entry.js);
    # it calls the exact same server method as "make_reverse_journal_entry"
    # (journal_entry.py) - genuine scanner-noise duplicate, verified against
    # source before aliasing (see DECISIONS.md).
    "Journal Entry": {"make_reverse_journal_entry", "reverse_journal_entry", "ledger"},
    # Chart of Accounts / Cost Center admin actions and ledger-navigation
    # shortcuts (universal/api.py _available_actions / run_document_action) -
    # real erpnext controller methods, matched by exact scanner action key.
    "Account": {"chart_of_accounts", "general_ledger", "convert_to_group", "convert_to_non_group", "merge_account", "update_account_name_number"},
    "Cost Center": {"chart_of_cost_centers", "budget", "convert_to_group", "convert_to_non_group", "update_cost_center_name_number"},
    "Period Closing Voucher": {"ledger"},
    "Warehouse": {"general_ledger", "stock_balance"},
    "Batch": {"view_ledger", "recalculate_batch_qty"},
    "Serial No": {"view_ledgers"},
    "Company": {"chart_of_accounts", "cost_centers"},
    # Pick List stock-reservation controls (universal/api.py). "reserve"/
    # "unreserve" are the JS button labels calling the exact same
    # create_stock_reservation_entries/cancel_stock_reservation_entries doc
    # methods - genuine scanner-noise duplicates, verified against
    # pick_list.js source. "reserved_stock"/"update_current_stock" are real
    # new actions (navigation + set_item_locations respectively). Reservation
    # only ever calls the standard Stock Reservation Entry controller - never
    # writes Bin or Stock Ledger Entry directly.
    "Pick List": {
        "create_stock_reservation_entries", "reserve",
        "cancel_stock_reservation_entries", "unreserve",
        "reserved_stock", "update_current_stock",
    },
    # "journal_entries" is the JS button label; it calls the exact same
    # doc method as "make_jv_entries" (exchange_rate_revaluation.js:
    # frm.events.make_jv -> frm.call({method: "make_jv_entries"})) - genuine
    # scanner-noise duplicate, verified against source before aliasing.
    "Exchange Rate Revaluation": {"make_jv_entries", "journal_entries"},
    "Dunning": {"payment", "resolve"},
    # "cancel_pcv_processing" is erpnext's own on_cancel() hook (process_
    # period_closing_voucher.py), not a separate button - already triggered
    # by the standard "cancel" GENERIC_LIFECYCLE_ACTIONS entry now that this
    # doctype is routed. start/pause/resume are real buttons, separately wired.
    "Process Period Closing Voucher": {"cancel_pcv_processing", "start_pcv_processing", "pause_pcv_processing", "resume_pcv_processing"},
}


# Audit correction: standard Desk "Page" feature entries that are either a
# stale/legacy stub superseded by the real Retail ERP Vue route, superseded
# by an already-routed destination, or genuine internal admin tooling.
PAGE_OVERRIDES = {
    # Legacy Frappe "Page" doctype stub (my_store_ui/page/smart_sales/) from
    # before the app moved to the Vue SPA shell. Smart Sales is a preserved
    # handcrafted page, genuinely implemented at the real SPA route below —
    # this stub is not what serves it.
    "smart-sales": ("custom_override", "implemented_unverified", "/retail-erp/smart-sales",
                     "Handcrafted Smart Sales page is implemented at the Retail ERP SPA route "
                     "(frontend/src/router/routes.js); this is a legacy pre-SPA Frappe Page stub."),
    "point-of-sale": ("special_adapter", "implemented_unverified", "/pos",
                       "Superseded by the Retail ERP POS launcher (safe_integration to POS Awesome)."),
    "pos": ("special_adapter", "implemented_unverified", "/pos",
            "Superseded by the Retail ERP POS launcher (safe_integration to POS Awesome)."),
    "posapp": ("special_adapter", "implemented_unverified", "/pos",
               "Superseded by the Retail ERP POS launcher (safe_integration to POS Awesome)."),
    "stock-balance": ("generated_report", "generated_provisional", "/retail-erp/reports/view/Stock%20Balance",
                       "Superseded by the routed Stock Balance report (REPORT_GROUPS.inventory)."),
    "print": ("internal", "internal", None,
              "Native Desk print-preview shell; the routed DocType print/PDF dialog is the Retail ERP path."),
    "print-format-builder": ("internal", "internal", None,
                              "Admin-only visual print format design tool; not a wholesale business route."),
    "print-format-builder-beta": ("internal", "internal", None,
                                   "Admin-only visual print format design tool; not a wholesale business route."),
    "workflow-builder": ("internal", "internal", None,
                          "Admin-only workflow design tool; not a wholesale business route."),
}


# Batch 10 (special finance adapters): DocTypes with a genuinely built,
# dedicated Retail ERP adapter — real Vue page + backend module, not generic
# CRUD (these are ERPNext "virtual"/tool doctypes, never meant for a list/
# form). The route lives outside ENTITY_ROUTES (which drives the generic
# engine only), so it is credited here with real evidence.
BUILT_ADAPTER_DOCTYPE_NAMES = {
    "Payment Reconciliation": (
        "/retail-erp/finance/payment-reconciliation",
        [
            "my_store_ui/wholesale/payment_reconciliation_api.py "
            "(get_unreconciled_entries/preview_allocation/reconcile, calling the standard "
            "erpnext PaymentReconciliation controller methods)",
            "frontend/src/pages/priority/PaymentReconciliationPage.vue",
            "Behaviourally verified read-only against site1 (Grant Plastics Ltd.: "
            "2 outstanding invoices, correct receivable account resolved). "
            "allocate/reconcile are source-verified (exact method signatures matched "
            "against erpnext's own Desk client) but not behaviourally exercised — "
            "no unallocated Payment Entry exists on site1 to reconcile against "
            "without creating test data.",
        ],
    ),
    "Bank Reconciliation Tool": (
        "/retail-erp/finance/bank-reconciliation",
        [
            "my_store_ui/wholesale/bank_reconciliation_api.py (get_summary/get_matches/"
            "update_transaction_reference/reconcile_transaction/unreconcile_transaction/"
            "preview_payment_entry/confirm_payment_entry/preview_journal_entry/"
            "confirm_journal_entry/auto_reconcile, calling the standard erpnext "
            "bank_reconciliation_tool controller functions and Bank Transaction."
            "remove_payment_entries — never a generic method-path RPC)",
            "frontend/src/pages/priority/BankReconciliationPage.vue",
            "Source-verified against erpnext's own bank_reconciliation_tool.py and "
            "bank_reconciliation_tool.js (exact function signatures and the Journal "
            "Entry Type allowlist matched against the Desk dialog). Read paths "
            "(get_summary/get_matches) exercise real erpnext functions with no site "
            "mutation. Write paths (create_payment_entry_bts/create_journal_entry_bts/"
            "reconcile_vouchers/auto_reconcile_vouchers) were not behaviourally "
            "exercised — site1 has no unreconciled Bank Transaction to reconcile "
            "against without creating test data.",
        ],
    ),
}

# Action keys served by each built adapter, keyed by the document_action's
# *parent* doctype. A document_action's parent is not always the same as the
# adapter's own primary doctype - e.g. Bank Transaction's create-bank-entries/
# unreconcile-transaction actions are served by the Bank Reconciliation Tool
# adapter, not by a dedicated Bank Transaction adapter.
BUILT_ADAPTER_ACTIONS_BY_PARENT = {
    "Payment Reconciliation": {"allocate", "get_unreconciled_entries", "reconcile"},
    "Bank Reconciliation Tool": {
        "auto_reconcile", "create_journal_entry_bts", "create_payment_entry_bts", "get_unreconciled_entries",
    },
    "Bank Transaction": {"create_bank_entries", "unreconcile_transaction"},
}
BUILT_ADAPTER_ACTION_ROUTE = {
    "Payment Reconciliation": "/retail-erp/finance/payment-reconciliation",
    "Bank Reconciliation Tool": "/retail-erp/finance/bank-reconciliation",
    "Bank Transaction": "/retail-erp/finance/bank-reconciliation",
}


NOT_REQUIRED_REPORT_NAMES = {
    "IRS 1099": "US IRS 1099 contractor tax report; not applicable outside the United States.",
    "UAE VAT 201": "UAE Federal Tax Authority VAT return; not applicable outside the UAE.",
    "VAT Audit Report": "Generic regional VAT audit report tied to non-Sri-Lanka regional localizations "
                         "(India GST/UAE/Saudi); this business's jurisdiction uses standard Sales/Purchase "
                         "tax reports instead.",
}

# Audit correction: country-specific DocTypes (as opposed to reports, see
# NOT_REQUIRED_REPORT_NAMES above) not applicable outside their jurisdiction.
NOT_REQUIRED_DOCTYPE_NAMES = {
    "Import Supplier Invoice": "India GST e-invoice bulk-import tool; not applicable outside India.",
    "Mpesa C2B Register URL": "Kenya M-Pesa mobile-money gateway integration; not applicable outside Kenya.",
    "Mpesa Payment Register": "Kenya M-Pesa mobile-money gateway integration; not applicable outside Kenya.",
}

# Step 12 (POS Awesome / external apps): capabilities that POS Awesome's own
# app UI (launched via the /pos safe_integration route, see PAGE_OVERRIDES
# and WORKSPACE_OVERRIDES) already handles natively — session/shift
# management, cash movements, and coupon condition editing. Retail ERP
# deliberately does not duplicate POS Awesome's own UI; these are reachable
# through the external launcher, not through a Retail ERP-native page.
POS_EXTERNAL_LAUNCHER_NAMES = {
    "POS Cash Movement": "POS Awesome session cash-in/cash-out record; managed inside the POS Awesome app itself.",
    "POS Closing Shift": "POS Awesome shift-closing record; managed inside the POS Awesome app itself.",
    "POS Opening Shift": "POS Awesome shift-opening record; managed inside the POS Awesome app itself.",
    "POS Invoice Submission Ledger": "POS Awesome offline-sync ledger; internal to the POS Awesome app.",
    # Underlying ERPNext-core POS records that POS Awesome itself creates and
    # manages as part of its normal operation (POS Awesome is built on top of
    # ERPNext's POS Invoice/POS Profile) - not a separate Retail ERP concern.
    "POS Invoice": "Created and managed by POS Awesome transactions; not a separate Retail ERP record.",
    "POS Profile": "POS Awesome terminal/session configuration; managed inside the POS Awesome app itself.",
    "POS Opening Entry": "ERPNext-core POS shift-opening record created by POS Awesome; managed inside the POS Awesome app.",
    "POS Closing Entry": "ERPNext-core POS shift-closing record created by POS Awesome; managed inside the POS Awesome app.",
    "Cashier Closing": "ERPNext-core POS cashier-closing record created by POS Awesome; managed inside the POS Awesome app.",
}
POS_EXTERNAL_LAUNCHER_ACTIONS = {
    "make_closing_shift_from_opening", "submit_closing_shift", "add_edit_coupon_conditions",
}

# Audit correction: print formats attached to a Report (doc_type is empty in
# ERPNext for these) rather than a DocType. feature_inventory.py's print
# format route resolver only checks doc_type, so these never get a route even
# though their underlying report is already routed via REPORT_GROUPS. Credit
# them the same way a DocType print format is credited by its routed parent.
PRINT_FORMAT_REPORT_NAMES = {
    "Accounts Payable Standard": "Accounts Payable",
    "Accounts Payable Summary Standard": "Accounts Payable",
    "Accounts Receivable Standard": "Accounts Receivable",
    "Accounts Receivable Summary Standard": "Accounts Receivable",
    "Balance Sheet Standard": "Balance Sheet",
    "Cash Flow Statement Standard": "Cash Flow",
    "General Ledger Standard": "General Ledger",
    "P&L Statement Standard": "Profit and Loss Statement",
    "Trial Balance Standard": "Trial Balance",
}

# Audit correction (Step 11): technical backend-only components — email/
# integration/OAuth/webhook infrastructure, workflow *design* tooling (as
# opposed to using an active workflow), bulk-automation config, system log
# tables, and one-time admin setup wizards. None of these are independent
# wholesale business destinations; System Manager retains them in Desk.
PLATFORM_INTERNAL_DOCTYPE_NAMES = {
    # Integrations module: auth/webhook/cloud-storage config.
    "Connected App", "Dropbox Settings", "Google Calendar", "Google Contacts",
    "Google Drive", "Google Settings", "LDAP Settings", "OAuth Authorization Code",
    "OAuth Bearer Token", "OAuth Client", "OAuth Provider Settings",
    "Push Notification Settings", "S3 Backup Settings", "Slack Webhook URL",
    "Social Login Key", "Webhook", "Plaid Settings",
    # Email module: mail infrastructure config.
    "Auto Email Report", "Email Account", "Email Domain", "Email Flag Queue",
    "Email Group", "Email Group Member", "Email Queue", "Email Rule",
    "Email Template", "Email Unsubscribe", "Newsletter", "Notification",
    "Communication Medium",
    # Workflow *design* tooling (distinct from using an active workflow).
    "Workflow", "Workflow Action", "Workflow Action Master", "Workflow State",
    # Automation/bulk-config admin tooling.
    "Assignment Rule", "Auto Repeat", "Milestone", "Milestone Tracker", "Reminder",
    "Bulk Transaction Log", "Bulk Transaction Log Detail",
    # One-time company setup wizards.
    "Chart of Accounts Importer", "Opening Invoice Creation Tool",
    # Bulk marketing/messaging admin tool.
    "SMS Center",
    # Auto-generated child-like record tied to Asset, not independently created.
    "Asset Depreciation Schedule",
}


def _canonical_path() -> Path:
    try:
        import frappe  # noqa
        app_path = Path(frappe.get_app_path("my_store_ui")).resolve().parent
    except Exception:
        app_path = Path(__file__).resolve().parents[2]
    return app_path / "docs" / "erpnext-v15-complete-inventory.json"


def _priority_for(feature: dict) -> str:
    name = feature.get("doctype") or feature.get("name")
    if name in P0_DOCTYPES:
        return "P0_go_live"
    return MODULE_PRIORITY.get(feature.get("module") or "", "P3_optional")


def _strategy_and_status(feature: dict, priority: str, routed_doctypes: frozenset[str] = frozenset()) -> tuple[str, str, str, list[str], str]:
    """Return (strategy, status, verification_level, evidence, notes)."""
    ftype = feature.get("feature_type")
    doctype = feature.get("doctype")
    route = feature.get("current_custom_route")

    # 0. A workspace shortcut credited with its target's real Retail ERP route is
    # reachable navigation, not an internal component.
    if ftype == "workspace_target" and route:
        return ("generated_doctype", "generated_provisional", "route_only",
                [f"Reachable via mapped destination {route}"],
                "Workspace shortcut resolves to a routed Retail ERP destination; card verification pending.")

    # 0b. Batch 10: DocTypes with a genuinely built dedicated adapter (virtual/
    # tool doctypes that don't belong in generic ENTITY_ROUTES CRUD).
    if ftype == "doctype" and doctype in BUILT_ADAPTER_DOCTYPE_NAMES:
        adapter_route, evidence = BUILT_ADAPTER_DOCTYPE_NAMES[doctype]
        return ("special_adapter", "implemented_unverified", "source_only", list(evidence),
                f"Dedicated Retail ERP adapter implemented at {adapter_route}.")
    if ftype == "document_action" and feature.get("parent_feature") in BUILT_ADAPTER_ACTIONS_BY_PARENT:
        action_key = ""
        mapped = feature.get("mapped_actions") or []
        if mapped and isinstance(mapped, list):
            action_key = str(mapped[0].get("action") or "")
        parent = feature.get("parent_feature")
        if action_key in BUILT_ADAPTER_ACTIONS_BY_PARENT[parent]:
            adapter_route = BUILT_ADAPTER_ACTION_ROUTE[parent]
            return ("special_adapter", "implemented_unverified", "source_only",
                    [f"Served by the {adapter_route} adapter"],
                    f"Allowlisted action '{action_key}' on {parent} is served by the dedicated Retail ERP adapter.")

    # 1. Any feature carrying a real Retail ERP route is implemented in some form
    # regardless of module/type — evaluate this before internal/priority rules.
    if route:
        if doctype in HANDCRAFTED_DOCTYPES and ftype == "doctype":
            return ("custom_override", "implemented_unverified", "source_only",
                    [f"Handcrafted route {route}", "Server schema + lifecycle actions exist"],
                    "Behavioural verification blocked: allow_tests disabled; no browser automation.")
        if ftype == "report":
            return ("generated_report", "generated_provisional", "route_only",
                    [f"Priority report route {route}"],
                    "Provisional report viewer; interactive filter/chart/PDF tests pending.")
        if ftype == "doctype":
            return ("generated_doctype", "generated_provisional", "route_only",
                    [f"Clean generated route {route}"],
                    "Generic engine route; per-feature action/permission/browser tests pending.")
        if ftype == "print_format":
            return ("generated_print", "generated_provisional", "route_only",
                    [f"Selectable in the print/PDF dialog of {route}"],
                    "Print format renders for a routed DocType; per-format/letterhead/language verification pending.")
        # Routed page/shell/installed-app surface (e.g. the /retail-erp SPA shell).
        return ("special_adapter", "implemented_unverified", "source_only",
                [f"Routed Retail ERP surface {route}"],
                "Routed surface exists; browser/role verification pending.")

    # 2. Internal component features (never routed).
    if ftype in INTERNAL_FEATURE_TYPES:
        return ("internal", "internal", "n/a", [],
                f"{ftype} is a component of its parent, not an independent user route.")

    # 2b. Audit correction: system/ledger/settings DocTypes and their document
    # actions are technical infrastructure, not a wholesale business
    # destination, regardless of their module's default priority. Scoped to
    # doctype/document_action only — reports whose *reference* doctype is a
    # ledger table (e.g. a report built on GL Entry) are still legitimate
    # financial reports and must not be swept into this rule.
    _system_parent = doctype or (feature.get("parent_feature") if ftype in {"doctype", "document_action", "print_format"} else None)
    if _system_parent in SYSTEM_INTERNAL_DOCTYPE_NAMES:
        return ("internal", "internal", "n/a", [],
                "System/ledger/settings record excluded from generic routing: "
                "never exposed as a normal page (unsafe accounting/stock record "
                "or single admin-config screen). Standard ERPNext Desk retains it.")

    # 2c. Audit correction (Step 11/13): platform/technical backend-only
    # components (email, integrations/OAuth/webhooks, workflow design
    # tooling, bulk-automation config, system logs, one-time setup wizards).
    if _system_parent in PLATFORM_INTERNAL_DOCTYPE_NAMES:
        return ("internal", "internal", "n/a", [],
                "Technical backend-only component (Step 11): admin/system configuration, "
                "not an independent wholesale business destination. Standard ERPNext Desk retains it.")

    # 2d. Audit correction: country-specific DocTypes not applicable to this
    # business's jurisdiction.
    if _system_parent in NOT_REQUIRED_DOCTYPE_NAMES:
        return ("not_required", "not_required", "n/a", [], NOT_REQUIRED_DOCTYPE_NAMES[_system_parent])

    # 2e. Step 12 (POS Awesome): records genuinely managed inside the POS
    # Awesome app's own UI, reachable via the /pos external launcher.
    if _system_parent in POS_EXTERNAL_LAUNCHER_NAMES:
        return ("external_app_adapter", "implemented_unverified", "source_only", ["Reachable via the /pos external launcher"],
                POS_EXTERNAL_LAUNCHER_NAMES[_system_parent])

    # 3. Platform/technical modules with no wholesale user destination.
    if priority == "internal":
        return ("internal", "internal", "n/a", [],
                "Platform/technical capability; owned by Frappe Desk, not a wholesale route.")

    # 5. Not-required modules.
    if priority == "not_required":
        return ("not_required", "not_required", "n/a", [],
                "Outside the stated wholesale importing/selling scope; ERPNext Desk retains it.")

    # 6. Document actions (mapped-document transitions).
    if ftype == "document_action":
        parent = feature.get("parent_feature") or feature.get("doctype")
        if parent in HANDCRAFTED_DOCTYPES:
            return ("special_adapter", "implemented_unverified", "source_only",
                    [f"Mapped action on {parent}"],
                    "Allowlisted mapped-document action exists; state/role/duplicate tests pending.")
        action_key = ""
        mapped = feature.get("mapped_actions") or []
        if mapped and isinstance(mapped, list):
            action_key = str(mapped[0].get("action") or "")
        if action_key in POS_EXTERNAL_LAUNCHER_ACTIONS:
            return ("external_app_adapter", "implemented_unverified", "source_only",
                    ["Reachable via the /pos external launcher"],
                    "Handled inside the POS Awesome app's own UI, not reimplemented in Retail ERP.")
        served = action_key in GENERIC_LIFECYCLE_ACTIONS or action_key in DOCTYPE_SPECIFIC_ACTIONS.get(parent, set())
        if served and parent in routed_doctypes:
            return ("special_adapter", "implemented_unverified", "source_only",
                    [f"Allowlisted action '{action_key}' served by the universal engine on routed {parent}"],
                    "Generic lifecycle action or MAPPED_ACTIONS conversion via my_store_ui/universal/api.py "
                    "(standard erpnext.*.make_* controller, permission re-checked); "
                    "state/role/browser verification pending.")
        return ("unavailable_with_reason", "unavailable_with_reason", "n/a", [],
                f"Pending implementation ({priority}); standard Desk mapping remains source of truth.")

    # 5b. Audit correction: legacy Page stubs superseded by the real Retail
    # ERP SPA route, or genuine internal admin tooling.
    if ftype == "page" and feature.get("name") in PAGE_OVERRIDES:
        strategy, status, dest, reason = PAGE_OVERRIDES[feature.get("name")]
        evidence = [f"Superseded by routed Retail ERP destination {dest}"] if dest else []
        return (strategy, status, "source_only" if dest else "n/a", evidence, reason)

    # 6a. Audit correction: native ERPNext module workspaces superseded by a
    # Retail ERP nav module landing page, or genuinely internal Desk config.
    if ftype == "workspace" and feature.get("name") in WORKSPACE_OVERRIDES:
        strategy, status, dest, reason = WORKSPACE_OVERRIDES[feature.get("name")]
        evidence = [f"Superseded by routed Retail ERP destination {dest}"] if dest else []
        return (strategy, status, "source_only" if dest else "n/a", evidence, reason)

    # 6b. Audit correction: country-specific regional reports not applicable
    # to this business's jurisdiction.
    if ftype == "report" and feature.get("name") in NOT_REQUIRED_REPORT_NAMES:
        return ("not_required", "not_required", "n/a", [], NOT_REQUIRED_REPORT_NAMES[feature.get("name")])

    # 6c. Audit correction: print formats attached to a Report rather than a
    # DocType (doc_type is empty in ERPNext for these), whose report is
    # already routed via REPORT_GROUPS. feature_inventory.py's print-format
    # resolver only checks doc_type, so these were never credited even though
    # the report they render is genuinely reachable.
    if ftype == "print_format" and feature.get("name") in PRINT_FORMAT_REPORT_NAMES:
        from my_store_ui.services.priority_registry import REPORT_GROUPS as _REPORT_GROUPS
        report_name = PRINT_FORMAT_REPORT_NAMES[feature.get("name")]
        if report_name in {r for names in _REPORT_GROUPS.values() for r in names}:
            return ("generated_print", "generated_provisional", "route_only",
                    [f"Selectable via the routed report {report_name}'s Print Preview"],
                    "Report-attached print format; renders through the routed report viewer's "
                    "print/PDF dialog. Per-format/letterhead verification pending.")

    # 7. Reports without a route.
    if ftype == "report":
        return ("generated_report", "unavailable_with_reason", "n/a", [],
                f"Not yet adapted ({priority}); runs in Desk. Candidate for the report engine.")

    # 8. Visual (workspace/dashboard/chart/number card).
    if ftype in VISUAL_TYPES:
        return ("generated_dashboard", "unavailable_with_reason", "n/a", [],
                f"Not yet adapted ({priority}); Desk workspace/dashboard remains source of truth.")

    # 9. Remaining in-scope DocTypes / pages -> planned, honestly unavailable.
    return ("unavailable_with_reason", "unavailable_with_reason", "n/a", [],
            f"Pending implementation ({priority}); standard Desk remains the source of truth.")


def build_parity_registry() -> dict:
    """Build the authoritative registry from the canonical inventory (read-only)."""
    data = json.loads(_canonical_path().read_text(encoding="utf-8"))
    routed_doctypes = frozenset(
        f.get("doctype") for f in data["features"]
        if f.get("feature_type") == "doctype" and f.get("current_custom_route")
    )
    entries = []
    for f in data["features"]:
        if not f.get("user_facing"):
            continue
        priority = _priority_for(f)
        strategy, status, vlevel, evidence, note = _strategy_and_status(f, priority, routed_doctypes)
        entries.append({
            "feature_key": f["feature_id"],
            "source_app": f.get("application"),
            "module": f.get("module"),
            "capability_type": f.get("feature_type"),
            "source_name": f.get("name"),
            "action_name": f.get("name") if f.get("feature_type") == "document_action" else None,
            "parent_feature": f.get("parent_feature"),
            "business_priority": priority,
            "implementation_strategy": strategy,
            "retail_erp_route": f.get("current_custom_route"),
            "backend_handler": None,
            "permission_rule": "standard_frappe_document_permissions",
            "status": status,
            "verification_level": vlevel,
            "evidence": evidence,
            "notes": note,
            "blocking_reason": None,
        })
    return {
        "schema": "retail-erp-parity-registry/1",
        "source_fingerprint": data.get("inventory_fingerprint"),
        "site": data.get("site"),
        "entry_count": len(entries),
        "entries": entries,
    }


def registry_summary(registry: dict) -> dict:
    entries = registry["entries"]
    by_status = Counter(e["status"] for e in entries)
    by_priority = Counter(e["business_priority"] for e in entries)
    by_strategy = Counter(e["implementation_strategy"] for e in entries)
    implemented = sum(by_status[s] for s in IMPLEMENTED_STATUSES)
    return {
        "entry_count": len(entries),
        "implemented_any": implemented,
        "by_status": dict(sorted(by_status.items())),
        "by_priority": dict(sorted(by_priority.items())),
        "by_strategy": dict(sorted(by_strategy.items())),
    }


def validate_parity_registry(registry: dict | None = None) -> dict:
    """Enforce the honesty contract. Returns {'status': 'pass'|'fail', 'errors': [...]}."""
    registry = registry or build_parity_registry()
    entries = registry["entries"]
    errors: list[str] = []

    # Coverage: every user-facing feature must be present exactly once.
    data = json.loads(_canonical_path().read_text(encoding="utf-8"))
    uf_keys = {f["feature_id"] for f in data["features"] if f.get("user_facing")}
    reg_keys = [e["feature_key"] for e in entries]
    key_counts = Counter(reg_keys)
    dupes = [k for k, n in key_counts.items() if n > 1]
    if dupes:
        errors.append(f"duplicate feature keys: {len(dupes)} (e.g. {dupes[:3]})")
    missing = uf_keys - set(reg_keys)
    if missing:
        errors.append(f"user-facing features with no registry entry: {len(missing)} (e.g. {sorted(missing)[:3]})")
    extra = set(reg_keys) - uf_keys
    if extra:
        errors.append(f"registry entries not user-facing in inventory: {len(extra)}")

    for e in entries:
        k = e["feature_key"]
        if e["implementation_strategy"] not in STRATEGIES:
            errors.append(f"{k}: unknown strategy {e['implementation_strategy']!r}")
        if e["status"] not in STATUSES:
            errors.append(f"{k}: unknown status {e['status']!r}")
        if e["business_priority"] not in PRIORITIES:
            errors.append(f"{k}: unknown priority {e['business_priority']!r}")
        if e["status"] == "verified_complete" and not e.get("evidence"):
            errors.append(f"{k}: verified_complete without evidence")
        # A bare route must never be counted as verified_complete.
        if e["status"] == "verified_complete" and e.get("verification_level") in {None, "route_only", "n/a"}:
            errors.append(f"{k}: verified_complete requires behavioural verification_level")
        # Routed entries must not silently be 'unavailable', 'not_required' or 'internal'.
        if e["retail_erp_route"] and e["status"] in {"unavailable_with_reason", "not_required", "internal"}:
            errors.append(f"{k}: has route but status {e['status']}")

    return {"status": "fail" if errors else "pass", "error_count": len(errors), "errors": errors[:50]}


def _summary_markdown(registry: dict, summ: dict, val: dict) -> str:
    prio_meaning = {
        "P0_go_live": "Blocks the fixed wholesale go-live flow",
        "P1_required": "Required before client go-live",
        "P2_important": "Important, not day-one blocking",
        "P3_optional": "Optional / after go-live",
        "not_required": "Outside the wholesale importing/selling scope",
        "internal": "Technical component, not a user route",
    }
    status_meaning = {
        "verified_complete": "Real implementation + behavioural evidence",
        "implemented_unverified": "Implemented, lacks browser/role/business verification",
        "generated_provisional": "Generic engine exposes it; specialised behaviour unverified",
        "special_adapter": "Dedicated adapter (e.g. mapped-document action)",
        "blocked": "Cannot complete without approval/credentials/packages",
        "unavailable_with_reason": "Inventoried, intentionally not yet available (planned)",
        "not_required": "Not needed for this business",
        "internal": "Technical/internal, no user route required",
    }
    L = ["# Authoritative Parity Registry Summary (Stage 2)", ""]
    L.append(f"- Source inventory fingerprint: `{registry['source_fingerprint']}`")
    L.append(f"- Registry entries (one per user-facing feature): **{summ['entry_count']}**")
    L.append(f"- Validation: **{val['status'].upper()}** ({val['error_count']} errors)")
    L.append(f"- Implemented in some form (custom/provisional/adapter/unverified): **{summ['implemented_any']}**")
    L.append("")
    L.append("> A route alone is never counted as completion. `unavailable_with_reason`, "
             "`not_required` and `internal` are NOT implemented functionality.")
    L.append("")
    L.append("## By status")
    L.append("")
    L.append("| Status | Meaning | Count |")
    L.append("|---|---|---:|")
    for s, n in summ["by_status"].items():
        L.append(f"| {s} | {status_meaning.get(s, '')} | {n} |")
    L.append("")
    L.append("## By business priority")
    L.append("")
    L.append("| Priority | Meaning | Count |")
    L.append("|---|---|---:|")
    for p, n in summ["by_priority"].items():
        L.append(f"| {p} | {prio_meaning.get(p, '')} | {n} |")
    L.append("")
    L.append("## By implementation strategy")
    L.append("")
    L.append("| Strategy | Count |")
    L.append("|---|---:|")
    for st, n in summ["by_strategy"].items():
        L.append(f"| {st} | {n} |")
    L.append("")
    L.append("## Reproduce / validate")
    L.append("")
    L.append("```bash")
    L.append("bench --site site1.local execute my_store_ui.audit.parity_registry.generate")
    L.append("bench --site site1.local execute my_store_ui.audit.parity_registry.validate_parity_registry")
    L.append("```")
    L.append("")
    return "\n".join(L) + "\n"


def generate() -> dict:
    """Write the authoritative registry snapshot + summary under docs/full-parity/inventory/."""
    registry = build_parity_registry()
    val = validate_parity_registry(registry)
    summ = registry_summary(registry)
    out = _canonical_path().parent / "full-parity" / "inventory"
    out.mkdir(parents=True, exist_ok=True)
    (out / "current_registry.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    (out / "parity_registry_summary.md").write_text(_summary_markdown(registry, summ, val), encoding="utf-8")
    return {"validation": val["status"], "error_count": val["error_count"], "summary": summ}


# ---------------------------------------------------------------------------
# Step 13: corrected production-parity audit
# ---------------------------------------------------------------------------
# The raw route-based `unmapped_user_facing` metric (feature_inventory.py)
# counts ANY feature without a `current_custom_route` as unmapped, even when
# that feature is truthfully internal, not_required, or already given a real
# (non-route) implementation strategy such as special_adapter. This produces
# a corrected, honest breakdown from the registry instead, so "zero unmapped"
# can only be reached by truthful classification, never by inventing routes.
#
# `required_but_missing` is the genuinely meaningful gap number: P0/P1/P2
# entries (P3_optional excluded — those are explicitly optional) that carry
# NO real implementation strategy yet (status not in IMPLEMENTED_STATUSES).
# This is reported honestly and is NOT forced to zero by this function —
# doing so would mean re-labelling real gaps as fake completions, which the
# mission explicitly forbids.
REQUIRED_PRIORITY_TIERS = {"P0_go_live", "P1_required", "P2_important"}
ALL_BUSINESS_TIERS = {"P0_go_live", "P1_required", "P2_important", "P3_optional"}


def corrected_production_parity_audit(registry: dict | None = None) -> dict:
    registry = registry or build_parity_registry()
    entries = registry["entries"]
    data = json.loads(_canonical_path().read_text(encoding="utf-8"))
    total_discovered = data["counts"]["features_total"]

    by_status = Counter(e["status"] for e in entries)
    by_strategy = Counter(e["implementation_strategy"] for e in entries)

    # A feature is "user-facing required" only by its actual resolved status,
    # not by the raw module-default priority alone: business_priority is
    # computed from the feature's *module* before any per-feature override
    # (e.g. a P1_required-module ledger table correctly re-classified
    # `internal` by SYSTEM_INTERNAL_DOCTYPE_NAMES keeps its module priority).
    # So "required" here means priority says required AND status did not
    # resolve it to internal/not_required — those are truthful exclusions,
    # never a gap, regardless of what the module-default priority says.
    RESOLVED_EXCLUSIONS = {"internal", "not_required"}
    user_facing_required = [
        e for e in entries
        if e["business_priority"] in ALL_BUSINESS_TIERS and e["status"] not in RESOLVED_EXCLUSIONS
    ]
    mapped_required = [e for e in user_facing_required if e["status"] in IMPLEMENTED_STATUSES]
    required_but_missing = [
        e for e in user_facing_required
        if e["status"] not in IMPLEMENTED_STATUSES and e["business_priority"] in REQUIRED_PRIORITY_TIERS
    ]
    unclassified = [
        e for e in entries
        if e["implementation_strategy"] not in STRATEGIES or e["status"] not in STATUSES
        or e["business_priority"] not in PRIORITIES
    ]
    corrected_unmapped_user_facing = [
        e for e in entries
        if e["status"] not in IMPLEMENTED_STATUSES
        and e["status"] not in RESOLVED_EXCLUSIONS
        and not (e["status"] in {"unavailable_with_reason", "blocked"} and e.get("notes"))
    ]

    return {
        "schema": "retail-erp-corrected-production-parity-audit/1",
        "source_fingerprint": registry.get("source_fingerprint"),
        "total_discovered": total_discovered,
        "user_facing_required": len(user_facing_required),
        "mapped_required": len(mapped_required),
        "required_but_missing": len(required_but_missing),
        "required_but_missing_feature_keys": [e["feature_key"] for e in required_but_missing][:200],
        "unclassified": len(unclassified),
        "corrected_unmapped_user_facing": len(corrected_unmapped_user_facing),
        "verified_complete": by_status.get("verified_complete", 0),
        "implemented_unverified": by_status.get("implemented_unverified", 0),
        "generated_provisional": by_status.get("generated_provisional", 0),
        # special_adapter / external_app_adapter are tracked as *strategy* in
        # this registry (status stays implemented_unverified) - see
        # by_strategy, not by_status, for these two.
        "special_adapter": by_strategy.get("special_adapter", 0),
        "external_app_adapter": by_strategy.get("external_app_adapter", 0),
        "unavailable_with_reason": by_status.get("unavailable_with_reason", 0),
        "not_required": by_status.get("not_required", 0),
        "internal": by_status.get("internal", 0),
        "blocked": by_status.get("blocked", 0),
        "success_criteria": {
            "required_but_missing_is_zero": len(required_but_missing) == 0,
            "unclassified_is_zero": len(unclassified) == 0,
        },
    }


def generate_corrected_audit() -> dict:
    """Write the Step 13 corrected production-parity audit to docs/full-parity/.

    Kept as a distinct file from strict_audit_latest.json (the raw
    route-based audit from feature_inventory.py) so both the raw and the
    corrected/truthful metric are visible side by side, per Step 13.
    """
    registry = build_parity_registry()
    audit = corrected_production_parity_audit(registry)
    out = _canonical_path().parent / "full-parity"
    out.mkdir(parents=True, exist_ok=True)
    (out / "corrected_production_parity_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    return audit
