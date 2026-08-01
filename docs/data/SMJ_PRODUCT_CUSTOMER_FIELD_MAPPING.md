# SMJ Product/Customer Field Mapping

## Product (17 visible fields — two selling prices)
| # | Label | DocType.field | Std/Custom | Type | Required | Notes |
|---|-------|---------------|-----------|------|----------|-------|
| 1 | Product ID | Item.item_code | std | Data | auto | make_autoname P1.##### (P100001); read-only; immutable |
| 2 | Upload Image 1 | Item.image | std | Attach Image | no | drag-and-drop upload |
| 3 | Upload Image 2 | Item.custom_image_2 | custom | Attach Image | no | drag-and-drop upload |
| 4 | SKU | Item.custom_sku | custom | Data | auto | make_autoname 5.### (5001); unique; read-only |
| 5 | Product Name | Item.item_name | std | Data | yes | trimmed |
| 6 | Size | Item.custom_product_size | custom | Data | no | |
| 7 | Category | Item.item_group | std | Link | yes | non-group only |
| 8 | Material | Item.custom_product_material | custom | Data | no | |
| 9 | Carton Qty | Item.custom_carton_qty | custom | Float | no | ≥0; units per carton |
| 10-12 | Stock Location 1-3 | Item.custom_stock_location_1/2/3 | custom | Link Warehouse | 1 req | company-scoped; unique; loc1→item_defaults |
| 13 | Re-Stock Qty | Item Reorder.warehouse_reorder_qty | std child | Float | no | on location 1 |
| 14 | Cost Price | Item Price (Standard Buying) | std | Currency | no | permission-gated; hidden from Sales |
| 15 | Margin | Item.custom_margin | custom | Percent | no | reference input |
| 16 | Wholesale Price | Item Price (Wholesale Price List) | std | Currency | no | selling only |
| 17 | Retail Price | Item Price (Retail Price List) | std | Currency | no | selling only |

**Two selling prices only: Wholesale and Retail.** (Department Price was removed.)
Stock quantity is NEVER a Product field — actual stock stays in Bin/Stock Ledger. New
stock products are batch-managed (series BAT-.YYYY.-.######). Photos use drag-and-drop
upload via Frappe's standard file mechanism.

## Customer (14 visible fields)
| # | Label | DocType.field | Std/Custom | Type | Required | Notes |
|---|-------|---------------|-----------|------|----------|-------|
| 1 | Customer | Customer.customer_name | std | Data | yes | duplicate warning |
| 2 | Address | Address.address_line1 (linked) | std | Data | no | Dynamic Link; no dup on edit |
| 3 | Contact No | Customer.mobile_no + Contact | std | Data | no | |
| 4 | WhatsApp No | Customer.custom_whatsapp_no | custom | Data | no | "same as contact" option |
| 5 | Account Dept No | Customer.custom_accounts_department_no | custom | Data | no | phone |
| 6 | Transport Detail | Customer.custom_transport_detail | custom | Small Text | no | |
| 7 | Transport Method | Customer.custom_transport_method | custom | Select | no | |
| 8 | BR No | Customer.custom_br_no | custom | Data | no | searchable |
| 9 | Business Nature | Customer.custom_business_nature | custom | Select | no | shown ONCE |
| 10 | Price Category | Customer.default_price_list | std | Link | no | default Retail; selling only; drives sale price |
| 11 | Payment Type | Customer.custom_credit_type | custom | Select | no | Credit/Non-Credit (existing field) |
| 12 | Credit Limit | credit_limits child.credit_limit | std child | Currency | if Credit | per company |
| 13 | Credit Days | Customer.custom_credit_days | custom | Int | if Credit | ≥0 |
| 14 | Created Date | Customer.creation | std | Datetime | auto | read-only |
