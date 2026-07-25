# SMJ Purchase Order — Data Audit (Phase 5)

**Audited:** 2026-07-25 on `staging.local` (ERPNext v15, `my_store_ui` universal engine).
**Method:** read-only, metadata-driven. Nothing is asserted from memory — the audit
reads the *installed* DocType metadata and the engine's own
`_readable_fields` / `_writable_fields` and reports what it finds.

Reproduce:

```bash
bench --site staging.local execute my_store_ui.dev_scripts.purchase_workflow_verification.audit
```

Regression form (read-only, runs in the normal suite):
`my_store_ui/tests/test_purchase_workflow.py` — **7 tests green**.

## Result

**PASS — no gaps.** All 66 required fields exist in the installed metadata and are
exposed for read; every field a buyer must type is writable; every
controller-calculated field is correctly read-only; all 14 required mappings are
registered.

| Group | Required | Present | Readable | Missing |
|-------|---------:|--------:|---------:|---------|
| Header & supplier information (`Purchase Order`) | 24 | 24 | 24 | none |
| Item table (`Purchase Order Item`) | 26 | 26 | 26 | none |
| Totals (`Purchase Order`) | 16 | 16 | 16 | none |
| Mappings | 14 | 14 | — | none |

Legend below: `R` readable, `W` writable, `*` mandatory in ERPNext.

## Header and supplier information

| Flags | Fieldname | Type | Label |
|-------|-----------|------|-------|
| `RW*` | `supplier` | Link | Supplier |
| `R-` | `supplier_name` | Data | Supplier Name (fetched) |
| `RW*` | `company` | Link | Company |
| `RW*` | `currency` | Link | Currency |
| `RW*` | `conversion_rate` | Float | Exchange Rate |
| `RW` | `buying_price_list` | Link | Price List |
| `R-` | `price_list_currency` | Link | Price List Currency (fetched) |
| `RW` | `plc_conversion_rate` | Float | Price List Exchange Rate |
| `RW*` | `transaction_date` | Date | Date |
| `RW` | `schedule_date` | Date | Required By |
| `RW` | `supplier_address` | Link | Supplier Address |
| `RW` | `contact_person` | Link | Supplier Contact |
| `RW` | `shipping_address` | Link | Shipping Address |
| `RW` | `billing_address` | Link | Company Billing Address |
| `RW` | `project` | Link | Project |
| `RW` | `cost_center` | Link | Cost Center |
| `RW` | `payment_terms_template` | Link | Payment Terms Template |
| `RW` | `payment_schedule` | Table | Payment Schedule |
| `RW` | `taxes_and_charges` | Link | Purchase Taxes and Charges Template |
| `RW` | `taxes` | Table | Purchase Taxes and Charges |
| `RW` | `tc_name` | Link | Terms |
| `RW` | `terms` | Text Editor | Terms and Conditions |
| `RW` | `apply_tds` | Check | Apply Tax Withholding Amount |
| `R-*` | `status` | Select | Status (controller-owned) |

**Supplier Group** is not a Purchase Order header field in v15 — it lives on
`Supplier.supplier_group` (audited separately: present, `RW`) and is fetched for
display/reporting. **Supplier Quotation** and **Material Request** links are
per-row, not per-header; they are audited in the item table below.

## Item table (`Purchase Order Item`)

Child DocTypes carry no `DocPerm` rows of their own. The engine resolves a child
table's permlevel access from its **parent** (`_field_definition`, `api.py`), and
this audit uses the same model. Auditing a child against its own (empty) permlevels
reports a false "not exposed" for every field.

Writable — buyer entry fields:
`item_code*`, `item_name*`, `description`, `qty*`, `uom*`, `conversion_factor*`,
`rate`, `price_list_rate`, `discount_percentage`, `discount_amount`, `warehouse`,
`schedule_date*`, `expense_account`, `cost_center`, `project`, `item_tax_template`

Read-only — controller-calculated or source links:
`stock_uom*`, `amount`, `base_amount*`, `received_qty`, `billed_amt`, `stock_qty`,
`material_request`, `material_request_item`, `supplier_quotation`,
`supplier_quotation_item`

This split is correct: quantities/rates/discounts are typed, while amounts,
received/billed progress, stock-UOM conversion and provenance links are owned by
ERPNext's controllers and must not be settable from the browser.

## Totals

Readable and **controller-owned (not writable)**: `total_qty`, `net_total`,
`base_net_total`, `total_taxes_and_charges`, `base_total_taxes_and_charges`,
`grand_total`, `base_grand_total`, `rounding_adjustment`, `rounded_total`,
`base_rounded_total`, `advance_paid`, `per_received`, `per_billed`.

Readable **and writable** (legitimate inputs): `apply_discount_on`,
`additional_discount_percentage`, `discount_amount`.

`test_purchase_order_totals_are_exposed_and_controller_owned` asserts the
controller-owned set stays non-writable, so a future metadata or engine change
cannot silently let the browser set a grand total.

## Lifecycle

| Capability | State |
|------------|-------|
| Create / Save Draft | Yes (`/purchases/orders/new`) |
| Submit | Yes — `is_submittable: True` |
| Cancel | Yes |
| Amend | Yes — verified live (`PUR-ORD-2026-00069` → `PUR-ORD-2026-00069-1`) |
| Duplicate | Yes — `allow_copy` not disabled |
| Print / PDF | Yes — standard renderer plus `Drop Shipping Format` |
| Active Workflow | None (so submit/cancel are the document's own) |

## Mappings

All 14 required mappings are registered in `MAPPED_ACTIONS` (`universal/api.py`) and
every one delegates to the standard ERPNext controller `make_*` function — no
hand-rolled document construction, no direct ledger writes.

| Source | Action | Target |
|--------|--------|--------|
| Material Request | `make_request_for_quotation` | Request for Quotation |
| Material Request | `make_supplier_quotation` | Supplier Quotation |
| Material Request | `make_purchase_order` | Purchase Order |
| Request for Quotation | `make_supplier_quotation` | Supplier Quotation |
| Supplier Quotation | `make_purchase_order` | Purchase Order |
| Supplier Quotation | `make_purchase_invoice` | Purchase Invoice |
| Purchase Order | `make_purchase_receipt` | Purchase Receipt |
| Purchase Order | `make_purchase_invoice` | Purchase Invoice |
| Purchase Order | `payment` | Payment Entry |
| Purchase Receipt | `make_purchase_invoice` | Purchase Invoice |
| Purchase Receipt | `make_purchase_return` | Purchase Receipt |
| Purchase Receipt | `make_lcv` | Landed Cost Voucher |
| Purchase Invoice | `make_payment_entry` | Payment Entry |
| Purchase Invoice | `make_debit_note` | Purchase Invoice |

Additional purchasing mappings already registered beyond the requirement:
`Material Request → Stock Entry / Pick List / In-Transit Stock Entry / PO-for-supplier`,
`Purchase Order → Inter Company Sales Order / Subcontracting Order / Material to
Supplier / Return of Components`, `Purchase Receipt → Inter Company Delivery Note /
Rejected-warehouse Return / Stock Entry`, `Purchase Invoice → Inter Company Sales
Invoice / Purchase Receipt / Stock Entry / LCV`.

Every mapped action re-checks `frappe.has_permission(target, "create")` before
running (`_run_mapped_action`), and the browser only ever sends a symbolic action
key — dotted Python paths are never accepted from a request.

## Safety

- Audit is read-only; no document, ledger or metadata was modified.
- Exposure is reported through the engine's own helpers, so the doc reflects what
  a real request would see rather than raw metadata.
