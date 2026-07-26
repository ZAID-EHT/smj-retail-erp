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

## RESOLVED 2026-07-25 — Item pricing now creates standard `Item Price` records

The previously recorded defect is **fixed**. `_apply_item_pricing` still computes
`custom_total_cost` / `custom_retail_price` / `custom_wholesale_price` for the form,
and `save_entity_form` now calls `_sync_item_prices(doc)` after save to mirror those
values into standard `Item Price` documents.

**Severity of the original defect, measured:** `Item Price` count on
`staging.local` was **0**. Every product created through this form had *no* price
that ERPNext's pricing engine could see, so Smart Sales, quotations and any call to
`get_item_details` found nothing.

### The price-list mapping decision (settled from data, not guessed)

The old note said staging had no `Wholesale Price List`. That is **wrong** — it
exists. The real data:

| Price List | buying | selling | Item Prices | Customers using |
|------------|:------:|:-------:|------------:|----------------:|
| Standard Buying | 1 | 0 | 0 | — |
| Standard Selling | 0 | 1 | 0 | 0 |
| Retail Price List | 0 | 1 | 0 | **23** |
| Preferred Customer Price List | 0 | 1 | 0 | 3 |
| Wholesale Price List | **1** | **0** | 0 | 0 |

Mapping chosen:

| Item field | Price List | Required flag |
|-----------|-----------|---------------|
| `custom_purchase_price` | Buying Settings `buying_price_list` → `Standard Buying` | `buying` |
| `custom_wholesale_price` | `Wholesale Price List` | `selling` |
| `custom_retail_price` | `Retail Price List` (23 of 26 customers default to it) | `selling` |

**Two configuration corrections were required**, applied in separate sessions and
both re-verified on 2026-07-26 by
`dev_scripts/verify_price_list_state.py` (read-only).

1. *(2026-07-25)* `Wholesale Price List` was `buying=1, selling=0`. ERPNext's
   pricing engine filters `Item Price` by buying/selling, so a wholesale *selling*
   price written to a buying-only list is silently never applied — the same class of
   bug being fixed. `selling` was set to `1`.
