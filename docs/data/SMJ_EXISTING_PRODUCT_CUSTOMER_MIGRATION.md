# SMJ Existing Product/Customer Migration

Tool: `my_store_ui/quick_entry/existing_data.py` (inspect / dry_run / apply / verify).
Guarded: refuses `site1.local` and any non-allowlisted site; never invents credit
values or BR numbers; never batch-enables a stocked Item; never touches historical
pricing.

## Dry-run on staging.local (2026-07-27)

| | Count |
|---|---|
| Products total | 41 |
| Customers total | 28 |

### Safe defaults (apply is deterministic + reversible)
| Default | Count | Rule |
|---------|------:|------|
| Generate missing SKU | 40 | make_autoname("5.###") where custom_sku empty |
| Default Price Category = Retail Price List | 2 | where default_price_list empty |
| Missing Payment Type = Non-Credit | 0 | only where **no outstanding** exists |

### Manual review (NOT auto-applied)
| Item | Count | Why manual |
|------|------:|-----------|
| Products not batch-managed | 40 | Enabling batch tracking on an Item **with stock history** would disturb stock records — a standard, deliberate migration only |
| Products with duplicate Item Prices | 0 | — |
| Customers missing Contact | 2 | needs real contact data |
| Customers missing Address | 2 | needs real address data |

## Decision
The safe defaults are **not auto-applied in this mission** — they change 40 existing
demo records, which is the owner's call. The tool is proven via dry-run and ready:

```
bench --site staging.local execute my_store_ui.quick_entry.existing_data.apply
bench --site staging.local execute my_store_ui.quick_entry.existing_data.verify
```

**Batch tracking on existing stocked products is an explicit manual migration** (new
products created through the quick form are batch-managed from the start).
