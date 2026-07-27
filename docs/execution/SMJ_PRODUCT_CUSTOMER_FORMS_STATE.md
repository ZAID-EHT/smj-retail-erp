# SMJ Product/Customer Forms — Mission State

- Branch: `full-feature-parity`; start commit `32f5c74` (v1.0.0-rc4)
- Recovery tag: `pre-smj-product-customer-forms-20260727-2014`
- Backup: `sites/staging.local/private/backups/20260727_201426-staging_local-*`
- Test site: staging.local; protected: site1.local (fingerprint recorded)

## Audit (Phase 1) key findings
- item_naming_by = "Item Code" (manual) → generate item_code server-side via make_autoname.
- Existing Item custom fields: material/size/colour, sku_prefix, published, purchase/retail/wholesale price + margins, purchase_uom/sales_uom/safety_stock; Item Price sync exists (purchase→Standard Buying, wholesale→Wholesale, retail→Retail).
- Need new Item fields: custom_sku, custom_image_2, custom_carton_qty, custom_margin, custom_department_price, custom_stock_location_1/2/3.
- Customer: custom_credit_type (Select Credit/Non-Credit) exists; credit limit in standard credit_limits child; credit code in wholesale/credit.py.
- Need new Customer fields: custom_whatsapp_no, custom_accounts_department_no, custom_transport_method, custom_transport_detail, custom_br_no, custom_business_nature, custom_credit_days.
- Price Lists: Retail, Wholesale exist (selling). Department Price List to be created (selling).

## Phase status
0 preflight done; 1 audit done; 2-13 pending.