2. *(2026-07-26)* `buying` was **still `1`**, which the earlier session left in place
   deliberately ("ERPNext supports dual-purpose lists"). That was wrong for this
   requirement: ERPNext stamps the list's `buying`/`selling` flags onto every
   `Item Price` row it creates, so the marked-up wholesale rate was selectable as a
   **purchase cost** — breaking "retail, wholesale and purchase prices remain
   separate". Verified by probe: a wholesale row was created with `buying=1,
   selling=1`. `buying` is now `0`.

Risk was nil for both changes and re-verified immediately before the second one:
**0** Item Prices, **0** customers, **0** suppliers, **0** customer groups, and **0**
Purchase Orders / Purchase Invoices / Purchase Receipts / Supplier Quotations
referencing the list. The change is applied by
`dev_scripts/fix_wholesale_price_list_selling_only.py`, which re-checks every one of
those references and **refuses to act** if any is non-zero, so it is safe to re-run.
`test_wholesale_price_list_is_selling_only` and
`test_retail_and_wholesale_rows_are_selling_only_and_purchase_is_buying_only` now
guard both the list and the rows it produces.

### Behaviour

- Creates one `Item Price` per configured list, at the item's stock UOM.
- **Updates** the existing row instead of duplicating on re-save.
- **Deletes** the row when a price is cleared, so a stale price stops applying.
- **Never overwrites** a batch-, party- or other-UOM-specific `Item Price` — those
  were entered deliberately. Legacy rows with a `NULL`/empty UOM *are* adopted.
- **Converges duplicates**: if more than one owned row exists for a list (reachable
  via differing `valid_from` dates, or through imported data), the extras are removed
  so a stale rate cannot keep applying alongside the maintained one.
- **Refuses to write an unusable price**: if a target list is missing, disabled, or
  lacks the required buying/selling flag, that one price is skipped and a warning is
  logged rather than creating a price the engine can never apply.
- Uses standard `Item Price` documents, so Pricing Rules, currency and validity dates
  all behave normally. Nothing is written directly to any pricing table.

### Permissions — the sync cannot silently escalate

`Item Price` is **master data in stock ERPNext v15**: `item_price.json` grants it to
`Sales Master Manager` and `Purchase Master Manager` only. Confirmed against
`apps/erpnext` source and the live site (no `Custom DocPerm` overrides). `Item
Manager` — the only non-Administrator role that can create an `Item` — therefore has
**no** `Item Price` permission.

Left unhandled, the sync would have made product creation fail outright for an Item
Manager with a bare `PermissionError` raised from inside the `Item Price` insert.
This was found by probe, not by the test suite, because the suite runs as
Administrator, which bypasses permission checks.

The sync now **plans every change before writing any of it** and gates on the exact
permissions the plan needs (`create` / `write` / `delete`), throwing one actionable
message that names the required roles. Consequences:

- No `ignore_permissions` anywhere — the standard permission model is enforced.
- A user who cannot maintain prices can still create an **unpriced** product; the
  gate only fires when a price actually has to be written.
- Failure is **atomic**: the throw happens before the first price write, and because
  `form_api` never commits mid-request, the whole request rolls back and no
  half-created product is left behind.

### Verification — `test_item_price_sync` (14 tests, all green on `staging.local`)

| Test | Asserts |
|------|---------|
| `test_every_configured_price_list_is_usable` | all three target lists exist, are enabled and carry the required flag — a misconfiguration fails loudly instead of silently skipping |
| `test_creating_a_product_writes_standard_item_prices` | 3 rows written; retail 1,800 / wholesale 1,500 / purchase 1,000 from cost 1,200 at 50% / 25% margins; custom fields still populated |
| `test_synced_price_is_visible_to_the_pricing_engine` | **`get_item_details` returns `price_list_rate` 1,800** — the actual point of the fix |
| `test_wholesale_price_list_is_selling_only` | the list is enabled, selling, and **not** buying |
| `test_retail_and_wholesale_rows_are_selling_only_and_purchase_is_buying_only` | the three prices stay separate at row level: selling rows are not usable as a cost, and the purchase row is not sellable |
| `test_editing_a_product_updates_instead_of_duplicating_item_prices` | re-save updates the same 3 rows |
| `test_clearing_a_price_removes_the_item_price` | cleared prices stop applying |
| `test_pricing_validation_still_rejects_impossible_margins` | wholesale > retail is still rejected and no Item is created |
| `test_a_customer_specific_price_is_never_overwritten` | a negotiated party price keeps its rate while the owned row updates |
| `test_a_legacy_row_without_a_uom_is_adopted_not_duplicated` | a `NULL`-UOM row is reused in place, not duplicated |
| `test_duplicate_owned_rows_converge_to_a_single_price` | a second owned row (differing `valid_from`) is removed so no stale rate survives |
| `test_pricing_a_product_without_item_price_rights_is_refused_atomically` | an Item Manager gets an actionable `PermissionError` naming the roles, **and no Item is left behind** |
| `test_an_unpriced_product_is_still_allowed_without_item_price_rights` | the gate does not fire when nothing needs writing |
| `test_a_master_manager_can_create_a_priced_product` | the same flow succeeds with the standard ERPNext roles |

Implementation traps found and fixed while building this:
- `uom IN ('', NULL)` never matches `NULL` in SQL, so the existing-row lookup missed
  and tried to insert duplicates. The match is done in Python.
- ERPNext defaults `Item Price.uom` to the item's stock UOM, so "no UOM set" was the
  wrong identity for our row.
- `Item Price` is master-data-restricted in ERPNext, so the sync had to gate on
  permissions before writing (see above) — otherwise it silently broke product
  creation for every role except the master managers and Administrator.

## Remaining (truthful)

- **Product form field gaps** vs the requirement list: `Colour`, `Purchase UOM`,
  `Selling UOM`, `Default Warehouse`, `Reorder Level`, `Safety Stock` and
  `Published` are not on the curated form. `Material` and `Size` **are** present as
  `custom_product_material` / `custom_product_size`. Adding Colour needs a new Custom
  Field; warehouse/reorder/safety-stock live in the `item_defaults` and
  `reorder_levels` child tables, so they need child-table support on this form rather
  than a plain field. This is ordinary remaining work, not a blocker.
- Supplier/Customer/transaction forms are curated and sectioned with required-field
  integrity intact; further field curation is cosmetic.
