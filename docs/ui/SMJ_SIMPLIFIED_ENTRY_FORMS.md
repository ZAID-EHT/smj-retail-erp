# SMJ Simplified Entry Forms (Phase 7)

## What already exists (verified)
The custom form engine (`services/form_schemas.py`) already renders **curated,
sectioned** create/edit forms with progressive disclosure — required ERPNext fields
are kept, less-used fields sit in later sections:

| Form | Sections |
|------|----------|
| Customer | Basic Information · Contact Information · Sales Information |
| Item / Product | Basic Information · Product Details · Pricing |
| Delivery Note | Delivery Information · Shipping Information · Terms and Notes |
| Sales Invoice | Invoice Information · Accounting Information · Terms and Notes |

Verified by `test_universal_frontend.test_custom_entry_forms_are_curated_into_progressive_sections`
(Customer + Item sections and required fields).

## Added this mission
**Supplier** flows through the universal generated engine, so it now has a curated
add form via `SIMPLE_CREATE_FIELDS["Supplier"]` (name, group, type, currency, price
list, payment terms, tax id, tax category, image) with `supplier_name` +
`supplier_group` required — the full field set remains for editing. Verified by
`test_universal_frontend.test_supplier_has_a_curated_universal_add_form`.

User curated add form (username/password/roles required) shipped earlier (`0d10f34`).

## Confirmed defect — Item pricing is stored only in custom fields (NOT fixed here)
`form_api._apply_item_pricing` computes retail/wholesale prices from
`custom_purchase_price` + margin percentages and writes them to
`custom_retail_price` / `custom_wholesale_price` **only**. It does **not** create or
update standard `Item Price` records.

**Why this matters:** the prompt requires "pricing must create or update standard
Item Price records; do not store purchase and sales prices only in custom display
fields." More concretely, prices held only in custom fields are invisible to
ERPNext's pricing engine (`get_item_details` / `Item Price` lookups) — which is
exactly what Smart Sales customer pricing (Phase 2) reads. So an item priced through
this form would not surface its wholesale/retail price in Smart Sales.

**Why not auto-fixed:** the correct fix upserts `Item Price` rows on the wholesale
and retail price lists, but the **price-list mapping is a business decision** —
`staging.local` has `Retail Price List` and `Preferred Customer Price List` but no
explicit `Wholesale Price List`. Guessing the mapping is forbidden by the brief.

**Recommended fix (for sign-off):** after computing retail/wholesale, upsert
`Item Price(item_code, price_list=<configured retail list>, selling=1,
price_list_rate=retail)` and likewise for wholesale, with the two target price lists
read from site config (defaults: retail → `Retail Price List`, wholesale → the
default selling price list), skipping gracefully when a target list does not exist.
Recorded in `SMJ_CORE_WORKFLOW_BLOCKERS.md`.

## Remaining (truthful)
- Item-price → Item Price sync (above), pending the price-list mapping decision.
- Supplier/Product/transaction forms could gain a few more curated fields, but the
  sectioned structure and required-field integrity are already in place.
