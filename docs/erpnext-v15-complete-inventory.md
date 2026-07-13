# ERPNext v15 complete installed feature inventory

> Machine-generated from `site1.local` database metadata and installed source. Do not edit generated tables manually.

Inventory fingerprint: `22c6ac5fef82279480834dba4c85bda0c6da5cc25186dca7956c5e30d4205a1b`

## Coverage summary

| Metric | Count |
|---|---:|
| Installed Applications | 7 |
| Modules | 40 |
| Parent Doctypes | 467 |
| Child Doctypes | 335 |
| Custom Doctypes | 1 |
| Reports | 198 |
| Pages | 22 |
| Workspaces | 25 |
| Dashboards | 176 |
| Active Workflows | 0 |
| Print Formats | 44 |
| Client Scripts | 1 |
| Server Scripts | 0 |
| Custom Fields | 212 |
| Property Setters | 101 |
| Document Mappings And Actions | 634 |
| User Facing Features | 2482 |
| System Internal Exclusions | 359 |
| Previous Matrix Rows User Supplied | 98 |
| Previous Matrix Rows Observed | 102 |
| Missing Features Added | 2076 |
| Duplicate Rows Detected | 0 |
| Specialized Interfaces | 1481 |
| Generic Engine Features | 249 |
| Installed App Features | 244 |
| Remaining Desk Dependencies | 2482 |
| Unclassified Features | 0 |
| Features Total | 2841 |
| New Matrix Rows | 2943 |

## Feature records

| Feature ID | App | Module | Type | Name | Class | User-facing | Custom route | Completion | Desk dependency |
|---|---|---|---|---|---|---|---|---|---|
| `custom:client-script:user:theme` | custom | Core | client_script | theme | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:address:address-is-your-company-address` | custom | Contacts | custom_field | Address-is_your_company_address | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:address:address-tax-category` | custom | Contacts | custom_field | Address-tax_category | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:contact:contact-is-billing-contact` | custom | Contacts | custom_field | Contact-is_billing_contact | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:custom-docperm:custom-docperm-impersonate` | custom | Core | custom_field | Custom DocPerm-impersonate | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:docperm:docperm-impersonate` | custom | Core | custom_field | DocPerm-impersonate | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:docshare:docshare-impersonate` | custom | Core | custom_field | DocShare-impersonate | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-allow-company-dashboard-scope` | custom | Accounts | custom_field | POS Profile-posa_allow_company_dashboard_scope | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-allow-source-account-override` | custom | Accounts | custom_field | POS Profile-posa_allow_source_account_override | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-allowed-expense-accounts` | custom | Accounts | custom_field | POS Profile-posa_allowed_expense_accounts | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-allowed-source-accounts` | custom | Accounts | custom_field | POS Profile-posa_allowed_source_accounts | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-auto-open-customer-display` | custom | Accounts | custom_field | POS Profile-posa_auto_open_customer_display | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-default-source-account` | custom | Accounts | custom_field | POS Profile-posa_default_source_account | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-enable-awesome-dashboard` | custom | Accounts | custom_field | POS Profile-posa_enable_awesome_dashboard | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-enable-customer-display` | custom | Accounts | custom_field | POS Profile-posa_enable_customer_display | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-low-stock-alert-threshold` | custom | Accounts | custom_field | POS Profile-posa_low_stock_alert_threshold | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-section-awesome-dashboard` | custom | Accounts | custom_field | POS Profile-posa_section_awesome_dashboard | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-profile:pos-profile-posa-section-customer-display` | custom | Accounts | custom_field | POS Profile-posa_section_customer_display | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-settings:pos-settings-posa-dashboard-default-scope` | custom | Accounts | custom_field | POS Settings-posa_dashboard_default_scope | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-settings:pos-settings-posa-dashboard-low-stock-alert-threshold` | custom | Accounts | custom_field | POS Settings-posa_dashboard_low_stock_alert_threshold | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-settings:pos-settings-posa-enable-awesome-dashboard-global` | custom | Accounts | custom_field | POS Settings-posa_enable_awesome_dashboard_global | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:pos-settings:pos-settings-posa-section-dashboard` | custom | Accounts | custom_field | POS Settings-posa_section_dashboard | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:custom-field:utm-campaign:utm-campaign-crm-campaign` | custom | Custom | custom_field | UTM Campaign-crm_campaign | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:notification:error-log:error-log` | custom | Email | notification | Error Log | E | No | — | Not implemented | None while disabled |
| `custom:notification:integration-request:integration-request` | custom | Email | notification | Integration Request | E | No | — | Not implemented | None while disabled |
| `custom:print-format:journal-entry:cheque-printing-format` | custom | Printing | print_format | Cheque Printing Format | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `custom:print-format:purchase-order:drop-shipping-format` | custom | Printing | print_format | Drop Shipping Format | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `custom:property-setter:customer:customer-naming-series-hidden` | custom | Selling | property_setter | Customer-naming_series-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:customer:customer-naming-series-reqd` | custom | Selling | property_setter | Customer-naming_series-reqd | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note-item:delivery-note-item-barcode-hidden` | custom | Stock | property_setter | Delivery Note Item-barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-base-rounded-total-hidden` | custom | Stock | property_setter | Delivery Note-base_rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-base-rounded-total-print-hide` | custom | Stock | property_setter | Delivery Note-base_rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-disable-rounded-total-default` | custom | Stock | property_setter | Delivery Note-disable_rounded_total-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-in-words-hidden` | custom | Stock | property_setter | Delivery Note-in_words-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-in-words-print-hide` | custom | Stock | property_setter | Delivery Note-in_words-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-rounded-total-hidden` | custom | Stock | property_setter | Delivery Note-rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-rounded-total-print-hide` | custom | Stock | property_setter | Delivery Note-rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-scan-barcode-hidden` | custom | Stock | property_setter | Delivery Note-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-tax-id-hidden` | custom | Stock | property_setter | Delivery Note-tax_id-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:delivery-note:delivery-note-tax-id-print-hide` | custom | Stock | property_setter | Delivery Note-tax_id-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:item-barcode:item-barcode-barcode-hidden` | custom | Stock | property_setter | Item Barcode-barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:item:item-barcodes-hidden` | custom | Stock | property_setter | Item-barcodes-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:item:item-item-code-hidden` | custom | Stock | property_setter | Item-item_code-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:item:item-item-code-reqd` | custom | Stock | property_setter | Item-item_code-reqd | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:item:item-naming-series-hidden` | custom | Stock | property_setter | Item-naming_series-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:item:item-naming-series-reqd` | custom | Stock | property_setter | Item-naming_series-reqd | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:job-card:job-card-barcode-hidden` | custom | Manufacturing | property_setter | Job Card-barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:material-request:material-request-scan-barcode-hidden` | custom | Stock | property_setter | Material Request-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:packed-item:packed-item-rate-read-only` | custom | Stock | property_setter | Packed Item-rate-read_only | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:pick-list:pick-list-scan-barcode-hidden` | custom | Stock | property_setter | Pick List-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:pos-invoice-item:pos-invoice-item-barcode-hidden` | custom | Accounts | property_setter | POS Invoice Item-barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:pos-invoice:pos-invoice-scan-barcode-hidden` | custom | Accounts | property_setter | POS Invoice-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-invoice:purchase-invoice-base-rounded-total-hidden` | custom | Accounts | property_setter | Purchase Invoice-base_rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-invoice:purchase-invoice-base-rounded-total-print-hide` | custom | Accounts | property_setter | Purchase Invoice-base_rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-invoice:purchase-invoice-disable-rounded-total-default` | custom | Accounts | property_setter | Purchase Invoice-disable_rounded_total-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-invoice:purchase-invoice-in-words-hidden` | custom | Accounts | property_setter | Purchase Invoice-in_words-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-invoice:purchase-invoice-in-words-print-hide` | custom | Accounts | property_setter | Purchase Invoice-in_words-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-invoice:purchase-invoice-rounded-total-hidden` | custom | Accounts | property_setter | Purchase Invoice-rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-invoice:purchase-invoice-rounded-total-print-hide` | custom | Accounts | property_setter | Purchase Invoice-rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-invoice:purchase-invoice-scan-barcode-hidden` | custom | Accounts | property_setter | Purchase Invoice-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-order:purchase-order-base-rounded-total-hidden` | custom | Buying | property_setter | Purchase Order-base_rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-order:purchase-order-base-rounded-total-print-hide` | custom | Buying | property_setter | Purchase Order-base_rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-order:purchase-order-disable-rounded-total-default` | custom | Buying | property_setter | Purchase Order-disable_rounded_total-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-order:purchase-order-in-words-hidden` | custom | Buying | property_setter | Purchase Order-in_words-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-order:purchase-order-in-words-print-hide` | custom | Buying | property_setter | Purchase Order-in_words-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-order:purchase-order-rounded-total-hidden` | custom | Buying | property_setter | Purchase Order-rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-order:purchase-order-rounded-total-print-hide` | custom | Buying | property_setter | Purchase Order-rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-order:purchase-order-scan-barcode-hidden` | custom | Buying | property_setter | Purchase Order-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt-item:purchase-receipt-item-barcode-hidden` | custom | Stock | property_setter | Purchase Receipt Item-barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-base-rounded-total-hidden` | custom | Stock | property_setter | Purchase Receipt-base_rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-base-rounded-total-print-hide` | custom | Stock | property_setter | Purchase Receipt-base_rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-disable-rounded-total-default` | custom | Stock | property_setter | Purchase Receipt-disable_rounded_total-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-in-words-hidden` | custom | Stock | property_setter | Purchase Receipt-in_words-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-in-words-print-hide` | custom | Stock | property_setter | Purchase Receipt-in_words-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-provisional-expense-account-hidden` | custom | Stock | property_setter | Purchase Receipt-provisional_expense_account-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-rounded-total-hidden` | custom | Stock | property_setter | Purchase Receipt-rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-rounded-total-print-hide` | custom | Stock | property_setter | Purchase Receipt-rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:purchase-receipt:purchase-receipt-scan-barcode-hidden` | custom | Stock | property_setter | Purchase Receipt-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:quotation:quotation-base-rounded-total-hidden` | custom | Selling | property_setter | Quotation-base_rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:quotation:quotation-base-rounded-total-print-hide` | custom | Selling | property_setter | Quotation-base_rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:quotation:quotation-disable-rounded-total-default` | custom | Selling | property_setter | Quotation-disable_rounded_total-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:quotation:quotation-in-words-hidden` | custom | Selling | property_setter | Quotation-in_words-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:quotation:quotation-in-words-print-hide` | custom | Selling | property_setter | Quotation-in_words-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:quotation:quotation-rounded-total-hidden` | custom | Selling | property_setter | Quotation-rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:quotation:quotation-rounded-total-print-hide` | custom | Selling | property_setter | Quotation-rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:quotation:quotation-scan-barcode-hidden` | custom | Selling | property_setter | Quotation-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice-item:sales-invoice-item-barcode-hidden` | custom | Accounts | property_setter | Sales Invoice Item-barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice-item:sales-invoice-item-discount-account-hidden` | custom | Accounts | property_setter | Sales Invoice Item-discount_account-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice-item:sales-invoice-item-discount-account-mandatory-depends-on` | custom | Accounts | property_setter | Sales Invoice Item-discount_account-mandatory_depends_on | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-additional-discount-account-hidden` | custom | Accounts | property_setter | Sales Invoice-additional_discount_account-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-additional-discount-account-mandatory-depends-on` | custom | Accounts | property_setter | Sales Invoice-additional_discount_account-mandatory_depends_on | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-base-rounded-total-hidden` | custom | Accounts | property_setter | Sales Invoice-base_rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-base-rounded-total-print-hide` | custom | Accounts | property_setter | Sales Invoice-base_rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-disable-rounded-total-default` | custom | Accounts | property_setter | Sales Invoice-disable_rounded_total-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-in-words-hidden` | custom | Accounts | property_setter | Sales Invoice-in_words-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-in-words-print-hide` | custom | Accounts | property_setter | Sales Invoice-in_words-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-rounded-total-hidden` | custom | Accounts | property_setter | Sales Invoice-rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-rounded-total-print-hide` | custom | Accounts | property_setter | Sales Invoice-rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-scan-barcode-hidden` | custom | Accounts | property_setter | Sales Invoice-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-tax-id-hidden` | custom | Accounts | property_setter | Sales Invoice-tax_id-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-invoice:sales-invoice-tax-id-print-hide` | custom | Accounts | property_setter | Sales Invoice-tax_id-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-base-rounded-total-hidden` | custom | Selling | property_setter | Sales Order-base_rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-base-rounded-total-print-hide` | custom | Selling | property_setter | Sales Order-base_rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-disable-rounded-total-default` | custom | Selling | property_setter | Sales Order-disable_rounded_total-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-in-words-hidden` | custom | Selling | property_setter | Sales Order-in_words-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-in-words-print-hide` | custom | Selling | property_setter | Sales Order-in_words-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-rounded-total-hidden` | custom | Selling | property_setter | Sales Order-rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-rounded-total-print-hide` | custom | Selling | property_setter | Sales Order-rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-scan-barcode-hidden` | custom | Selling | property_setter | Sales Order-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-tax-id-hidden` | custom | Selling | property_setter | Sales Order-tax_id-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:sales-order:sales-order-tax-id-print-hide` | custom | Selling | property_setter | Sales Order-tax_id-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:stock-entry-detail:stock-entry-detail-barcode-hidden` | custom | Stock | property_setter | Stock Entry Detail-barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:stock-entry:stock-entry-scan-barcode-hidden` | custom | Stock | property_setter | Stock Entry-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:stock-reconciliation-item:stock-reconciliation-item-barcode-hidden` | custom | Stock | property_setter | Stock Reconciliation Item-barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:stock-reconciliation:stock-reconciliation-scan-barcode-hidden` | custom | Stock | property_setter | Stock Reconciliation-scan_barcode-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier-quotation:supplier-quotation-base-rounded-total-hidden` | custom | Buying | property_setter | Supplier Quotation-base_rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier-quotation:supplier-quotation-base-rounded-total-print-hide` | custom | Buying | property_setter | Supplier Quotation-base_rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier-quotation:supplier-quotation-disable-rounded-total-default` | custom | Buying | property_setter | Supplier Quotation-disable_rounded_total-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier-quotation:supplier-quotation-in-words-hidden` | custom | Buying | property_setter | Supplier Quotation-in_words-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier-quotation:supplier-quotation-in-words-print-hide` | custom | Buying | property_setter | Supplier Quotation-in_words-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier-quotation:supplier-quotation-rounded-total-hidden` | custom | Buying | property_setter | Supplier Quotation-rounded_total-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier-quotation:supplier-quotation-rounded-total-print-hide` | custom | Buying | property_setter | Supplier Quotation-rounded_total-print_hide | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier:supplier-naming-series-hidden` | custom | Buying | property_setter | Supplier-naming_series-hidden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `custom:property-setter:supplier:supplier-naming-series-reqd` | custom | Buying | property_setter | Supplier-naming_series-reqd | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `erpnext-chatgpt:doctype:openai-settings` | erpnext_chatgpt | ERPNext ChatGPT | doctype | OpenAI Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext-chatgpt:document-action:openai-settings:test-api-key` | erpnext_chatgpt | ERPNext ChatGPT | document_action | Test API Key | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext-chatgpt:installed-app:erpnext-chatgpt` | erpnext_chatgpt | erpnext_chatgpt | installed_app | erpnext_chatgpt | F | Yes | — | Not implemented | Installed app capabilities require classified Retail ERP routes or safe embedding |
| `erpnext-gemini-integration:dashboard-connection:gemini-page-gemini-sql-dashboard-gemini-sql-dashboard-py:gemini-sql` | erpnext_gemini_integration |  | dashboard_connection | Gemini Sql Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext-gemini-integration:doctype:gemini-assistant-settings` | erpnext_gemini_integration | ERPNext Gemini Integration | doctype | Gemini Assistant Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext-gemini-integration:doctype:gemini-audit-log` | erpnext_gemini_integration | ERPNext Gemini Integration | doctype | Gemini Audit Log | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext-gemini-integration:doctype:gemini-conversation` | erpnext_gemini_integration | ERPNext Gemini Integration | doctype | Gemini Conversation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext-gemini-integration:doctype:gemini-feedback` | erpnext_gemini_integration | ERPNext Gemini Integration | doctype | Gemini Feedback | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext-gemini-integration:doctype:gemini-message` | erpnext_gemini_integration | ERPNext Gemini Integration | doctype | Gemini Message | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext-gemini-integration:doctype:gemini-sensitive-keyword` | erpnext_gemini_integration | ERPNext Gemini Integration | doctype | Gemini Sensitive Keyword | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext-gemini-integration:document-action:gemini-conversation:refresh-messages` | erpnext_gemini_integration | ERPNext Gemini Integration | document_action | Refresh Messages | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext-gemini-integration:document-action:gemini-message:add-feedback` | erpnext_gemini_integration | ERPNext Gemini Integration | document_action | Add Feedback | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext-gemini-integration:installed-app:erpnext-gemini-integration` | erpnext_gemini_integration | erpnext_gemini_integration | installed_app | erpnext_gemini_integration | F | Yes | — | Not implemented | Installed app capabilities require classified Retail ERP routes or safe embedding |
| `erpnext-gemini-integration:page:gemini-sql-dashboard` | erpnext_gemini_integration | Gemini | page | gemini-sql-dashboard | F | Yes | — | Not implemented | Required or safe integration route must be designed |
| `erpnext:child-doctype:accounting-dimension-detail` | erpnext | Accounts | child_doctype | Accounting Dimension Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:advance-tax` | erpnext | Accounts | child_doctype | Advance Tax | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:advance-taxes-and-charges` | erpnext | Accounts | child_doctype | Advance Taxes and Charges | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:allowed-dimension` | erpnext | Accounts | child_doctype | Allowed Dimension | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:allowed-to-transact-with` | erpnext | Accounts | child_doctype | Allowed To Transact With | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:applicable-on-account` | erpnext | Accounts | child_doctype | Applicable On Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:appointment-booking-slots` | erpnext | CRM | child_doctype | Appointment Booking Slots | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:asset-capitalization-asset-item` | erpnext | Assets | child_doctype | Asset Capitalization Asset Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:asset-capitalization-service-item` | erpnext | Assets | child_doctype | Asset Capitalization Service Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:asset-capitalization-stock-item` | erpnext | Assets | child_doctype | Asset Capitalization Stock Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:asset-category-account` | erpnext | Assets | child_doctype | Asset Category Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:asset-finance-book` | erpnext | Assets | child_doctype | Asset Finance Book | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:asset-maintenance-task` | erpnext | Assets | child_doctype | Asset Maintenance Task | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:asset-movement-item` | erpnext | Assets | child_doctype | Asset Movement Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:asset-repair-consumed-item` | erpnext | Assets | child_doctype | Asset Repair Consumed Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:availability-of-slots` | erpnext | CRM | child_doctype | Availability Of Slots | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bank-clearance-detail` | erpnext | Accounts | child_doctype | Bank Clearance Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bank-transaction-mapping` | erpnext | Accounts | child_doctype | Bank Transaction Mapping | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bank-transaction-payments` | erpnext | Accounts | child_doctype | Bank Transaction Payments | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:blanket-order-item` | erpnext | Manufacturing | child_doctype | Blanket Order Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bom-creator-item` | erpnext | Manufacturing | child_doctype | BOM Creator Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bom-explosion-item` | erpnext | Manufacturing | child_doctype | BOM Explosion Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bom-item` | erpnext | Manufacturing | child_doctype | BOM Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bom-operation` | erpnext | Manufacturing | child_doctype | BOM Operation | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bom-scrap-item` | erpnext | Manufacturing | child_doctype | BOM Scrap Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bom-update-batch` | erpnext | Manufacturing | child_doctype | BOM Update Batch | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bom-website-item` | erpnext | Manufacturing | child_doctype | BOM Website Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:bom-website-operation` | erpnext | Manufacturing | child_doctype | BOM Website Operation | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:budget-account` | erpnext | Accounts | child_doctype | Budget Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:campaign-email-schedule` | erpnext | CRM | child_doctype | Campaign Email Schedule | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:campaign-item` | erpnext | Accounts | child_doctype | Campaign Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:cashier-closing-payments` | erpnext | Accounts | child_doctype | Cashier Closing Payments | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:closed-document` | erpnext | Accounts | child_doctype | Closed Document | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:communication-medium-timeslot` | erpnext | Communication | child_doctype | Communication Medium Timeslot | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:competitor-detail` | erpnext | CRM | child_doctype | Competitor Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:contract-fulfilment-checklist` | erpnext | CRM | child_doctype | Contract Fulfilment Checklist | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:contract-template-fulfilment-terms` | erpnext | CRM | child_doctype | Contract Template Fulfilment Terms | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:cost-center-allocation-percentage` | erpnext | Accounts | child_doctype | Cost Center Allocation Percentage | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:crm-note` | erpnext | CRM | child_doctype | CRM Note | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:currency-exchange-settings-details` | erpnext | Accounts | child_doctype | Currency Exchange Settings Details | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:currency-exchange-settings-result` | erpnext | Accounts | child_doctype | Currency Exchange Settings Result | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:customer-credit-limit` | erpnext | Selling | child_doctype | Customer Credit Limit | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:customer-group-item` | erpnext | Accounts | child_doctype | Customer Group Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:customer-item` | erpnext | Accounts | child_doctype | Customer Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:delivery-note-item` | erpnext | Stock | child_doctype | Delivery Note Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:delivery-stop` | erpnext | Stock | child_doctype | Delivery Stop | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:dependent-task` | erpnext | Projects | child_doctype | Dependent Task | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:depreciation-schedule` | erpnext | Assets | child_doctype | Depreciation Schedule | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:discounted-invoice` | erpnext | Accounts | child_doctype | Discounted Invoice | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:driving-license-category` | erpnext | Setup | child_doctype | Driving License Category | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:dunning-letter-text` | erpnext | Accounts | child_doctype | Dunning Letter Text | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:email-digest-recipient` | erpnext | Setup | child_doctype | Email Digest Recipient | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:employee-education` | erpnext | Setup | child_doctype | Employee Education | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:employee-external-work-history` | erpnext | Setup | child_doctype | Employee External Work History | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:employee-group-table` | erpnext | Setup | child_doctype | Employee Group Table | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:employee-internal-work-history` | erpnext | Setup | child_doctype | Employee Internal Work History | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:exchange-rate-revaluation-account` | erpnext | Accounts | child_doctype | Exchange Rate Revaluation Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:fiscal-year-company` | erpnext | Accounts | child_doctype | Fiscal Year Company | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:holiday` | erpnext | Setup | child_doctype | Holiday | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:homepage-section-card` | erpnext | Portal | child_doctype | Homepage Section Card | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:incoming-call-handling-schedule` | erpnext | Telephony | child_doctype | Incoming Call Handling Schedule | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:installation-note-item` | erpnext | Selling | child_doctype | Installation Note Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-attribute-value` | erpnext | Stock | child_doctype | Item Attribute Value | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-barcode` | erpnext | Stock | child_doctype | Item Barcode | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-customer-detail` | erpnext | Stock | child_doctype | Item Customer Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-default` | erpnext | Stock | child_doctype | Item Default | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-quality-inspection-parameter` | erpnext | Stock | child_doctype | Item Quality Inspection Parameter | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-reorder` | erpnext | Stock | child_doctype | Item Reorder | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-supplier` | erpnext | Stock | child_doctype | Item Supplier | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-tax` | erpnext | Stock | child_doctype | Item Tax | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-tax-template-detail` | erpnext | Accounts | child_doctype | Item Tax Template Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-variant` | erpnext | Stock | child_doctype | Item Variant | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-variant-attribute` | erpnext | Stock | child_doctype | Item Variant Attribute | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:item-website-specification` | erpnext | Stock | child_doctype | Item Website Specification | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:job-card-item` | erpnext | Manufacturing | child_doctype | Job Card Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:job-card-operation` | erpnext | Manufacturing | child_doctype | Job Card Operation | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:job-card-scheduled-time` | erpnext | Manufacturing | child_doctype | Job Card Scheduled Time | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:job-card-scrap-item` | erpnext | Manufacturing | child_doctype | Job Card Scrap Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:job-card-time-log` | erpnext | Manufacturing | child_doctype | Job Card Time Log | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:journal-entry-account` | erpnext | Accounts | child_doctype | Journal Entry Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:journal-entry-template-account` | erpnext | Accounts | child_doctype | Journal Entry Template Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:landed-cost-item` | erpnext | Stock | child_doctype | Landed Cost Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:landed-cost-purchase-receipt` | erpnext | Stock | child_doctype | Landed Cost Purchase Receipt | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:landed-cost-taxes-and-charges` | erpnext | Stock | child_doctype | Landed Cost Taxes and Charges | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:ledger-health-monitor-company` | erpnext | Accounts | child_doctype | Ledger Health Monitor Company | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:ledger-merge-accounts` | erpnext | Accounts | child_doctype | Ledger Merge Accounts | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:linked-location` | erpnext | Assets | child_doctype | Linked Location | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:lost-reason-detail` | erpnext | CRM | child_doctype | Lost Reason Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:loyalty-point-entry-redemption` | erpnext | Accounts | child_doctype | Loyalty Point Entry Redemption | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:loyalty-program-collection` | erpnext | Accounts | child_doctype | Loyalty Program Collection | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:maintenance-schedule-detail` | erpnext | Maintenance | child_doctype | Maintenance Schedule Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:maintenance-schedule-item` | erpnext | Maintenance | child_doctype | Maintenance Schedule Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:maintenance-team-member` | erpnext | Assets | child_doctype | Maintenance Team Member | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:maintenance-visit-purpose` | erpnext | Maintenance | child_doctype | Maintenance Visit Purpose | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:material-request-item` | erpnext | Stock | child_doctype | Material Request Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:material-request-plan-item` | erpnext | Manufacturing | child_doctype | Material Request Plan Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:mode-of-payment-account` | erpnext | Accounts | child_doctype | Mode of Payment Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:monthly-distribution-percentage` | erpnext | Accounts | child_doctype | Monthly Distribution Percentage | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:opening-invoice-creation-tool-item` | erpnext | Accounts | child_doctype | Opening Invoice Creation Tool Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:opportunity-item` | erpnext | CRM | child_doctype | Opportunity Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:opportunity-lost-reason-detail` | erpnext | CRM | child_doctype | Opportunity Lost Reason Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:overdue-payment` | erpnext | Accounts | child_doctype | Overdue Payment | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:packed-item` | erpnext | Stock | child_doctype | Packed Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:packing-slip-item` | erpnext | Stock | child_doctype | Packing Slip Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:party-account` | erpnext | Accounts | child_doctype | Party Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pause-sla-on-status` | erpnext | Support | child_doctype | Pause SLA On Status | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:payment-entry-deduction` | erpnext | Accounts | child_doctype | Payment Entry Deduction | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:payment-entry-reference` | erpnext | Accounts | child_doctype | Payment Entry Reference | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:payment-order-reference` | erpnext | Accounts | child_doctype | Payment Order Reference | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:payment-reconciliation-allocation` | erpnext | Accounts | child_doctype | Payment Reconciliation Allocation | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:payment-reconciliation-invoice` | erpnext | Accounts | child_doctype | Payment Reconciliation Invoice | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:payment-reconciliation-payment` | erpnext | Accounts | child_doctype | Payment Reconciliation Payment | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:payment-schedule` | erpnext | Accounts | child_doctype | Payment Schedule | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:payment-terms-template-detail` | erpnext | Accounts | child_doctype | Payment Terms Template Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pegged-currency-details` | erpnext | Accounts | child_doctype | Pegged Currency Details | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pick-list-item` | erpnext | Stock | child_doctype | Pick List Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:portal-user` | erpnext | Utilities | child_doctype | Portal User | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-closing-entry-detail` | erpnext | Accounts | child_doctype | POS Closing Entry Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-closing-entry-taxes` | erpnext | Accounts | child_doctype | POS Closing Entry Taxes | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-customer-group` | erpnext | Accounts | child_doctype | POS Customer Group | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-field` | erpnext | Accounts | child_doctype | POS Field | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-invoice-item` | erpnext | Accounts | child_doctype | POS Invoice Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-invoice-reference` | erpnext | Accounts | child_doctype | POS Invoice Reference | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-item-group` | erpnext | Accounts | child_doctype | POS Item Group | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-opening-entry-detail` | erpnext | Accounts | child_doctype | POS Opening Entry Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-payment-method` | erpnext | Accounts | child_doctype | POS Payment Method | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-profile-user` | erpnext | Accounts | child_doctype | POS Profile User | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pos-search-fields` | erpnext | Accounts | child_doctype | POS Search Fields | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:price-list-country` | erpnext | Stock | child_doctype | Price List Country | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pricing-rule-brand` | erpnext | Accounts | child_doctype | Pricing Rule Brand | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pricing-rule-detail` | erpnext | Accounts | child_doctype | Pricing Rule Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pricing-rule-item-code` | erpnext | Accounts | child_doctype | Pricing Rule Item Code | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:pricing-rule-item-group` | erpnext | Accounts | child_doctype | Pricing Rule Item Group | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:process-payment-reconciliation-log-allocations` | erpnext | Accounts | child_doctype | Process Payment Reconciliation Log Allocations | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:process-period-closing-voucher-detail` | erpnext | Accounts | child_doctype | Process Period Closing Voucher Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:process-statement-of-accounts-cc` | erpnext | Accounts | child_doctype | Process Statement Of Accounts CC | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:process-statement-of-accounts-customer` | erpnext | Accounts | child_doctype | Process Statement Of Accounts Customer | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:product-bundle-item` | erpnext | Selling | child_doctype | Product Bundle Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:production-plan-item` | erpnext | Manufacturing | child_doctype | Production Plan Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:production-plan-item-reference` | erpnext | Manufacturing | child_doctype | Production Plan Item Reference | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:production-plan-material-request` | erpnext | Manufacturing | child_doctype | Production Plan Material Request | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:production-plan-material-request-warehouse` | erpnext | Manufacturing | child_doctype | Production Plan Material Request Warehouse | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:production-plan-sales-order` | erpnext | Manufacturing | child_doctype | Production Plan Sales Order | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:production-plan-sub-assembly-item` | erpnext | Manufacturing | child_doctype | Production Plan Sub Assembly Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:project-template-task` | erpnext | Projects | child_doctype | Project Template Task | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:project-user` | erpnext | Projects | child_doctype | Project User | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:promotional-scheme-price-discount` | erpnext | Accounts | child_doctype | Promotional Scheme Price Discount | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:promotional-scheme-product-discount` | erpnext | Accounts | child_doctype | Promotional Scheme Product Discount | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:prospect-lead` | erpnext | CRM | child_doctype | Prospect Lead | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:prospect-opportunity` | erpnext | CRM | child_doctype | Prospect Opportunity | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:psoa-cost-center` | erpnext | Accounts | child_doctype | PSOA Cost Center | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:psoa-project` | erpnext | Accounts | child_doctype | PSOA Project | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:purchase-invoice-advance` | erpnext | Accounts | child_doctype | Purchase Invoice Advance | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:purchase-invoice-item` | erpnext | Accounts | child_doctype | Purchase Invoice Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:purchase-order-item` | erpnext | Buying | child_doctype | Purchase Order Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:purchase-order-item-supplied` | erpnext | Buying | child_doctype | Purchase Order Item Supplied | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:purchase-receipt-item` | erpnext | Stock | child_doctype | Purchase Receipt Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:purchase-receipt-item-supplied` | erpnext | Buying | child_doctype | Purchase Receipt Item Supplied | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:purchase-taxes-and-charges` | erpnext | Accounts | child_doctype | Purchase Taxes and Charges | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-action-resolution` | erpnext | Quality Management | child_doctype | Quality Action Resolution | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-feedback-parameter` | erpnext | Quality Management | child_doctype | Quality Feedback Parameter | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-feedback-template-parameter` | erpnext | Quality Management | child_doctype | Quality Feedback Template Parameter | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-goal-objective` | erpnext | Quality Management | child_doctype | Quality Goal Objective | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-inspection-reading` | erpnext | Stock | child_doctype | Quality Inspection Reading | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-meeting-agenda` | erpnext | Quality Management | child_doctype | Quality Meeting Agenda | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-meeting-minutes` | erpnext | Quality Management | child_doctype | Quality Meeting Minutes | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-procedure-process` | erpnext | Quality Management | child_doctype | Quality Procedure Process | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quality-review-objective` | erpnext | Quality Management | child_doctype | Quality Review Objective | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quotation-item` | erpnext | Selling | child_doctype | Quotation Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:quotation-lost-reason-detail` | erpnext | Setup | child_doctype | Quotation Lost Reason Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:repost-accounting-ledger-items` | erpnext | Accounts | child_doctype | Repost Accounting Ledger Items | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:repost-allowed-types` | erpnext | Accounts | child_doctype | Repost Allowed Types | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:repost-payment-ledger-items` | erpnext | Accounts | child_doctype | Repost Payment Ledger Items | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:request-for-quotation-item` | erpnext | Buying | child_doctype | Request for Quotation Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:request-for-quotation-supplier` | erpnext | Buying | child_doctype | Request for Quotation Supplier | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sales-invoice-advance` | erpnext | Accounts | child_doctype | Sales Invoice Advance | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sales-invoice-item` | erpnext | Accounts | child_doctype | Sales Invoice Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sales-invoice-payment` | erpnext | Accounts | child_doctype | Sales Invoice Payment | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sales-invoice-timesheet` | erpnext | Accounts | child_doctype | Sales Invoice Timesheet | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sales-order-item` | erpnext | Selling | child_doctype | Sales Order Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sales-partner-item` | erpnext | Accounts | child_doctype | Sales Partner Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sales-taxes-and-charges` | erpnext | Accounts | child_doctype | Sales Taxes and Charges | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sales-team` | erpnext | Selling | child_doctype | Sales Team | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:serial-and-batch-entry` | erpnext | Stock | child_doctype | Serial and Batch Entry | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:service-day` | erpnext | Support | child_doctype | Service Day | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:service-level-priority` | erpnext | Support | child_doctype | Service Level Priority | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:share-balance` | erpnext | Accounts | child_doctype | Share Balance | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:shipment-delivery-note` | erpnext | Stock | child_doctype | Shipment Delivery Note | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:shipment-parcel` | erpnext | Stock | child_doctype | Shipment Parcel | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:shipping-rule-condition` | erpnext | Accounts | child_doctype | Shipping Rule Condition | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:shipping-rule-country` | erpnext | Accounts | child_doctype | Shipping Rule Country | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sla-fulfilled-on-status` | erpnext | Support | child_doctype | SLA Fulfilled On Status | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:south-africa-vat-account` | erpnext | Accounts | child_doctype | South Africa VAT Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:stock-entry-detail` | erpnext | Stock | child_doctype | Stock Entry Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:stock-reconciliation-item` | erpnext | Stock | child_doctype | Stock Reconciliation Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:sub-operation` | erpnext | Manufacturing | child_doctype | Sub Operation | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:subcontracting-order-item` | erpnext | Subcontracting | child_doctype | Subcontracting Order Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:subcontracting-order-service-item` | erpnext | Subcontracting | child_doctype | Subcontracting Order Service Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:subcontracting-order-supplied-item` | erpnext | Subcontracting | child_doctype | Subcontracting Order Supplied Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:subcontracting-receipt-item` | erpnext | Subcontracting | child_doctype | Subcontracting Receipt Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:subcontracting-receipt-supplied-item` | erpnext | Subcontracting | child_doctype | Subcontracting Receipt Supplied Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:subscription-invoice` | erpnext | Accounts | child_doctype | Subscription Invoice | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:subscription-plan-detail` | erpnext | Accounts | child_doctype | Subscription Plan Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:supplier-group-item` | erpnext | Accounts | child_doctype | Supplier Group Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:supplier-item` | erpnext | Accounts | child_doctype | Supplier Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:supplier-quotation-item` | erpnext | Buying | child_doctype | Supplier Quotation Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:supplier-scorecard-scoring-criteria` | erpnext | Buying | child_doctype | Supplier Scorecard Scoring Criteria | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:supplier-scorecard-scoring-standing` | erpnext | Buying | child_doctype | Supplier Scorecard Scoring Standing | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:supplier-scorecard-scoring-variable` | erpnext | Buying | child_doctype | Supplier Scorecard Scoring Variable | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:support-search-source` | erpnext | Support | child_doctype | Support Search Source | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:target-detail` | erpnext | Setup | child_doctype | Target Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:task-depends-on` | erpnext | Projects | child_doctype | Task Depends On | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:tax-withheld-vouchers` | erpnext | Accounts | child_doctype | Tax Withheld Vouchers | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:tax-withholding-account` | erpnext | Accounts | child_doctype | Tax Withholding Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:tax-withholding-rate` | erpnext | Accounts | child_doctype | Tax Withholding Rate | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:territory-item` | erpnext | Accounts | child_doctype | Territory Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:timesheet-detail` | erpnext | Projects | child_doctype | Timesheet Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:transaction-deletion-record-details` | erpnext | Accounts | child_doctype | Transaction Deletion Record Details | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:transaction-deletion-record-item` | erpnext | Setup | child_doctype | Transaction Deletion Record Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:uae-vat-account` | erpnext | Regional | child_doctype | UAE VAT Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:unreconcile-payment-entries` | erpnext | Accounts | child_doctype | Unreconcile Payment Entries | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:uom-conversion-detail` | erpnext | Stock | child_doctype | UOM Conversion Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:variant-field` | erpnext | Stock | child_doctype | Variant Field | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:website-attribute` | erpnext | Portal | child_doctype | Website Attribute | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:website-filter-field` | erpnext | Portal | child_doctype | Website Filter Field | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:website-item-group` | erpnext | Setup | child_doctype | Website Item Group | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:work-order-item` | erpnext | Manufacturing | child_doctype | Work Order Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:work-order-operation` | erpnext | Manufacturing | child_doctype | Work Order Operation | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:child-doctype:workstation-working-hour` | erpnext | Manufacturing | child_doctype | Workstation Working Hour | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `erpnext:dashboard-chart:accounts-payable-ageing` | erpnext | Accounts | dashboard_chart | Accounts Payable Ageing | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:accounts-receivable-ageing` | erpnext | Accounts | dashboard_chart | Accounts Receivable Ageing | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:asset-value-analytics` | erpnext | Assets | dashboard_chart | Asset Value Analytics | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:bank-balance` | erpnext | Accounts | dashboard_chart | Bank Balance | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:budget-variance` | erpnext | Accounts | dashboard_chart | Budget Variance | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:category-wise-asset-value` | erpnext | Assets | dashboard_chart | Category-wise Asset Value | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:completed-operation` | erpnext | Manufacturing | dashboard_chart | Completed Operation | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:completed-projects` | erpnext | Projects | dashboard_chart | Completed Projects | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:delivery-trends` | erpnext | Stock | dashboard_chart | Delivery Trends | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:incoming-bills-purchase-invoice` | erpnext | Accounts | dashboard_chart | Incoming Bills (Purchase Invoice) | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:incoming-leads` | erpnext | CRM | dashboard_chart | Incoming Leads | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:item-shortage-summary` | erpnext | Stock | dashboard_chart | Item Shortage Summary | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:item-wise-annual-sales` | erpnext | Selling | dashboard_chart | Item-wise Annual Sales | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:job-card-analysis` | erpnext | Manufacturing | dashboard_chart | Job Card Analysis | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:last-month-downtime-analysis` | erpnext | Manufacturing | dashboard_chart | Last Month Downtime Analysis | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:lead-source` | erpnext | CRM | dashboard_chart | Lead Source | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:location-wise-asset-value` | erpnext | Assets | dashboard_chart | Location-wise Asset Value | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:material-request-analysis` | erpnext | Buying | dashboard_chart | Material Request Analysis | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:oldest-items` | erpnext | Stock | dashboard_chart | Oldest Items | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:opportunities-via-campaigns` | erpnext | CRM | dashboard_chart | Opportunities via Campaigns | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:opportunity-trends` | erpnext | CRM | dashboard_chart | Opportunity Trends | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:outgoing-bills-sales-invoice` | erpnext | Accounts | dashboard_chart | Outgoing Bills (Sales Invoice) | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:pending-work-order` | erpnext | Manufacturing | dashboard_chart | Pending Work Order | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:produced-quantity` | erpnext | Manufacturing | dashboard_chart | Produced Quantity | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:profit-and-loss` | erpnext | Accounts | dashboard_chart | Profit and Loss | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:project-summary` | erpnext | Projects | dashboard_chart | Project Summary | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:purchase-order-analysis` | erpnext | Buying | dashboard_chart | Purchase Order Analysis | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:purchase-order-trends` | erpnext | Buying | dashboard_chart | Purchase Order Trends | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:purchase-receipt-trends` | erpnext | Stock | dashboard_chart | Purchase Receipt Trends | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:quality-inspection-analysis` | erpnext | Manufacturing | dashboard_chart | Quality Inspection Analysis | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:quality-inspections` | erpnext | Quality Management | dashboard_chart | Quality Inspections | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:sales-order-analysis` | erpnext | Selling | dashboard_chart | Sales Order Analysis | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:sales-order-trends` | erpnext | Selling | dashboard_chart | Sales Order Trends | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:stock-value-by-item-group` | erpnext | Stock | dashboard_chart | Stock Value by Item Group | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:subcontracting-order` | erpnext | Subcontracting | dashboard_chart | Subcontracting Order | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:territory-wise-opportunity-count` | erpnext | CRM | dashboard_chart | Territory Wise Opportunity Count | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:territory-wise-sales` | erpnext | CRM | dashboard_chart | Territory Wise Sales | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:top-customers` | erpnext | Selling | dashboard_chart | Top Customers | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:top-suppliers` | erpnext | Buying | dashboard_chart | Top Suppliers | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:warehouse-wise-stock-value` | erpnext | Stock | dashboard_chart | Warehouse wise Stock Value | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:won-opportunities` | erpnext | CRM | dashboard_chart | Won Opportunities | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:work-order-analysis` | erpnext | Manufacturing | dashboard_chart | Work Order Analysis | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-chart:work-order-qty-analysis` | erpnext | Manufacturing | dashboard_chart | Work Order Qty Analysis | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `erpnext:dashboard-connection:accounts-doctype-bank-bank-dashboard-py:bank` | erpnext |  | dashboard_connection | Bank Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-cost-center-cost-center-dashboard-py:cost-center` | erpnext |  | dashboard_connection | Cost Center Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-exchange-rate-revaluation-exchange-rate-revaluation-dashboard-py:exchange-rate-revaluation` | erpnext |  | dashboard_connection | Exchange Rate Revaluation Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-finance-book-finance-book-dashboard-py:finance-book` | erpnext |  | dashboard_connection | Finance Book Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-fiscal-year-fiscal-year-dashboard-py:fiscal-year` | erpnext |  | dashboard_connection | Fiscal Year Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-invoice-discounting-invoice-discounting-dashboard-py:invoice-discounting` | erpnext |  | dashboard_connection | Invoice Discounting Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-item-tax-template-item-tax-template-dashboard-py:item-tax-template` | erpnext |  | dashboard_connection | Item Tax Template Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-loyalty-program-loyalty-program-dashboard-py:loyalty-program` | erpnext |  | dashboard_connection | Loyalty Program Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-monthly-distribution-monthly-distribution-dashboard-py:monthly-distribution` | erpnext |  | dashboard_connection | Monthly Distribution Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-payment-gateway-account-payment-gateway-account-dashboard-py:payment-gateway-account` | erpnext |  | dashboard_connection | Payment Gateway Account Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-payment-order-payment-order-dashboard-py:payment-order` | erpnext |  | dashboard_connection | Payment Order Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-payment-request-payment-request-dashboard-py:payment-request` | erpnext |  | dashboard_connection | Payment Request Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-payment-term-payment-term-dashboard-py:payment-term` | erpnext |  | dashboard_connection | Payment Term Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-payment-terms-template-payment-terms-template-dashboard-py:payment-terms-template` | erpnext |  | dashboard_connection | Payment Terms Template Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-process-payment-reconciliation-process-payment-reconciliation-dashboard-py:process-payment-reconciliation` | erpnext |  | dashboard_connection | Process Payment Reconciliation Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-promotional-scheme-promotional-scheme-dashboard-py:promotional-scheme` | erpnext |  | dashboard_connection | Promotional Scheme Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-purchase-invoice-purchase-invoice-dashboard-py:purchase-invoice` | erpnext |  | dashboard_connection | Purchase Invoice Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-purchase-taxes-and-charges-template-purchase-taxes-and-charges-template-dashboard-py:purchase-taxes-and-charges-template` | erpnext |  | dashboard_connection | Purchase Taxes and Charges Template Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-sales-invoice-sales-invoice-dashboard-py:sales-invoice` | erpnext |  | dashboard_connection | Sales Invoice Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-sales-taxes-and-charges-template-sales-taxes-and-charges-template-dashboard-py:sales-taxes-and-charges-template` | erpnext |  | dashboard_connection | Sales Taxes and Charges Template Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-share-type-share-type-dashboard-py:share-type` | erpnext |  | dashboard_connection | Share Type Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-shareholder-shareholder-dashboard-py:shareholder` | erpnext |  | dashboard_connection | Shareholder Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-shipping-rule-shipping-rule-dashboard-py:shipping-rule` | erpnext |  | dashboard_connection | Shipping Rule Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-subscription-plan-subscription-plan-dashboard-py:subscription-plan` | erpnext |  | dashboard_connection | Subscription Plan Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-tax-category-tax-category-dashboard-py:tax-category` | erpnext |  | dashboard_connection | Tax Category Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:accounts-doctype-tax-withholding-category-tax-withholding-category-dashboard-py:tax-withholding-category` | erpnext |  | dashboard_connection | Tax Withholding Category Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:assets-doctype-asset-asset-dashboard-py:asset` | erpnext |  | dashboard_connection | Asset Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:buying-doctype-purchase-order-purchase-order-dashboard-py:purchase-order` | erpnext |  | dashboard_connection | Purchase Order Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:buying-doctype-request-for-quotation-request-for-quotation-dashboard-py:request-for-quotation` | erpnext |  | dashboard_connection | Request for Quotation Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:buying-doctype-supplier-quotation-supplier-quotation-dashboard-py:supplier-quotation` | erpnext |  | dashboard_connection | Supplier Quotation Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:buying-doctype-supplier-scorecard-supplier-scorecard-dashboard-py:supplier-scorecard` | erpnext |  | dashboard_connection | Supplier Scorecard Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:buying-doctype-supplier-supplier-dashboard-py:supplier` | erpnext |  | dashboard_connection | Supplier Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:crm-doctype-lead-lead-dashboard-py:lead` | erpnext |  | dashboard_connection | Lead Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:crm-doctype-opportunity-opportunity-dashboard-py:opportunity` | erpnext |  | dashboard_connection | Opportunity Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:manufacturing-doctype-blanket-order-blanket-order-dashboard-py:blanket-order` | erpnext |  | dashboard_connection | Blanket Order Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:manufacturing-doctype-bom-bom-dashboard-py:bom` | erpnext |  | dashboard_connection | BOM Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:manufacturing-doctype-job-card-job-card-dashboard-py:job-card` | erpnext |  | dashboard_connection | Job Card Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:manufacturing-doctype-operation-operation-dashboard-py:operation` | erpnext |  | dashboard_connection | Operation Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:manufacturing-doctype-production-plan-production-plan-dashboard-py:production-plan` | erpnext |  | dashboard_connection | Production Plan Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:manufacturing-doctype-routing-routing-dashboard-py:routing` | erpnext |  | dashboard_connection | Routing Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:manufacturing-doctype-work-order-work-order-dashboard-py:work-order` | erpnext |  | dashboard_connection | Work Order Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:manufacturing-doctype-workstation-workstation-dashboard-py:workstation` | erpnext |  | dashboard_connection | Workstation Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:projects-doctype-project-project-dashboard-py:project` | erpnext |  | dashboard_connection | Project Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:projects-doctype-project-template-project-template-dashboard-py:project-template` | erpnext |  | dashboard_connection | Project Template Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:projects-doctype-task-task-dashboard-py:task` | erpnext |  | dashboard_connection | Task Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:projects-doctype-timesheet-timesheet-dashboard-py:timesheet` | erpnext |  | dashboard_connection | Timesheet Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:selling-doctype-customer-customer-dashboard-py:customer` | erpnext |  | dashboard_connection | Customer Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:selling-doctype-quotation-quotation-dashboard-py:quotation` | erpnext |  | dashboard_connection | Quotation Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:selling-doctype-sales-order-sales-order-dashboard-py:sales-order` | erpnext |  | dashboard_connection | Sales Order Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:setup-doctype-company-company-dashboard-py:company` | erpnext |  | dashboard_connection | Company Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:setup-doctype-holiday-list-holiday-list-dashboard-py:holiday-list` | erpnext |  | dashboard_connection | Holiday List Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:setup-doctype-sales-person-sales-person-dashboard-py:sales-person` | erpnext |  | dashboard_connection | Sales Person Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:setup-doctype-vehicle-vehicle-dashboard-py:vehicle` | erpnext |  | dashboard_connection | Vehicle Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-dashboard-item-dashboard-py:item` | erpnext |  | dashboard_connection | Item Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-dashboard-warehouse-capacity-dashboard-py:warehouse-capacity` | erpnext |  | dashboard_connection | Warehouse Capacity Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-doctype-batch-batch-dashboard-py:batch` | erpnext |  | dashboard_connection | Batch Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-doctype-delivery-note-delivery-note-dashboard-py:delivery-note` | erpnext |  | dashboard_connection | Delivery Note Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-doctype-item-item-dashboard-py:item` | erpnext |  | dashboard_connection | Item Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-doctype-material-request-material-request-dashboard-py:material-request` | erpnext |  | dashboard_connection | Material Request Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-doctype-pick-list-pick-list-dashboard-py:pick-list` | erpnext |  | dashboard_connection | Pick List Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-doctype-purchase-receipt-purchase-receipt-dashboard-py:purchase-receipt` | erpnext |  | dashboard_connection | Purchase Receipt Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:stock-doctype-stock-entry-stock-entry-dashboard-py:stock-entry` | erpnext |  | dashboard_connection | Stock Entry Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:subcontracting-doctype-subcontracting-order-subcontracting-order-dashboard-py:subcontracting-order` | erpnext |  | dashboard_connection | Subcontracting Order Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:subcontracting-doctype-subcontracting-receipt-subcontracting-receipt-dashboard-py:subcontracting-receipt` | erpnext |  | dashboard_connection | Subcontracting Receipt Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard-connection:support-doctype-issue-issue-dashboard-py:issue` | erpnext |  | dashboard_connection | Issue Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `erpnext:dashboard:accounts` | erpnext | Accounts | dashboard | Accounts | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:dashboard:asset` | erpnext | Assets | dashboard | Asset | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:dashboard:buying` | erpnext | Buying | dashboard | Buying | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:dashboard:crm` | erpnext | CRM | dashboard | CRM | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:dashboard:manufacturing` | erpnext | Manufacturing | dashboard | Manufacturing | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:dashboard:payments` | erpnext | Accounts | dashboard | Payments | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:dashboard:project` | erpnext | Projects | dashboard | Project | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:dashboard:selling` | erpnext | Selling | dashboard | Selling | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:dashboard:stock` | erpnext | Stock | dashboard | Stock | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:doctype:account` | erpnext | Accounts | doctype | Account | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:account-closing-balance` | erpnext | Accounts | doctype | Account Closing Balance | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:accounting-dimension` | erpnext | Accounts | doctype | Accounting Dimension | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:accounting-dimension-filter` | erpnext | Accounts | doctype | Accounting Dimension Filter | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:accounting-period` | erpnext | Accounts | doctype | Accounting Period | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:accounts-settings` | erpnext | Accounts | doctype | Accounts Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:activity-cost` | erpnext | Projects | doctype | Activity Cost | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:activity-type` | erpnext | Projects | doctype | Activity Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:advance-payment-ledger-entry` | erpnext | Accounts | doctype | Advance Payment Ledger Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:appointment` | erpnext | CRM | doctype | Appointment | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:appointment-booking-settings` | erpnext | CRM | doctype | Appointment Booking Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset` | erpnext | Assets | doctype | Asset | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-activity` | erpnext | Assets | doctype | Asset Activity | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-capitalization` | erpnext | Assets | doctype | Asset Capitalization | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-category` | erpnext | Assets | doctype | Asset Category | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-depreciation-schedule` | erpnext | Assets | doctype | Asset Depreciation Schedule | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-maintenance` | erpnext | Assets | doctype | Asset Maintenance | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-maintenance-log` | erpnext | Assets | doctype | Asset Maintenance Log | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-maintenance-team` | erpnext | Assets | doctype | Asset Maintenance Team | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-movement` | erpnext | Assets | doctype | Asset Movement | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-repair` | erpnext | Assets | doctype | Asset Repair | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-shift-allocation` | erpnext | Assets | doctype | Asset Shift Allocation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-shift-factor` | erpnext | Assets | doctype | Asset Shift Factor | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:asset-value-adjustment` | erpnext | Assets | doctype | Asset Value Adjustment | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:authorization-control` | erpnext | Setup | doctype | Authorization Control | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:authorization-rule` | erpnext | Setup | doctype | Authorization Rule | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank` | erpnext | Accounts | doctype | Bank | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank-account` | erpnext | Accounts | doctype | Bank Account | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank-account-subtype` | erpnext | Accounts | doctype | Bank Account Subtype | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank-account-type` | erpnext | Accounts | doctype | Bank Account Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank-clearance` | erpnext | Accounts | doctype | Bank Clearance | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank-guarantee` | erpnext | Accounts | doctype | Bank Guarantee | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank-reconciliation-tool` | erpnext | Accounts | doctype | Bank Reconciliation Tool | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank-statement-import` | erpnext | Accounts | doctype | Bank Statement Import | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bank-transaction` | erpnext | Accounts | doctype | Bank Transaction | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:batch` | erpnext | Stock | doctype | Batch | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bin` | erpnext | Stock | doctype | Bin | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bisect-accounting-statements` | erpnext | Accounts | doctype | Bisect Accounting Statements | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bisect-nodes` | erpnext | Accounts | doctype | Bisect Nodes | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:blanket-order` | erpnext | Manufacturing | doctype | Blanket Order | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bom` | erpnext | Manufacturing | doctype | BOM | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bom-creator` | erpnext | Manufacturing | doctype | BOM Creator | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bom-update-log` | erpnext | Manufacturing | doctype | BOM Update Log | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bom-update-tool` | erpnext | Manufacturing | doctype | BOM Update Tool | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:branch` | erpnext | Setup | doctype | Branch | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:brand` | erpnext | Setup | doctype | Brand | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:budget` | erpnext | Accounts | doctype | Budget | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bulk-transaction-log` | erpnext | Bulk Transaction | doctype | Bulk Transaction Log | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:bulk-transaction-log-detail` | erpnext | Bulk Transaction | doctype | Bulk Transaction Log Detail | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:buying-settings` | erpnext | Buying | doctype | Buying Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:call-log` | erpnext | Telephony | doctype | Call Log | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:campaign` | erpnext | CRM | doctype | Campaign | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:cashier-closing` | erpnext | Accounts | doctype | Cashier Closing | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:chart-of-accounts-importer` | erpnext | Accounts | doctype | Chart of Accounts Importer | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:cheque-print-template` | erpnext | Accounts | doctype | Cheque Print Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:closing-stock-balance` | erpnext | Stock | doctype | Closing Stock Balance | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:code-list` | erpnext | EDI | doctype | Code List | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:common-code` | erpnext | EDI | doctype | Common Code | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:communication-medium` | erpnext | Communication | doctype | Communication Medium | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:company` | erpnext | Setup | doctype | Company | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:competitor` | erpnext | CRM | doctype | Competitor | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:contract` | erpnext | CRM | doctype | Contract | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:contract-template` | erpnext | CRM | doctype | Contract Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:cost-center` | erpnext | Accounts | doctype | Cost Center | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:cost-center-allocation` | erpnext | Accounts | doctype | Cost Center Allocation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:coupon-code` | erpnext | Accounts | doctype | Coupon Code | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:crm-settings` | erpnext | CRM | doctype | CRM Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:currency-exchange` | erpnext | Setup | doctype | Currency Exchange | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:currency-exchange-settings` | erpnext | Accounts | doctype | Currency Exchange Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:customer` | erpnext | Selling | doctype | Customer | A | Yes | /retail-erp/sales/customers | Read-only list/detail implemented; forms and actions pending | Create/edit, workflow, actions, print and communication remain |
| `erpnext:doctype:customer-group` | erpnext | Setup | doctype | Customer Group | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:customs-tariff-number` | erpnext | Stock | doctype | Customs Tariff Number | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:delivery-note` | erpnext | Stock | doctype | Delivery Note | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:delivery-settings` | erpnext | Stock | doctype | Delivery Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:delivery-trip` | erpnext | Stock | doctype | Delivery Trip | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:department` | erpnext | Setup | doctype | Department | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:designation` | erpnext | Setup | doctype | Designation | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:downtime-entry` | erpnext | Manufacturing | doctype | Downtime Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:driver` | erpnext | Setup | doctype | Driver | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:dunning` | erpnext | Accounts | doctype | Dunning | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:dunning-type` | erpnext | Accounts | doctype | Dunning Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:email-campaign` | erpnext | CRM | doctype | Email Campaign | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:email-digest` | erpnext | Setup | doctype | Email Digest | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:employee` | erpnext | Setup | doctype | Employee | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:employee-group` | erpnext | Setup | doctype | Employee Group | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:exchange-rate-revaluation` | erpnext | Accounts | doctype | Exchange Rate Revaluation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:finance-book` | erpnext | Accounts | doctype | Finance Book | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:fiscal-year` | erpnext | Accounts | doctype | Fiscal Year | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:gl-entry` | erpnext | Accounts | doctype | GL Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:global-defaults` | erpnext | Setup | doctype | Global Defaults | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:holiday-list` | erpnext | Setup | doctype | Holiday List | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:homepage` | erpnext | Portal | doctype | Homepage | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:homepage-section` | erpnext | Portal | doctype | Homepage Section | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:import-supplier-invoice` | erpnext | Regional | doctype | Import Supplier Invoice | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:incoming-call-settings` | erpnext | Telephony | doctype | Incoming Call Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:incoterm` | erpnext | Setup | doctype | Incoterm | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:industry-type` | erpnext | Selling | doctype | Industry Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:installation-note` | erpnext | Selling | doctype | Installation Note | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:inventory-dimension` | erpnext | Stock | doctype | Inventory Dimension | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:invoice-discounting` | erpnext | Accounts | doctype | Invoice Discounting | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:issue` | erpnext | Support | doctype | Issue | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:issue-priority` | erpnext | Support | doctype | Issue Priority | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:issue-type` | erpnext | Support | doctype | Issue Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:item` | erpnext | Stock | doctype | Item | B | Yes | /retail-erp/inventory/products | Read-only list/detail implemented; forms and actions pending | Create/edit, workflow, actions, print and communication remain |
| `erpnext:doctype:item-alternative` | erpnext | Stock | doctype | Item Alternative | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:item-attribute` | erpnext | Stock | doctype | Item Attribute | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:item-group` | erpnext | Setup | doctype | Item Group | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:item-manufacturer` | erpnext | Stock | doctype | Item Manufacturer | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:item-price` | erpnext | Stock | doctype | Item Price | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:item-tax-template` | erpnext | Accounts | doctype | Item Tax Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:item-variant-settings` | erpnext | Stock | doctype | Item Variant Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:job-card` | erpnext | Manufacturing | doctype | Job Card | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:journal-entry` | erpnext | Accounts | doctype | Journal Entry | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:journal-entry-template` | erpnext | Accounts | doctype | Journal Entry Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:landed-cost-voucher` | erpnext | Stock | doctype | Landed Cost Voucher | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:lead` | erpnext | CRM | doctype | Lead | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:lead-source` | erpnext | CRM | doctype | Lead Source | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:ledger-health` | erpnext | Accounts | doctype | Ledger Health | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:ledger-health-monitor` | erpnext | Accounts | doctype | Ledger Health Monitor | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:ledger-merge` | erpnext | Accounts | doctype | Ledger Merge | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:location` | erpnext | Assets | doctype | Location | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:lower-deduction-certificate` | erpnext | Regional | doctype | Lower Deduction Certificate | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:loyalty-point-entry` | erpnext | Accounts | doctype | Loyalty Point Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:loyalty-program` | erpnext | Accounts | doctype | Loyalty Program | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:maintenance-schedule` | erpnext | Maintenance | doctype | Maintenance Schedule | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:maintenance-visit` | erpnext | Maintenance | doctype | Maintenance Visit | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:manufacturer` | erpnext | Stock | doctype | Manufacturer | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:manufacturing-settings` | erpnext | Manufacturing | doctype | Manufacturing Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:market-segment` | erpnext | CRM | doctype | Market Segment | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:material-request` | erpnext | Stock | doctype | Material Request | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:mode-of-payment` | erpnext | Accounts | doctype | Mode of Payment | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:monthly-distribution` | erpnext | Accounts | doctype | Monthly Distribution | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:non-conformance` | erpnext | Quality Management | doctype | Non Conformance | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:opening-invoice-creation-tool` | erpnext | Accounts | doctype | Opening Invoice Creation Tool | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:operation` | erpnext | Manufacturing | doctype | Operation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:opportunity` | erpnext | CRM | doctype | Opportunity | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:opportunity-lost-reason` | erpnext | CRM | doctype | Opportunity Lost Reason | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:opportunity-type` | erpnext | CRM | doctype | Opportunity Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:packing-slip` | erpnext | Stock | doctype | Packing Slip | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:party-link` | erpnext | Accounts | doctype | Party Link | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:party-specific-item` | erpnext | Selling | doctype | Party Specific Item | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:party-type` | erpnext | Setup | doctype | Party Type | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:payment-entry` | erpnext | Accounts | doctype | Payment Entry | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:payment-gateway-account` | erpnext | Accounts | doctype | Payment Gateway Account | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:payment-ledger-entry` | erpnext | Accounts | doctype | Payment Ledger Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:payment-order` | erpnext | Accounts | doctype | Payment Order | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:payment-reconciliation` | erpnext | Accounts | doctype | Payment Reconciliation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:payment-request` | erpnext | Accounts | doctype | Payment Request | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:payment-term` | erpnext | Accounts | doctype | Payment Term | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:payment-terms-template` | erpnext | Accounts | doctype | Payment Terms Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pegged-currencies` | erpnext | Accounts | doctype | Pegged Currencies | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:period-closing-voucher` | erpnext | Accounts | doctype | Period Closing Voucher | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pick-list` | erpnext | Stock | doctype | Pick List | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:plaid-settings` | erpnext | ERPNext Integrations | doctype | Plaid Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:plant-floor` | erpnext | Manufacturing | doctype | Plant Floor | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pos-closing-entry` | erpnext | Accounts | doctype | POS Closing Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pos-invoice` | erpnext | Accounts | doctype | POS Invoice | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pos-invoice-merge-log` | erpnext | Accounts | doctype | POS Invoice Merge Log | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pos-opening-entry` | erpnext | Accounts | doctype | POS Opening Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pos-profile` | erpnext | Accounts | doctype | POS Profile | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pos-settings` | erpnext | Accounts | doctype | POS Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:price-list` | erpnext | Stock | doctype | Price List | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:pricing-rule` | erpnext | Accounts | doctype | Pricing Rule | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:print-heading` | erpnext | Setup | doctype | Print Heading | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:process-deferred-accounting` | erpnext | Accounts | doctype | Process Deferred Accounting | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:process-payment-reconciliation` | erpnext | Accounts | doctype | Process Payment Reconciliation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:process-payment-reconciliation-log` | erpnext | Accounts | doctype | Process Payment Reconciliation Log | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:process-period-closing-voucher` | erpnext | Accounts | doctype | Process Period Closing Voucher | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:process-statement-of-accounts` | erpnext | Accounts | doctype | Process Statement Of Accounts | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:process-subscription` | erpnext | Accounts | doctype | Process Subscription | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:product-bundle` | erpnext | Selling | doctype | Product Bundle | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:production-plan` | erpnext | Manufacturing | doctype | Production Plan | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:project` | erpnext | Projects | doctype | Project | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:project-template` | erpnext | Projects | doctype | Project Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:project-type` | erpnext | Projects | doctype | Project Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:project-update` | erpnext | Projects | doctype | Project Update | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:projects-settings` | erpnext | Projects | doctype | Projects Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:promotional-scheme` | erpnext | Accounts | doctype | Promotional Scheme | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:prospect` | erpnext | CRM | doctype | Prospect | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:purchase-invoice` | erpnext | Accounts | doctype | Purchase Invoice | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:purchase-order` | erpnext | Buying | doctype | Purchase Order | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:purchase-receipt` | erpnext | Stock | doctype | Purchase Receipt | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:purchase-taxes-and-charges-template` | erpnext | Accounts | doctype | Purchase Taxes and Charges Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:putaway-rule` | erpnext | Stock | doctype | Putaway Rule | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-action` | erpnext | Quality Management | doctype | Quality Action | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-feedback` | erpnext | Quality Management | doctype | Quality Feedback | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-feedback-template` | erpnext | Quality Management | doctype | Quality Feedback Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-goal` | erpnext | Quality Management | doctype | Quality Goal | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-inspection` | erpnext | Stock | doctype | Quality Inspection | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-inspection-parameter` | erpnext | Stock | doctype | Quality Inspection Parameter | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-inspection-parameter-group` | erpnext | Stock | doctype | Quality Inspection Parameter Group | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-inspection-template` | erpnext | Stock | doctype | Quality Inspection Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-meeting` | erpnext | Quality Management | doctype | Quality Meeting | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-procedure` | erpnext | Quality Management | doctype | Quality Procedure | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quality-review` | erpnext | Quality Management | doctype | Quality Review | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quick-stock-balance` | erpnext | Stock | doctype | Quick Stock Balance | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quotation` | erpnext | Selling | doctype | Quotation | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:quotation-lost-reason` | erpnext | Setup | doctype | Quotation Lost Reason | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:rename-tool` | erpnext | Utilities | doctype | Rename Tool | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:repost-accounting-ledger` | erpnext | Accounts | doctype | Repost Accounting Ledger | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:repost-accounting-ledger-settings` | erpnext | Accounts | doctype | Repost Accounting Ledger Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:repost-item-valuation` | erpnext | Stock | doctype | Repost Item Valuation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:repost-payment-ledger` | erpnext | Accounts | doctype | Repost Payment Ledger | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:request-for-quotation` | erpnext | Buying | doctype | Request for Quotation | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:routing` | erpnext | Manufacturing | doctype | Routing | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:sales-invoice` | erpnext | Accounts | doctype | Sales Invoice | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:sales-order` | erpnext | Selling | doctype | Sales Order | B | Yes | /retail-erp/sales/orders | Read-only list/detail implemented; forms and actions pending | Create/edit, workflow, actions, print and communication remain |
| `erpnext:doctype:sales-partner` | erpnext | Setup | doctype | Sales Partner | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:sales-partner-type` | erpnext | Selling | doctype | Sales Partner Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:sales-person` | erpnext | Setup | doctype | Sales Person | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:sales-stage` | erpnext | CRM | doctype | Sales Stage | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:sales-taxes-and-charges-template` | erpnext | Accounts | doctype | Sales Taxes and Charges Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:selling-settings` | erpnext | Selling | doctype | Selling Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:serial-and-batch-bundle` | erpnext | Stock | doctype | Serial and Batch Bundle | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:serial-no` | erpnext | Stock | doctype | Serial No | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:service-level-agreement` | erpnext | Support | doctype | Service Level Agreement | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:share-transfer` | erpnext | Accounts | doctype | Share Transfer | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:share-type` | erpnext | Accounts | doctype | Share Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:shareholder` | erpnext | Accounts | doctype | Shareholder | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:shipment` | erpnext | Stock | doctype | Shipment | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:shipment-parcel-template` | erpnext | Stock | doctype | Shipment Parcel Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:shipping-rule` | erpnext | Accounts | doctype | Shipping Rule | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:sms-center` | erpnext | Selling | doctype | SMS Center | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:sms-log` | erpnext | Utilities | doctype | SMS Log | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:south-africa-vat-settings` | erpnext | Regional | doctype | South Africa VAT Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:stock-entry` | erpnext | Stock | doctype | Stock Entry | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:stock-entry-type` | erpnext | Stock | doctype | Stock Entry Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:stock-ledger-entry` | erpnext | Stock | doctype | Stock Ledger Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:stock-reconciliation` | erpnext | Stock | doctype | Stock Reconciliation | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:stock-reposting-settings` | erpnext | Stock | doctype | Stock Reposting Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:stock-reservation-entry` | erpnext | Stock | doctype | Stock Reservation Entry | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:stock-settings` | erpnext | Stock | doctype | Stock Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:subcontracting-bom` | erpnext | Subcontracting | doctype | Subcontracting BOM | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:subcontracting-order` | erpnext | Subcontracting | doctype | Subcontracting Order | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:subcontracting-receipt` | erpnext | Subcontracting | doctype | Subcontracting Receipt | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:subscription` | erpnext | Accounts | doctype | Subscription | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:subscription-plan` | erpnext | Accounts | doctype | Subscription Plan | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:subscription-settings` | erpnext | Accounts | doctype | Subscription Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:supplier` | erpnext | Buying | doctype | Supplier | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:supplier-group` | erpnext | Setup | doctype | Supplier Group | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:supplier-quotation` | erpnext | Buying | doctype | Supplier Quotation | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:supplier-scorecard` | erpnext | Buying | doctype | Supplier Scorecard | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:supplier-scorecard-criteria` | erpnext | Buying | doctype | Supplier Scorecard Criteria | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:supplier-scorecard-period` | erpnext | Buying | doctype | Supplier Scorecard Period | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:supplier-scorecard-standing` | erpnext | Buying | doctype | Supplier Scorecard Standing | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:supplier-scorecard-variable` | erpnext | Buying | doctype | Supplier Scorecard Variable | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:support-settings` | erpnext | Support | doctype | Support Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:task` | erpnext | Projects | doctype | Task | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:task-type` | erpnext | Projects | doctype | Task Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:tax-category` | erpnext | Accounts | doctype | Tax Category | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:tax-rule` | erpnext | Accounts | doctype | Tax Rule | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:tax-withholding-category` | erpnext | Accounts | doctype | Tax Withholding Category | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:telephony-call-type` | erpnext | Telephony | doctype | Telephony Call Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:terms-and-conditions` | erpnext | Setup | doctype | Terms and Conditions | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:territory` | erpnext | Setup | doctype | Territory | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:timesheet` | erpnext | Projects | doctype | Timesheet | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:transaction-deletion-record` | erpnext | Setup | doctype | Transaction Deletion Record | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:uae-vat-settings` | erpnext | Regional | doctype | UAE VAT Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:unreconcile-payment` | erpnext | Accounts | doctype | Unreconcile Payment | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:uom` | erpnext | Setup | doctype | UOM | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:uom-category` | erpnext | Stock | doctype | UOM Category | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:uom-conversion-factor` | erpnext | Setup | doctype | UOM Conversion Factor | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:vehicle` | erpnext | Setup | doctype | Vehicle | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:video` | erpnext | Utilities | doctype | Video | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:video-settings` | erpnext | Utilities | doctype | Video Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:voice-call-settings` | erpnext | Telephony | doctype | Voice Call Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:warehouse` | erpnext | Stock | doctype | Warehouse | C | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:warehouse-type` | erpnext | Stock | doctype | Warehouse Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:warranty-claim` | erpnext | Support | doctype | Warranty Claim | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:work-order` | erpnext | Manufacturing | doctype | Work Order | B | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:workstation` | erpnext | Manufacturing | doctype | Workstation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:doctype:workstation-type` | erpnext | Manufacturing | doctype | Workstation Type | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `erpnext:document-action:account:chart-of-accounts` | erpnext | Accounts | document_action | Chart of Accounts | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:account:convert-to-group` | erpnext | Accounts | document_action | Convert to Group | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:account:convert-to-non-group` | erpnext | Accounts | document_action | Convert to Non-Group | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:account:general-ledger` | erpnext | Accounts | document_action | General Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:account:merge-account` | erpnext | Accounts | document_action | Merge Account | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:account:update-account-name-number` | erpnext | Accounts | document_action | Update Account Name / Number | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:accounting-dimension:show-0` | erpnext | Accounts | document_action | Show {0} | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:activity-type:activity-cost-per-employee` | erpnext | Projects | document_action | Activity Cost per Employee | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset-repair:accounting-ledger` | erpnext | Assets | document_action | Accounting Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:adjust-asset-value` | erpnext | Assets | document_action | Adjust Asset Value | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:capitalize-asset` | erpnext | Assets | document_action | Capitalize Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:create-asset-capitalization` | erpnext | Assets | document_action | Create Asset Capitalization | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:create-asset-maintenance` | erpnext | Assets | document_action | Create Asset Maintenance | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:create-asset-repair` | erpnext | Assets | document_action | Create Asset Repair | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:create-asset-value-adjustment` | erpnext | Assets | document_action | Create Asset Value Adjustment | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:create-depreciation-entry` | erpnext | Assets | document_action | Create Depreciation Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:maintain-asset` | erpnext | Assets | document_action | Maintain Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:make-asset-movement` | erpnext | Assets | document_action | Make Asset Movement | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:make-depreciation-entry` | erpnext | Assets | document_action | Make Depreciation Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:make-journal-entry` | erpnext | Assets | document_action | Make Journal Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:make-sales-invoice` | erpnext | Assets | document_action | Make Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:repair-asset` | erpnext | Assets | document_action | Repair Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:restore-asset` | erpnext | Assets | document_action | Restore Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:scrap-asset` | erpnext | Assets | document_action | Scrap Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:sell-asset` | erpnext | Assets | document_action | Sell Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:split-asset` | erpnext | Assets | document_action | Split Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:transfer-asset` | erpnext | Assets | document_action | Transfer Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:asset:view-general-ledger` | erpnext | Assets | document_action | View General Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-account:make-bank-account` | erpnext | Accounts | document_action | Make Bank Account | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-account:unlink-external-integrations` | erpnext | Accounts | document_action | Unlink external integrations | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-clearance:get-payment-entries` | erpnext | Accounts | document_action | Get Payment Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-clearance:update-clearance-date` | erpnext | Accounts | document_action | Update Clearance Date | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-reconciliation-tool:auto-reconcile` | erpnext | Accounts | document_action | Auto Reconcile | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-reconciliation-tool:create-journal-entry-bts` | erpnext | Accounts | document_action | Create Journal Entry Bts | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-reconciliation-tool:create-payment-entry-bts` | erpnext | Accounts | document_action | Create Payment Entry Bts | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-reconciliation-tool:get-unreconciled-entries` | erpnext | Accounts | document_action | Get Unreconciled Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-reconciliation-tool:upload-bank-statement` | erpnext | Accounts | document_action | Upload Bank Statement | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-statement-import:export-errored-rows` | erpnext | Accounts | document_action | Export Errored Rows | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-statement-import:export-import-log` | erpnext | Accounts | document_action | Export Import Log | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-statement-import:go-to-0-list` | erpnext | Accounts | document_action | Go to {0} List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-statement-import:report-error` | erpnext | Accounts | document_action | Report Error | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-transaction:create-bank-entries` | erpnext | Accounts | document_action | Create Bank Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank-transaction:unreconcile-transaction` | erpnext | Accounts | document_action | Unreconcile Transaction | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bank:refresh-plaid-link` | erpnext | Accounts | document_action | Refresh Plaid Link | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:batch:recalculate-batch-qty` | erpnext | Stock | document_action | Recalculate Batch Qty | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:batch:view-ledger` | erpnext | Stock | document_action | View Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bin:recalculate-bin-qty` | erpnext | Stock | document_action | Recalculate Bin Qty | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bisect-accounting-statements:bisect-left` | erpnext | Accounts | document_action | Bisect Left | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bisect-accounting-statements:bisect-right` | erpnext | Accounts | document_action | Bisect Right | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bisect-accounting-statements:build-tree` | erpnext | Accounts | document_action | Build Tree | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bisect-accounting-statements:up` | erpnext | Accounts | document_action | Up | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:blanket-order:make-order` | erpnext | Manufacturing | document_action | Make Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:blanket-order:purchase-order` | erpnext | Manufacturing | document_action | Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:blanket-order:quotation` | erpnext | Manufacturing | document_action | Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:blanket-order:sales-order` | erpnext | Manufacturing | document_action | Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom-creator:create-multi-level-bom` | erpnext | Manufacturing | document_action | Create Multi-level BOM | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom-creator:rebuild-tree` | erpnext | Manufacturing | document_action | Rebuild Tree | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom-update-tool:view-bom-update-log` | erpnext | Manufacturing | document_action | View BOM Update Log | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom:alternate-item` | erpnext | Manufacturing | document_action | Alternate Item | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom:browse-bom` | erpnext | Manufacturing | document_action | Browse BOM | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom:make-variant-bom` | erpnext | Manufacturing | document_action | Make Variant Bom | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom:new-version` | erpnext | Manufacturing | document_action | New Version | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom:quality-inspection` | erpnext | Manufacturing | document_action | Quality Inspection | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom:update-cost` | erpnext | Manufacturing | document_action | Update Cost | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom:variant-bom` | erpnext | Manufacturing | document_action | Variant BOM | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bom:work-order` | erpnext | Manufacturing | document_action | Work Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bulk-transaction-log:failed-entries` | erpnext | Bulk Transaction | document_action | Failed Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bulk-transaction-log:retry-failed-transactions` | erpnext | Bulk Transaction | document_action | Retry Failed Transactions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:bulk-transaction-log:succeeded-entries` | erpnext | Bulk Transaction | document_action | Succeeded Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:campaign:view-leads` | erpnext | CRM | document_action | View Leads | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:cheque-print-template:create-or-update-cheque-print-format` | erpnext | Accounts | document_action | Create Or Update Cheque Print Format | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:closing-stock-balance:generate-closing-stock-balance` | erpnext | Stock | document_action | Generate Closing Stock Balance | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:closing-stock-balance:regenerate-closing-stock-balance` | erpnext | Stock | document_action | Regenerate Closing Stock Balance | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:code-list:import-genericode-file` | erpnext | EDI | document_action | Import Genericode File | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:company:chart-of-accounts` | erpnext | Setup | document_action | Chart of Accounts | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:company:cost-centers` | erpnext | Setup | document_action | Cost Centers | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:company:create-default-tax-template` | erpnext | Setup | document_action | Create Default Tax Template | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:company:create-tax-template` | erpnext | Setup | document_action | Create Tax Template | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:company:create-transaction-deletion-request` | erpnext | Setup | document_action | Create Transaction Deletion Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:company:delete-transactions` | erpnext | Setup | document_action | Delete Transactions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:company:purchase-tax-template` | erpnext | Setup | document_action | Purchase Tax Template | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:company:sales-tax-template` | erpnext | Setup | document_action | Sales Tax Template | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:cost-center:budget` | erpnext | Accounts | document_action | Budget | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:cost-center:chart-of-cost-centers` | erpnext | Accounts | document_action | Chart of Cost Centers | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:cost-center:convert-to-group` | erpnext | Accounts | document_action | Convert to Group | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:cost-center:convert-to-non-group` | erpnext | Accounts | document_action | Convert to Non-Group | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:cost-center:update-cost-center-name-number` | erpnext | Accounts | document_action | Update Cost Center Name / Number | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:coupon-code:add-edit-coupon-conditions` | erpnext | Accounts | document_action | Add/Edit Coupon Conditions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:customer:accounting-ledger` | erpnext | Selling | document_action | Accounting Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:customer:accounts-receivable` | erpnext | Selling | document_action | Accounts Receivable | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:customer:get-customer-group-details` | erpnext | Selling | document_action | Get Customer Group Details | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:customer:link-with-supplier` | erpnext | Selling | document_action | Link with Supplier | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:customer:make-opportunity` | erpnext | Selling | document_action | Make Opportunity | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:customer:make-quotation` | erpnext | Selling | document_action | Make Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:customer:pricing-rule` | erpnext | Selling | document_action | Pricing Rule | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:close` | erpnext | Stock | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:credit-note` | erpnext | Stock | document_action | Credit Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:delivery-trip` | erpnext | Stock | document_action | Delivery Trip | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:installation-note` | erpnext | Stock | document_action | Installation Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:make-delivery-trip` | erpnext | Stock | document_action | Make Delivery Trip | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:make-installation-note` | erpnext | Stock | document_action | Make Installation Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:make-inter-company-purchase-receipt` | erpnext | Stock | document_action | Make Inter Company Purchase Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:make-packing-slip` | erpnext | Stock | document_action | Make Packing Slip | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:make-sales-invoice` | erpnext | Stock | document_action | Make Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:make-sales-return` | erpnext | Stock | document_action | Make Sales Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:make-shipment` | erpnext | Stock | document_action | Make Shipment | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:packing-slip` | erpnext | Stock | document_action | Packing Slip | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:pick-list` | erpnext | Stock | document_action | Pick List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:reopen` | erpnext | Stock | document_action | Reopen | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:sales-invoice` | erpnext | Stock | document_action | Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:sales-order` | erpnext | Stock | document_action | Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:sales-return` | erpnext | Stock | document_action | Sales Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-note:shipment` | erpnext | Stock | document_action | Shipment | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-trip:delivery-note` | erpnext | Stock | document_action | Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-trip:delivery-notes` | erpnext | Stock | document_action | Delivery Notes | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:delivery-trip:notify-customers-via-email` | erpnext | Stock | document_action | Notify Customers via Email | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:dunning:fetch-overdue-payments` | erpnext | Accounts | document_action | Fetch Overdue Payments | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:dunning:payment` | erpnext | Accounts | document_action | Payment | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:dunning:resolve` | erpnext | Accounts | document_action | Resolve | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:email-digest:send-now` | erpnext | Setup | document_action | Send Now | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:email-digest:view-now` | erpnext | Setup | document_action | View Now | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:employee:create-user` | erpnext | Setup | document_action | Create User | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:exchange-rate-revaluation:journal-entries` | erpnext | Accounts | document_action | Journal Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:exchange-rate-revaluation:make-jv-entries` | erpnext | Accounts | document_action | Make Jv Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:homepage:customize-homepage-sections` | erpnext | Portal | document_action | Customize Homepage Sections | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:homepage:set-meta-tags` | erpnext | Portal | document_action | Set Meta Tags | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:installation-note:from-delivery-note` | erpnext | Selling | document_action | From Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:inventory-dimension:delete-dimension` | erpnext | Stock | document_action | Delete Dimension | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:invoice-discounting:accounting-ledger` | erpnext | Accounts | document_action | Accounting Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:invoice-discounting:close-loan` | erpnext | Accounts | document_action | Close Loan | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:invoice-discounting:create-disbursement-entry` | erpnext | Accounts | document_action | Create Disbursement Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:invoice-discounting:disburse-loan` | erpnext | Accounts | document_action | Disburse Loan | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:invoice-discounting:get-invoices` | erpnext | Accounts | document_action | Get Invoices | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:issue:close` | erpnext | Support | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:issue:make-issue-from-communication` | erpnext | Support | document_action | Make Issue From Communication | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:issue:make-task` | erpnext | Support | document_action | Make Task | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:issue:reopen` | erpnext | Support | document_action | Reopen | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:issue:set-status` | erpnext | Support | document_action | Set Status | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:issue:task` | erpnext | Support | document_action | Task | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item-group:item-group-tree` | erpnext | Setup | document_action | Item Group Tree | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item-group:items` | erpnext | Setup | document_action | Items | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:add-edit-prices` | erpnext | Stock | document_action | Add / Edit Prices | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:duplicate` | erpnext | Stock | document_action | Duplicate | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:item-variant-settings` | erpnext | Stock | document_action | Item Variant Settings | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:multiple-variants` | erpnext | Stock | document_action | Multiple Variants | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:show-variants` | erpnext | Stock | document_action | Show Variants | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:single-variant` | erpnext | Stock | document_action | Single Variant | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:stock-balance` | erpnext | Stock | document_action | Stock Balance | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:stock-ledger` | erpnext | Stock | document_action | Stock Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:stock-projected-qty` | erpnext | Stock | document_action | Stock Projected Qty | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:variant` | erpnext | Stock | document_action | Variant | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:item:variant-details-report` | erpnext | Stock | document_action | Variant Details Report | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:complete-job` | erpnext | Manufacturing | document_action | Complete Job | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:corrective-job-card` | erpnext | Manufacturing | document_action | Corrective Job Card | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:make-corrective-job-card` | erpnext | Manufacturing | document_action | Make Corrective Job Card | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:make-material-request` | erpnext | Manufacturing | document_action | Make Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:make-stock-entry` | erpnext | Manufacturing | document_action | Make Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:make-time-log` | erpnext | Manufacturing | document_action | Make Time Log | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:material-request` | erpnext | Manufacturing | document_action | Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:material-transfer` | erpnext | Manufacturing | document_action | Material Transfer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:pause-job` | erpnext | Manufacturing | document_action | Pause Job | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:resume-job` | erpnext | Manufacturing | document_action | Resume Job | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:job-card:start-job` | erpnext | Manufacturing | document_action | Start Job | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:journal-entry:create-inter-company-journal-entry` | erpnext | Accounts | document_action | Create Inter Company Journal Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:journal-entry:get-payment-entry-against-invoice` | erpnext | Accounts | document_action | Get Payment Entry Against Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:journal-entry:get-payment-entry-against-order` | erpnext | Accounts | document_action | Get Payment Entry Against Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:journal-entry:ledger` | erpnext | Accounts | document_action | Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:journal-entry:make-inter-company-journal-entry` | erpnext | Accounts | document_action | Make Inter Company Journal Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:journal-entry:make-reverse-journal-entry` | erpnext | Accounts | document_action | Make Reverse Journal Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:journal-entry:quick-entry` | erpnext | Accounts | document_action | Quick Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:journal-entry:reverse-journal-entry` | erpnext | Accounts | document_action | Reverse Journal Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:add-to-prospect` | erpnext | CRM | document_action | Add to Prospect | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:create-prospect-and-contact` | erpnext | CRM | document_action | Create Prospect And Contact | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:customer` | erpnext | CRM | document_action | Customer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:make-customer` | erpnext | CRM | document_action | Make Customer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:make-lead-from-communication` | erpnext | CRM | document_action | Make Lead From Communication | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:make-opportunity` | erpnext | CRM | document_action | Make Opportunity | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:make-quotation` | erpnext | CRM | document_action | Make Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:opportunity` | erpnext | CRM | document_action | Opportunity | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:prospect` | erpnext | CRM | document_action | Prospect | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:lead:quotation` | erpnext | CRM | document_action | Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:maintenance-schedule:maintenance-visit` | erpnext | Maintenance | document_action | Maintenance Visit | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:maintenance-schedule:make-maintenance-visit` | erpnext | Maintenance | document_action | Make Maintenance Visit | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:maintenance-schedule:sales-order` | erpnext | Maintenance | document_action | Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:maintenance-visit:maintenance-schedule` | erpnext | Maintenance | document_action | Maintenance Schedule | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:maintenance-visit:sales-order` | erpnext | Maintenance | document_action | Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:maintenance-visit:warranty-claim` | erpnext | Maintenance | document_action | Warranty Claim | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:bill-of-materials` | erpnext | Stock | document_action | Bill of Materials | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:create-pick-list` | erpnext | Stock | document_action | Create Pick List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:issue-material` | erpnext | Stock | document_action | Issue Material | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:make-in-transit-stock-entry` | erpnext | Stock | document_action | Make In Transit Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:make-purchase-order` | erpnext | Stock | document_action | Make Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:make-purchase-order-based-on-supplier` | erpnext | Stock | document_action | Make Purchase Order Based On Supplier | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:make-request-for-quotation` | erpnext | Stock | document_action | Make Request For Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:make-stock-entry` | erpnext | Stock | document_action | Make Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:make-supplier-quotation` | erpnext | Stock | document_action | Make Supplier Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:material-receipt` | erpnext | Stock | document_action | Material Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:material-transfer` | erpnext | Stock | document_action | Material Transfer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:material-transfer-in-transit` | erpnext | Stock | document_action | Material Transfer (In Transit) | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:pick-list` | erpnext | Stock | document_action | Pick List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:purchase-order` | erpnext | Stock | document_action | Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:re-open` | erpnext | Stock | document_action | Re-open | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:request-for-quotation` | erpnext | Stock | document_action | Request for Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:sales-order` | erpnext | Stock | document_action | Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:stop` | erpnext | Stock | document_action | Stop | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:subcontracted-purchase-order` | erpnext | Stock | document_action | Subcontracted Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:supplier-quotation` | erpnext | Stock | document_action | Supplier Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:update-status` | erpnext | Stock | document_action | Update Status | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:material-request:work-order` | erpnext | Stock | document_action | Work Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opening-invoice-creation-tool:make-invoices` | erpnext | Accounts | document_action | Make Invoices | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:close` | erpnext | CRM | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:customer` | erpnext | CRM | document_action | Customer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:fetch-latest-exchange-rate` | erpnext | CRM | document_action | Fetch Latest Exchange Rate | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:make-customer` | erpnext | CRM | document_action | Make Customer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:make-opportunity-from-communication` | erpnext | CRM | document_action | Make Opportunity From Communication | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:make-quotation` | erpnext | CRM | document_action | Make Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:make-request-for-quotation` | erpnext | CRM | document_action | Make Request For Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:make-supplier-quotation` | erpnext | CRM | document_action | Make Supplier Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:quotation` | erpnext | CRM | document_action | Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:reopen` | erpnext | CRM | document_action | Reopen | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:request-for-quotation` | erpnext | CRM | document_action | Request For Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:opportunity:supplier-quotation` | erpnext | CRM | document_action | Supplier Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:party-link:create-party-link` | erpnext | Accounts | document_action | Create Party Link | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-entry:get-payment-entry` | erpnext | Accounts | document_action | Get Payment Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-entry:ledger` | erpnext | Accounts | document_action | Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-entry:make-payment-order` | erpnext | Accounts | document_action | Make Payment Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-entry:view-exchange-gain-loss-journals` | erpnext | Accounts | document_action | View Exchange Gain/Loss Journals | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-order:create-journal-entries` | erpnext | Accounts | document_action | Create Journal Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-order:make-payment-records` | erpnext | Accounts | document_action | Make Payment Records | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-order:payment-entry` | erpnext | Accounts | document_action | Payment Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-order:payment-request` | erpnext | Accounts | document_action | Payment Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-reconciliation:allocate` | erpnext | Accounts | document_action | Allocate | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-reconciliation:get-unreconciled-entries` | erpnext | Accounts | document_action | Get Unreconciled Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-reconciliation:reconcile` | erpnext | Accounts | document_action | Reconcile | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-request:create-payment-entry` | erpnext | Accounts | document_action | Create Payment Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-request:make-payment-entry` | erpnext | Accounts | document_action | Make Payment Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-request:make-payment-order` | erpnext | Accounts | document_action | Make Payment Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-request:make-payment-request` | erpnext | Accounts | document_action | Make Payment Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:payment-request:resend-payment-email` | erpnext | Accounts | document_action | Resend Payment Email | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:period-closing-voucher:ledger` | erpnext | Accounts | document_action | Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:cancel-stock-reservation-entries` | erpnext | Stock | document_action | Cancel Stock Reservation Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:create-delivery-note` | erpnext | Stock | document_action | Create Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:create-dn-for-pick-lists` | erpnext | Stock | document_action | Create Dn For Pick Lists | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:create-stock-entry` | erpnext | Stock | document_action | Create Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:create-stock-reservation-entries` | erpnext | Stock | document_action | Create Stock Reservation Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:get-items` | erpnext | Stock | document_action | Get Items | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:reserve` | erpnext | Stock | document_action | Reserve | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:reserved-stock` | erpnext | Stock | document_action | Reserved Stock | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:unreserve` | erpnext | Stock | document_action | Unreserve | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pick-list:update-current-stock` | erpnext | Stock | document_action | Update Current Stock | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:plaid-settings:link-a-new-bank-account` | erpnext | ERPNext Integrations | document_action | Link a new bank account | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:plaid-settings:reset-plaid-link` | erpnext | ERPNext Integrations | document_action | Reset Plaid Link | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:plaid-settings:sync-now` | erpnext | ERPNext Integrations | document_action | Sync Now | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:plant-floor:create-workstation` | erpnext | Manufacturing | document_action | Create Workstation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:plant-floor:make-stock-entry` | erpnext | Manufacturing | document_action | Make Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pos-closing-entry:retry` | erpnext | Accounts | document_action | Retry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pos-invoice:create-payment-request` | erpnext | Accounts | document_action | Create Payment Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pos-invoice:make-merge-log` | erpnext | Accounts | document_action | Make Merge Log | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pos-invoice:make-sales-return` | erpnext | Accounts | document_action | Make Sales Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pos-invoice:return` | erpnext | Accounts | document_action | Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:price-list:add-edit-prices` | erpnext | Stock | document_action | Add / Edit Prices | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:pricing-rule:make-pricing-rule` | erpnext | Accounts | document_action | Make Pricing Rule | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:process-period-closing-voucher:cancel-pcv-processing` | erpnext | Accounts | document_action | Cancel Pcv Processing | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:process-statement-of-accounts:download` | erpnext | Accounts | document_action | Download | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:process-statement-of-accounts:send-emails` | erpnext | Accounts | document_action | Send Emails | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:production-plan:close` | erpnext | Manufacturing | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:production-plan:make-material-request` | erpnext | Manufacturing | document_action | Make Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:production-plan:make-work-order` | erpnext | Manufacturing | document_action | Make Work Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:production-plan:material-request` | erpnext | Manufacturing | document_action | Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:production-plan:production-plan-summary` | erpnext | Manufacturing | document_action | Production Plan Summary | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:production-plan:re-open` | erpnext | Manufacturing | document_action | Re-open | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:production-plan:set-status` | erpnext | Manufacturing | document_action | Set Status | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:production-plan:work-order-subcontract-po` | erpnext | Manufacturing | document_action | Work Order / Subcontract PO | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:project:create-duplicate-project` | erpnext | Projects | document_action | Create Duplicate Project | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:project:create-kanban-board-if-not-exists` | erpnext | Projects | document_action | Create Kanban Board If Not Exists | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:project:duplicate-project-with-tasks` | erpnext | Projects | document_action | Duplicate Project with Tasks | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:project:gantt-chart` | erpnext | Projects | document_action | Gantt Chart | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:project:kanban-board` | erpnext | Projects | document_action | Kanban Board | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:project:set-project-status` | erpnext | Projects | document_action | Set Project Status | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:project:update-costing-and-billing` | erpnext | Projects | document_action | Update Costing and Billing | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:prospect:customer` | erpnext | CRM | document_action | Customer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:prospect:make-customer` | erpnext | CRM | document_action | Make Customer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:prospect:make-opportunity` | erpnext | CRM | document_action | Make Opportunity | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:prospect:opportunity` | erpnext | CRM | document_action | Opportunity | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:block-invoice` | erpnext | Accounts | document_action | Block Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:change-release-date` | erpnext | Accounts | document_action | Change Release Date | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:inter-company-invoice` | erpnext | Accounts | document_action | Inter Company Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:landed-cost-voucher` | erpnext | Accounts | document_action | Landed Cost Voucher | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:make-debit-note` | erpnext | Accounts | document_action | Make Debit Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:make-inter-company-sales-invoice` | erpnext | Accounts | document_action | Make Inter Company Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:make-purchase-receipt` | erpnext | Accounts | document_action | Make Purchase Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:make-stock-entry` | erpnext | Accounts | document_action | Make Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:payment` | erpnext | Accounts | document_action | Payment | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:payment-request` | erpnext | Accounts | document_action | Payment Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:purchase-order` | erpnext | Accounts | document_action | Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:purchase-receipt` | erpnext | Accounts | document_action | Purchase Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:return-debit-note` | erpnext | Accounts | document_action | Return / Debit Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-invoice:unblock-invoice` | erpnext | Accounts | document_action | Unblock Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:close` | erpnext | Buying | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:delivered` | erpnext | Buying | document_action | Delivered | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:hold` | erpnext | Buying | document_action | Hold | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:link-to-material-request` | erpnext | Buying | document_action | Link to Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:make-inter-company-sales-order` | erpnext | Buying | document_action | Make Inter Company Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:make-purchase-invoice` | erpnext | Buying | document_action | Make Purchase Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:make-purchase-invoice-from-portal` | erpnext | Buying | document_action | Make Purchase Invoice From Portal | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:make-purchase-receipt` | erpnext | Buying | document_action | Make Purchase Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:make-subcontracting-order` | erpnext | Buying | document_action | Make Subcontracting Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:material-request` | erpnext | Buying | document_action | Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:material-to-supplier` | erpnext | Buying | document_action | Material to Supplier | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:payment` | erpnext | Buying | document_action | Payment | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:payment-request` | erpnext | Buying | document_action | Payment Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:purchase-invoice` | erpnext | Buying | document_action | Purchase Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:purchase-receipt` | erpnext | Buying | document_action | Purchase Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:re-open` | erpnext | Buying | document_action | Re-open | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:resume` | erpnext | Buying | document_action | Resume | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:return-of-components` | erpnext | Buying | document_action | Return of Components | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:subcontracting-order` | erpnext | Buying | document_action | Subcontracting Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:supplier-quotation` | erpnext | Buying | document_action | Supplier Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:update-items` | erpnext | Buying | document_action | Update Items | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:update-rate-as-per-last-purchase` | erpnext | Buying | document_action | Update Rate as per Last Purchase | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-order:update-status` | erpnext | Buying | document_action | Update Status | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:asset` | erpnext | Stock | document_action | Asset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:asset-movement` | erpnext | Stock | document_action | Asset Movement | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:close` | erpnext | Stock | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:debit-note` | erpnext | Stock | document_action | Debit Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:delivery-note` | erpnext | Stock | document_action | Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:landed-cost-voucher` | erpnext | Stock | document_action | Landed Cost Voucher | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:make-inter-company-delivery-note` | erpnext | Stock | document_action | Make Inter Company Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:make-lcv` | erpnext | Stock | document_action | Make Lcv | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:make-purchase-invoice` | erpnext | Stock | document_action | Make Purchase Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:make-purchase-return` | erpnext | Stock | document_action | Make Purchase Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:make-purchase-return-against-rejected-warehouse` | erpnext | Stock | document_action | Make Purchase Return Against Rejected Warehouse | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:make-stock-entry` | erpnext | Stock | document_action | Make Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:purchase-invoice` | erpnext | Stock | document_action | Purchase Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:purchase-order` | erpnext | Stock | document_action | Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:purchase-return` | erpnext | Stock | document_action | Purchase Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:reopen` | erpnext | Stock | document_action | Reopen | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:purchase-receipt:retention-stock-entry` | erpnext | Stock | document_action | Retention Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:quality-inspection:make-quality-inspection` | erpnext | Stock | document_action | Make Quality Inspection | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:quick-stock-balance:stock-balance-report` | erpnext | Stock | document_action | Stock Balance Report | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:quotation:make-sales-invoice` | erpnext | Selling | document_action | Make Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:quotation:make-sales-order` | erpnext | Selling | document_action | Make Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:quotation:opportunity` | erpnext | Selling | document_action | Opportunity | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:quotation:sales-order` | erpnext | Selling | document_action | Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:quotation:set-as-lost` | erpnext | Selling | document_action | Set as Lost | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:quotation:update-items` | erpnext | Selling | document_action | Update Items | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:repost-accounting-ledger:show-preview` | erpnext | Accounts | document_action | Show Preview | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:repost-item-valuation:restart` | erpnext | Stock | document_action | Restart | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:repost-item-valuation:start-reposting` | erpnext | Stock | document_action | Start Reposting | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:create-supplier-quotation` | erpnext | Buying | document_action | Create Supplier Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:download-pdf` | erpnext | Buying | document_action | Download PDF | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:get-suppliers` | erpnext | Buying | document_action | Get Suppliers | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:link-to-material-requests` | erpnext | Buying | document_action | Link to Material Requests | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:make-supplier-quotation-from-rfq` | erpnext | Buying | document_action | Make Supplier Quotation From Rfq | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:material-request` | erpnext | Buying | document_action | Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:opportunity` | erpnext | Buying | document_action | Opportunity | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:possible-supplier` | erpnext | Buying | document_action | Possible Supplier | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:send-emails-to-suppliers` | erpnext | Buying | document_action | Send Emails to Suppliers | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:supplier-quotation` | erpnext | Buying | document_action | Supplier Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:request-for-quotation:supplier-quotation-comparison` | erpnext | Buying | document_action | Supplier Quotation Comparison | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:create-dunning` | erpnext | Accounts | document_action | Create Dunning | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:create-invoice-discounting` | erpnext | Accounts | document_action | Create Invoice Discounting | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:delivery-note` | erpnext | Accounts | document_action | Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:dunning` | erpnext | Accounts | document_action | Dunning | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:generate-e-invoice` | erpnext | Accounts | document_action | Generate E-Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:invoice-discounting` | erpnext | Accounts | document_action | Invoice Discounting | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:maintenance-schedule` | erpnext | Accounts | document_action | Maintenance Schedule | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:make-delivery-note` | erpnext | Accounts | document_action | Make Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:make-inter-company-purchase-invoice` | erpnext | Accounts | document_action | Make Inter Company Purchase Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:make-maintenance-schedule` | erpnext | Accounts | document_action | Make Maintenance Schedule | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:make-sales-return` | erpnext | Accounts | document_action | Make Sales Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:payment` | erpnext | Accounts | document_action | Payment | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:payment-request` | erpnext | Accounts | document_action | Payment Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:quotation` | erpnext | Accounts | document_action | Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:return-credit-note` | erpnext | Accounts | document_action | Return / Credit Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:sales-order` | erpnext | Accounts | document_action | Sales Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-invoice:timesheet` | erpnext | Accounts | document_action | Timesheet | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:cancel-stock-reservation-entries` | erpnext | Selling | document_action | Cancel Stock Reservation Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:close` | erpnext | Selling | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:create-pick-list` | erpnext | Selling | document_action | Create Pick List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:create-stock-reservation-entries` | erpnext | Selling | document_action | Create Stock Reservation Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:delivery-note` | erpnext | Selling | document_action | Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:hold` | erpnext | Selling | document_action | Hold | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:maintenance-schedule` | erpnext | Selling | document_action | Maintenance Schedule | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:maintenance-visit` | erpnext | Selling | document_action | Maintenance Visit | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-delivery-note` | erpnext | Selling | document_action | Make Delivery Note | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-inter-company-purchase-order` | erpnext | Selling | document_action | Make Inter Company Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-maintenance-schedule` | erpnext | Selling | document_action | Make Maintenance Schedule | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-maintenance-visit` | erpnext | Selling | document_action | Make Maintenance Visit | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-material-request` | erpnext | Selling | document_action | Make Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-project` | erpnext | Selling | document_action | Make Project | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-purchase-order` | erpnext | Selling | document_action | Make Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-purchase-order-for-default-supplier` | erpnext | Selling | document_action | Make Purchase Order For Default Supplier | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-raw-material-request` | erpnext | Selling | document_action | Make Raw Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-sales-invoice` | erpnext | Selling | document_action | Make Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:make-work-orders` | erpnext | Selling | document_action | Make Work Orders | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:material-request` | erpnext | Selling | document_action | Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:payment` | erpnext | Selling | document_action | Payment | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:payment-request` | erpnext | Selling | document_action | Payment Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:pick-list` | erpnext | Selling | document_action | Pick List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:project` | erpnext | Selling | document_action | Project | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:purchase-order` | erpnext | Selling | document_action | Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:quotation` | erpnext | Selling | document_action | Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:re-open` | erpnext | Selling | document_action | Re-open | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:request-for-raw-materials` | erpnext | Selling | document_action | Request for Raw Materials | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:reserve` | erpnext | Selling | document_action | Reserve | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:reserved-stock` | erpnext | Selling | document_action | Reserved Stock | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:resume` | erpnext | Selling | document_action | Resume | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:sales-invoice` | erpnext | Selling | document_action | Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:unreserve` | erpnext | Selling | document_action | Unreserve | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:update-items` | erpnext | Selling | document_action | Update Items | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:update-status` | erpnext | Selling | document_action | Update Status | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sales-order:work-order` | erpnext | Selling | document_action | Work Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:serial-and-batch-bundle:create-serial-nos` | erpnext | Stock | document_action | Create Serial Nos | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:serial-and-batch-bundle:make-0` | erpnext | Stock | document_action | Make {0} | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:serial-no:view-ledgers` | erpnext | Stock | document_action | View Ledgers | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:share-transfer:create-journal-entry` | erpnext | Accounts | document_action | Create Journal Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:share-transfer:make-jv-entry` | erpnext | Accounts | document_action | Make Jv Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:shareholder:share-balance` | erpnext | Accounts | document_action | Share Balance | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:shareholder:share-ledger` | erpnext | Accounts | document_action | Share Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:sms-center:create-receiver-list` | erpnext | Selling | document_action | Create Receiver List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:alternate-item` | erpnext | Stock | document_action | Alternate Item | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:bill-of-materials` | erpnext | Stock | document_action | Bill of Materials | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:create-sample-retention-stock-entry` | erpnext | Stock | document_action | Create Sample Retention Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:disassemble` | erpnext | Stock | document_action | Disassemble | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:end-transit` | erpnext | Stock | document_action | End Transit | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:excise-invoice` | erpnext | Stock | document_action | Excise Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:expired-batches` | erpnext | Stock | document_action | Expired Batches | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:make-stock-entry` | erpnext | Stock | document_action | Make Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:make-stock-in-entry` | erpnext | Stock | document_action | Make Stock In Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:material-request` | erpnext | Stock | document_action | Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:purchase-invoice` | erpnext | Stock | document_action | Purchase Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:quality-inspection-s` | erpnext | Stock | document_action | Quality Inspection(s) | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:received-stock-entries` | erpnext | Stock | document_action | Received Stock Entries | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-entry:transit-entry` | erpnext | Stock | document_action | Transit Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-reconciliation:fetch-items-from-warehouse` | erpnext | Stock | document_action | Fetch Items from Warehouse | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:stock-reposting-settings:convert-to-item-based-reposting` | erpnext | Stock | document_action | Convert to Item Based Reposting | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-order:close` | erpnext | Subcontracting | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-order:make-subcontracting-receipt` | erpnext | Subcontracting | document_action | Make Subcontracting Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-order:material-to-supplier` | erpnext | Subcontracting | document_action | Material to Supplier | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-order:re-open` | erpnext | Subcontracting | document_action | Re-open | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-order:return-of-components` | erpnext | Subcontracting | document_action | Return of Components | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-order:subcontracting-receipt` | erpnext | Subcontracting | document_action | Subcontracting Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-receipt:accounting-ledger` | erpnext | Subcontracting | document_action | Accounting Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-receipt:make-purchase-receipt` | erpnext | Subcontracting | document_action | Make Purchase Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-receipt:make-subcontract-return` | erpnext | Subcontracting | document_action | Make Subcontract Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-receipt:make-subcontract-return-against-rejected-warehouse` | erpnext | Subcontracting | document_action | Make Subcontract Return Against Rejected Warehouse | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-receipt:purchase-receipt` | erpnext | Subcontracting | document_action | Purchase Receipt | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-receipt:stock-ledger` | erpnext | Subcontracting | document_action | Stock Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-receipt:subcontract-return` | erpnext | Subcontracting | document_action | Subcontract Return | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subcontracting-receipt:subcontracting-order` | erpnext | Subcontracting | document_action | Subcontracting Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subscription:cancel-subscription` | erpnext | Accounts | document_action | Cancel Subscription | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subscription:fetch-subscription-updates` | erpnext | Accounts | document_action | Fetch Subscription Updates | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subscription:force-fetch-subscription-updates` | erpnext | Accounts | document_action | Force-Fetch Subscription Updates | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:subscription:restart-subscription` | erpnext | Accounts | document_action | Restart Subscription | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:link-to-material-requests` | erpnext | Buying | document_action | Link to Material Requests | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:make-purchase-invoice` | erpnext | Buying | document_action | Make Purchase Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:make-purchase-order` | erpnext | Buying | document_action | Make Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:make-quotation` | erpnext | Buying | document_action | Make Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:material-request` | erpnext | Buying | document_action | Material Request | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:purchase-order` | erpnext | Buying | document_action | Purchase Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:quotation` | erpnext | Buying | document_action | Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:request-for-quotation` | erpnext | Buying | document_action | Request for Quotation | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-quotation:update-items` | erpnext | Buying | document_action | Update Items | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier-scorecard:make-all-scorecards` | erpnext | Buying | document_action | Make All Scorecards | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier:accounting-ledger` | erpnext | Buying | document_action | Accounting Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier:accounts-payable` | erpnext | Buying | document_action | Accounts Payable | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier:bank-account` | erpnext | Buying | document_action | Bank Account | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier:get-supplier-group-details` | erpnext | Buying | document_action | Get Supplier Group Details | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier:link-with-customer` | erpnext | Buying | document_action | Link with Customer | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:supplier:pricing-rule` | erpnext | Buying | document_action | Pricing Rule | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:task:make-timesheet` | erpnext | Projects | document_action | Make Timesheet | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:timesheet:create-sales-invoice` | erpnext | Projects | document_action | Create Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:timesheet:make-sales-invoice` | erpnext | Projects | document_action | Make Sales Invoice | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:unreconcile-payment:create-unreconcile-doc-for-selection` | erpnext | Accounts | document_action | Create Unreconcile Doc For Selection | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:video:watch-video` | erpnext | Utilities | document_action | Watch Video | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:warehouse:general-ledger` | erpnext | Stock | document_action | General Ledger | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:warehouse:stock-balance` | erpnext | Stock | document_action | Stock Balance | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:warranty-claim:maintenance-visit` | erpnext | Support | document_action | Maintenance Visit | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:warranty-claim:make-maintenance-visit` | erpnext | Support | document_action | Make Maintenance Visit | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:alternate-item` | erpnext | Manufacturing | document_action | Alternate Item | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:bom` | erpnext | Manufacturing | document_action | BOM | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:close` | erpnext | Manufacturing | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:create-job-card` | erpnext | Manufacturing | document_action | Create Job Card | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:create-pick-list` | erpnext | Manufacturing | document_action | Create Pick List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:disassemble-order` | erpnext | Manufacturing | document_action | Disassemble Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:finish` | erpnext | Manufacturing | document_action | Finish | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:make-bom` | erpnext | Manufacturing | document_action | Make Bom | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:make-job-card` | erpnext | Manufacturing | document_action | Make Job Card | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:make-stock-entry` | erpnext | Manufacturing | document_action | Make Stock Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:make-stock-return-entry` | erpnext | Manufacturing | document_action | Make Stock Return Entry | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:make-work-order` | erpnext | Manufacturing | document_action | Make Work Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:material-consumption` | erpnext | Manufacturing | document_action | Material Consumption | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:re-open` | erpnext | Manufacturing | document_action | Re-open | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:return-components` | erpnext | Manufacturing | document_action | Return Components | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:start` | erpnext | Manufacturing | document_action | Start | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:document-action:work-order:stop` | erpnext | Manufacturing | document_action | Stop | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `erpnext:installed-app:erpnext` | erpnext | erpnext | installed_app | erpnext | E | Yes | — | Not implemented | Installed app capabilities require classified Retail ERP routes or safe embedding |
| `erpnext:notification:fiscal-year:notification-for-new-fiscal-year` | erpnext | Accounts | notification | Notification for new fiscal year | E | Yes | — | Not implemented | Notification configuration and document event behavior require parity |
| `erpnext:notification:material-request:material-request-receipt-notification` | erpnext | Manufacturing | notification | Material Request Receipt Notification | E | Yes | — | Not implemented | Notification configuration and document event behavior require parity |
| `erpnext:number-card:active-customers` | erpnext | Selling | number_card | Active Customers | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:active-subcontracted-items` | erpnext | Subcontracting | number_card | Active Subcontracted Items | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:active-suppliers` | erpnext | Buying | number_card | Active Suppliers | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:annual-purchase` | erpnext | Buying | number_card | Annual Purchase | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:annual-sales` | erpnext | Selling | number_card | Annual Sales | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:asset-value` | erpnext | Assets | number_card | Asset Value | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:average-order-values` | erpnext | Buying | number_card | Average Order Values | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:average-sales-order-value` | erpnext | Selling | number_card | Average Sales Order Value | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:manufactured-items-value` | erpnext | Manufacturing | number_card | Manufactured Items Value | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:monthly-completed-work-order` | erpnext | Manufacturing | number_card | Monthly Completed Work Order | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:monthly-quality-inspection` | erpnext | Manufacturing | number_card | Monthly Quality Inspection | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:monthly-total-work-order` | erpnext | Manufacturing | number_card | Monthly Total Work Order | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:new-assets-this-year` | erpnext | Assets | number_card | New Assets (This Year) | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:new-lead-last-1-month` | erpnext | CRM | number_card | New Lead (Last 1 Month) | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:new-opportunity-last-1-month` | erpnext | CRM | number_card | New Opportunity (Last 1 Month) | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:non-completed-tasks` | erpnext | Projects | number_card | Non Completed Tasks | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:ongoing-job-card` | erpnext | Manufacturing | number_card | Ongoing Job Card | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:open-opportunity` | erpnext | CRM | number_card | Open Opportunity | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:open-projects` | erpnext | Projects | number_card | Open Projects | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:open-work-orders` | erpnext | Manufacturing | number_card | Open Work Orders | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:purchase-orders-count` | erpnext | Buying | number_card | Purchase Orders Count | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:purchase-orders-to-bill` | erpnext | Buying | number_card | Purchase Orders to Bill | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:purchase-orders-to-receive` | erpnext | Buying | number_card | Purchase Orders to Receive | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:sales-orders-count` | erpnext | Selling | number_card | Sales Orders Count | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:sales-orders-to-bill` | erpnext | Selling | number_card | Sales Orders to Bill | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:sales-orders-to-deliver` | erpnext | Selling | number_card | Sales Orders to Deliver | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:subcontracting-inward-order-count` | erpnext | Subcontracting | number_card | Subcontracting Inward Order Count | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:subcontracting-outward-order-count` | erpnext | Subcontracting | number_card | Subcontracting Outward Order Count | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:timesheet-working-hours` | erpnext | Projects | number_card | Timesheet Working Hours | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-active-items` | erpnext | Stock | number_card | Total Active Items | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-assets` | erpnext | Assets | number_card | Total Assets | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-incoming-bills` | erpnext | Accounts | number_card | Total Incoming Bills | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-incoming-payment` | erpnext | Accounts | number_card | Total Incoming Payment | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-outgoing-bills` | erpnext | Accounts | number_card | Total Outgoing Bills | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-outgoing-payment` | erpnext | Accounts | number_card | Total Outgoing Payment | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-purchase-amount` | erpnext | Buying | number_card | Total Purchase Amount | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-sales-amount` | erpnext | Selling | number_card | Total Sales Amount | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-stock-value` | erpnext | Stock | number_card | Total Stock Value | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:total-warehouses` | erpnext | Stock | number_card | Total Warehouses | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:wip-work-orders` | erpnext | Manufacturing | number_card | WIP Work Orders | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:number-card:won-opportunity-last-1-month` | erpnext | CRM | number_card | Won Opportunity (Last 1 Month) | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `erpnext:page:bom-comparison-tool` | erpnext | Manufacturing | page | bom-comparison-tool | C | Yes | — | Not implemented | Required or safe integration route must be designed |
| `erpnext:page:point-of-sale` | erpnext | Selling | page | point-of-sale | C | Yes | — | Not implemented | Required or safe integration route must be designed |
| `erpnext:page:sales-funnel` | erpnext | Selling | page | sales-funnel | C | Yes | — | Not implemented | Required or safe integration route must be designed |
| `erpnext:page:stock-balance` | erpnext | Stock | page | stock-balance | C | Yes | — | Not implemented | Required or safe integration route must be designed |
| `erpnext:page:visual-plant-floor` | erpnext | Manufacturing | page | visual-plant-floor | C | Yes | — | Not implemented | Required or safe integration route must be designed |
| `erpnext:page:warehouse-capacity-summary` | erpnext | Stock | page | warehouse-capacity-summary | C | Yes | — | Not implemented | Required or safe integration route must be designed |
| `erpnext:print-format:accounts-payable-standard` | erpnext | Accounts | print_format | Accounts Payable Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:accounts-payable-summary-standard` | erpnext | Accounts | print_format | Accounts Payable Summary Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:accounts-receivable-standard` | erpnext | Accounts | print_format | Accounts Receivable Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:accounts-receivable-summary-standard` | erpnext | Accounts | print_format | Accounts Receivable Summary Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:balance-sheet-standard` | erpnext | Accounts | print_format | Balance Sheet Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:cash-flow-statement-standard` | erpnext | Accounts | print_format | Cash Flow Statement Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:delivery-note:delivery-note-standard` | erpnext | Stock | print_format | Delivery Note Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:delivery-note:delivery-note-with-item-image` | erpnext | Stock | print_format | Delivery Note with Item Image | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:dunning:dunning-letter` | erpnext | Accounts | print_format | Dunning Letter | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:general-ledger-standard` | erpnext | Accounts | print_format | General Ledger Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:journal-entry:credit-note` | erpnext | Accounts | print_format | Credit Note | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:journal-entry:journal-auditing-voucher` | erpnext | Accounts | print_format | Journal Auditing Voucher | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:p-l-statement-standard` | erpnext | Accounts | print_format | P&L Statement Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:payment-entry:bank-and-cash-payment-voucher` | erpnext | Accounts | print_format | Bank and Cash Payment Voucher | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:pick-list:pick-list` | erpnext | Stock | print_format | Pick List | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:pos-invoice:pos-invoice` | erpnext | Selling | print_format | POS Invoice | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:pos-invoice:pos-invoice-standard` | erpnext | Accounts | print_format | POS Invoice Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:pos-invoice:pos-invoice-with-item-image` | erpnext | Accounts | print_format | POS Invoice with Item Image | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:pos-invoice:return-pos-invoice` | erpnext | Selling | print_format | Return POS Invoice | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:purchase-invoice:purchase-auditing-voucher` | erpnext | Accounts | print_format | Purchase Auditing Voucher | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:purchase-invoice:purchase-einvoice` | erpnext | Regional | print_format | Purchase eInvoice | E | No | — | Not implemented | None while disabled |
| `erpnext:print-format:purchase-invoice:purchase-invoice-standard` | erpnext | Accounts | print_format | Purchase Invoice Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:purchase-invoice:purchase-invoice-with-item-image` | erpnext | Accounts | print_format | Purchase Invoice with Item Image | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:purchase-order:purchase-order-standard` | erpnext | Buying | print_format | Purchase Order Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:purchase-order:purchase-order-with-item-image` | erpnext | Buying | print_format | Purchase Order with Item Image | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:purchase-receipt:purchase-receipt-serial-and-batch-bundle-print` | erpnext | Stock | print_format | Purchase Receipt Serial and Batch Bundle Print | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:quotation:quotation-standard` | erpnext | Selling | print_format | Quotation Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:quotation:quotation-with-item-image` | erpnext | Selling | print_format | Quotation with Item Image | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:request-for-quotation:request-for-quotation-with-item-image` | erpnext | Buying | print_format | Request for Quotation with Item Image | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:sales-invoice:detailed-tax-invoice` | erpnext | Regional | print_format | Detailed Tax Invoice | E | No | — | Not implemented | None while disabled |
| `erpnext:print-format:sales-invoice:sales-auditing-voucher` | erpnext | Accounts | print_format | Sales Auditing Voucher | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:sales-invoice:sales-invoice-print` | erpnext | Accounts | print_format | Sales Invoice Print | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:sales-invoice:sales-invoice-return` | erpnext | Accounts | print_format | Sales Invoice Return | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:sales-invoice:sales-invoice-standard` | erpnext | Accounts | print_format | Sales Invoice Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:sales-invoice:sales-invoice-with-item-image` | erpnext | Accounts | print_format | Sales Invoice with Item Image | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:sales-invoice:simplified-tax-invoice` | erpnext | Regional | print_format | Simplified Tax Invoice | E | No | — | Not implemented | None while disabled |
| `erpnext:print-format:sales-invoice:tax-invoice` | erpnext | Regional | print_format | Tax Invoice | E | No | — | Not implemented | None while disabled |
| `erpnext:print-format:sales-order:sales-order-standard` | erpnext | Selling | print_format | Sales Order Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:sales-order:sales-order-with-item-image` | erpnext | Selling | print_format | Sales Order with Item Image | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:supplier:irs-1099-form` | erpnext | Regional | print_format | IRS 1099 Form | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:print-format:trial-balance-standard` | erpnext | Accounts | print_format | Trial Balance Standard | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
| `erpnext:report:account-balance` | erpnext | Accounts | report | Account Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:accounts-payable` | erpnext | Accounts | report | Accounts Payable | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:accounts-payable-summary` | erpnext | Accounts | report | Accounts Payable Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:accounts-receivable` | erpnext | Accounts | report | Accounts Receivable | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:accounts-receivable-summary` | erpnext | Accounts | report | Accounts Receivable Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:address-and-contacts` | erpnext | Selling | report | Address And Contacts | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:asset-activity` | erpnext | Assets | report | Asset Activity | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:asset-depreciation-ledger` | erpnext | Accounts | report | Asset Depreciation Ledger | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:asset-depreciations-and-balances` | erpnext | Accounts | report | Asset Depreciations and Balances | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:asset-maintenance` | erpnext | Assets | report | Asset Maintenance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:available-batch-report` | erpnext | Stock | report | Available Batch Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:available-serial-no` | erpnext | Stock | report | Available Serial No | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:available-stock-for-packing-items` | erpnext | Selling | report | Available Stock for Packing Items | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:balance-sheet` | erpnext | Accounts | report | Balance Sheet | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bank-clearance-summary` | erpnext | Accounts | report | Bank Clearance Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bank-reconciliation-statement` | erpnext | Accounts | report | Bank Reconciliation Statement | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:batch-item-expiry-status` | erpnext | Stock | report | Batch Item Expiry Status | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:batch-wise-balance-history` | erpnext | Stock | report | Batch-Wise Balance History | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:billed-items-to-be-received` | erpnext | Accounts | report | Billed Items To Be Received | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bom-explorer` | erpnext | Manufacturing | report | BOM Explorer | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bom-operations-time` | erpnext | Manufacturing | report | BOM Operations Time | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bom-search` | erpnext | Stock | report | BOM Search | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bom-stock-analysis` | erpnext | Manufacturing | report | BOM Stock Analysis | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bom-stock-calculated` | erpnext | Manufacturing | report | BOM Stock Calculated | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bom-stock-report` | erpnext | Manufacturing | report | BOM Stock Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:bom-variance-report` | erpnext | Manufacturing | report | BOM Variance Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:budget-variance-report` | erpnext | Accounts | report | Budget Variance Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:calculated-discount-mismatch` | erpnext | Accounts | report | Calculated Discount Mismatch | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:campaign-efficiency` | erpnext | CRM | report | Campaign Efficiency | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:cash-flow` | erpnext | Accounts | report | Cash Flow | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:cheques-and-deposits-incorrectly-cleared` | erpnext | Accounts | report | Cheques and Deposits Incorrectly cleared | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:cogs-by-item-group` | erpnext | Stock | report | COGS By Item Group | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:completed-work-orders` | erpnext | Manufacturing | report | Completed Work Orders | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:consolidated-financial-statement` | erpnext | Accounts | report | Consolidated Financial Statement | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:consolidated-trial-balance` | erpnext | Accounts | report | Consolidated Trial Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:cost-of-poor-quality-report` | erpnext | Manufacturing | report | Cost of Poor Quality Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:custom-financial-statement` | erpnext | Accounts | report | Custom Financial Statement | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:customer-acquisition-and-loyalty` | erpnext | Selling | report | Customer Acquisition and Loyalty | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:customer-credit-balance` | erpnext | Selling | report | Customer Credit Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:customer-ledger-summary` | erpnext | Accounts | report | Customer Ledger Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:customer-wise-item-price` | erpnext | Selling | report | Customer-wise Item Price | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:customers-without-any-sales-transactions` | erpnext | Selling | report | Customers Without Any Sales Transactions | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:daily-timesheet-summary` | erpnext | Projects | report | Daily Timesheet Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:deferred-revenue-and-expense` | erpnext | Accounts | report | Deferred Revenue and Expense | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:delayed-item-report` | erpnext | Stock | report | Delayed Item Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:delayed-order-report` | erpnext | Stock | report | Delayed Order Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:delayed-tasks-summary` | erpnext | Projects | report | Delayed Tasks Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:delivered-items-to-be-billed` | erpnext | Accounts | report | Delivered Items To Be Billed | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:delivery-note-trends` | erpnext | Stock | report | Delivery Note Trends | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:dimension-wise-accounts-balance-report` | erpnext | Accounts | report | Dimension-wise Accounts Balance Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:downtime-analysis` | erpnext | Manufacturing | report | Downtime Analysis | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:electronic-invoice-register` | erpnext | Regional | report | Electronic Invoice Register | D | No | — | Not implemented | None while disabled |
| `erpnext:report:employee-billing-summary` | erpnext | Projects | report | Employee Billing Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:exponential-smoothing-forecasting` | erpnext | Manufacturing | report | Exponential Smoothing Forecasting | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:fifo-queue-vs-qty-after-transaction-comparison` | erpnext | Stock | report | FIFO Queue vs Qty After Transaction Comparison | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:financial-ratios` | erpnext | Accounts | report | Financial Ratios | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:first-response-time-for-issues` | erpnext | Support | report | First Response Time for Issues | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:first-response-time-for-opportunity` | erpnext | CRM | report | First Response Time for Opportunity | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:fixed-asset-register` | erpnext | Assets | report | Fixed Asset Register | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:general-and-payment-ledger-comparison` | erpnext | Accounts | report | General and Payment Ledger Comparison | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:general-ledger` | erpnext | Accounts | report | General Ledger | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:gross-and-net-profit-report` | erpnext | Accounts | report | Gross and Net Profit Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:gross-profit` | erpnext | Accounts | report | Gross Profit | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:inactive-customers` | erpnext | Selling | report | Inactive Customers | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:inactive-sales-items` | erpnext | Accounts | report | Inactive Sales Items | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:incorrect-balance-qty-after-transaction` | erpnext | Stock | report | Incorrect Balance Qty After Transaction | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:incorrect-serial-and-batch-bundle` | erpnext | Stock | report | Incorrect Serial and Batch Bundle | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:incorrect-serial-no-valuation` | erpnext | Stock | report | Incorrect Serial No Valuation | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:incorrect-stock-value-report` | erpnext | Stock | report | Incorrect Stock Value Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:invalid-ledger-entries` | erpnext | Accounts | report | Invalid Ledger Entries | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:irs-1099` | erpnext | Regional | report | IRS 1099 | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:issue-analytics` | erpnext | Support | report | Issue Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:issue-summary` | erpnext | Support | report | Issue Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:issued-items-against-work-order` | erpnext | Manufacturing | report | Issued Items Against Work Order | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-balance-simple` | erpnext | Stock | report | Item Balance (Simple) | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-price-stock` | erpnext | Stock | report | Item Price Stock | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-prices` | erpnext | Stock | report | Item Prices | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-shortage-report` | erpnext | Stock | report | Item Shortage Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-variant-details` | erpnext | Stock | report | Item Variant Details | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-wise-consumption` | erpnext | Stock | report | Item Wise Consumption | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-wise-price-list-rate` | erpnext | Stock | report | Item-wise Price List Rate | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-wise-purchase-history` | erpnext | Buying | report | Item-wise Purchase History | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-wise-purchase-register` | erpnext | Accounts | report | Item-wise Purchase Register | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-wise-sales-history` | erpnext | Selling | report | Item-wise Sales History | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:item-wise-sales-register` | erpnext | Accounts | report | Item-wise Sales Register | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:items-to-be-requested` | erpnext | Stock | report | Items To Be Requested | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:itemwise-recommended-reorder-level` | erpnext | Stock | report | Itemwise Recommended Reorder Level | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:job-card-summary` | erpnext | Manufacturing | report | Job Card Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:landed-cost-report` | erpnext | Stock | report | Landed Cost Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:lead-conversion-time` | erpnext | CRM | report | Lead Conversion Time | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:lead-details` | erpnext | CRM | report | Lead Details | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:lead-owner-efficiency` | erpnext | CRM | report | Lead Owner Efficiency | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:lost-opportunity` | erpnext | CRM | report | Lost Opportunity | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:lost-quotations` | erpnext | Selling | report | Lost Quotations | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:maintenance-schedules` | erpnext | Maintenance | report | Maintenance Schedules | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:material-requests-for-which-supplier-quotations-are-not-created` | erpnext | Stock | report | Material Requests for which Supplier Quotations are not created | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:material-requirements-planning-report` | erpnext | Manufacturing | report | Material Requirements Planning Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:negative-batch-report` | erpnext | Stock | report | Negative Batch Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:open-work-orders` | erpnext | Manufacturing | report | Open Work Orders | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:opportunity-summary-by-sales-stage` | erpnext | CRM | report | Opportunity Summary by Sales Stage | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:payment-ledger` | erpnext | Accounts | report | Payment Ledger | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:payment-period-based-on-invoice-date` | erpnext | Accounts | report | Payment Period Based On Invoice Date | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:payment-terms-status-for-sales-order` | erpnext | Selling | report | Payment Terms Status for Sales Order | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:pending-so-items-for-purchase-request` | erpnext | Selling | report | Pending SO Items For Purchase Request | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:pos-register` | erpnext | Accounts | report | POS Register | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:process-loss-report` | erpnext | Manufacturing | report | Process Loss Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:procurement-tracker` | erpnext | Buying | report | Procurement Tracker | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:product-bundle-balance` | erpnext | Stock | report | Product Bundle Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:production-analytics` | erpnext | Manufacturing | report | Production Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:production-plan-summary` | erpnext | Manufacturing | report | Production Plan Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:production-planning-report` | erpnext | Manufacturing | report | Production Planning Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:profit-and-loss-statement` | erpnext | Accounts | report | Profit and Loss Statement | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:profitability-analysis` | erpnext | Accounts | report | Profitability Analysis | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:project-billing-summary` | erpnext | Projects | report | Project Billing Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:project-summary` | erpnext | Projects | report | Project Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:project-wise-stock-tracking` | erpnext | Projects | report | Project wise Stock Tracking | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:prospects-engaged-but-not-converted` | erpnext | CRM | report | Prospects Engaged But Not Converted | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:purchase-analytics` | erpnext | Buying | report | Purchase Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:purchase-invoice-trends` | erpnext | Accounts | report | Purchase Invoice Trends | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:purchase-order-analysis` | erpnext | Buying | report | Purchase Order Analysis | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:purchase-order-trends` | erpnext | Buying | report | Purchase Order Trends | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:purchase-receipt-trends` | erpnext | Stock | report | Purchase Receipt Trends | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:purchase-register` | erpnext | Accounts | report | Purchase Register | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:quality-inspection-summary` | erpnext | Manufacturing | report | Quality Inspection Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:quotation-trends` | erpnext | Selling | report | Quotation Trends | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:received-items-to-be-billed` | erpnext | Accounts | report | Received Items To Be Billed | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:requested-items-to-be-transferred` | erpnext | Stock | report | Requested Items To Be Transferred | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:requested-items-to-order-and-receive` | erpnext | Buying | report | Requested Items to Order and Receive | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:reserved-stock` | erpnext | Stock | report | Reserved Stock | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:review` | erpnext | Quality Management | report | Review | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-analytics` | erpnext | Selling | report | Sales Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-invoice-trends` | erpnext | Accounts | report | Sales Invoice Trends | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-order-analysis` | erpnext | Selling | report | Sales Order Analysis | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-order-trends` | erpnext | Selling | report | Sales Order Trends | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-partner-commission-summary` | erpnext | Selling | report | Sales Partner Commission Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-partner-target-variance-based-on-item-group` | erpnext | Selling | report | Sales Partner Target Variance based on Item Group | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-partner-transaction-summary` | erpnext | Selling | report | Sales Partner Transaction Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-partners-commission` | erpnext | Accounts | report | Sales Partners Commission | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-payment-summary` | erpnext | Accounts | report | Sales Payment Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-person-commission-summary` | erpnext | Selling | report | Sales Person Commission Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-person-target-variance-based-on-item-group` | erpnext | Selling | report | Sales Person Target Variance Based On Item Group | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-person-wise-transaction-summary` | erpnext | Selling | report | Sales Person-wise Transaction Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-pipeline-analytics` | erpnext | CRM | report | Sales Pipeline Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:sales-register` | erpnext | Accounts | report | Sales Register | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:serial-and-batch-summary` | erpnext | Stock | report | Serial and Batch Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:serial-no-and-batch-traceability` | erpnext | Stock | report | Serial No and Batch Traceability | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:serial-no-ledger` | erpnext | Stock | report | Serial No Ledger | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:serial-no-service-contract-expiry` | erpnext | Stock | report | Serial No Service Contract Expiry | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:serial-no-status` | erpnext | Stock | report | Serial No Status | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:serial-no-warranty-expiry` | erpnext | Stock | report | Serial No Warranty Expiry | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:share-balance` | erpnext | Accounts | report | Share Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:share-ledger` | erpnext | Accounts | report | Share Ledger | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-ageing` | erpnext | Stock | report | Stock Ageing | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-analytics` | erpnext | Stock | report | Stock Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-and-account-value-comparison` | erpnext | Stock | report | Stock and Account Value Comparison | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-balance` | erpnext | Stock | report | Stock Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-ledger` | erpnext | Stock | report | Stock Ledger | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-ledger-invariant-check` | erpnext | Stock | report | Stock Ledger Invariant Check | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-ledger-variance` | erpnext | Stock | report | Stock Ledger Variance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-projected-qty` | erpnext | Stock | report | Stock Projected Qty | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-qty-vs-batch-qty` | erpnext | Stock | report | Stock Qty vs Batch Qty | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:stock-qty-vs-serial-no-count` | erpnext | Stock | report | Stock Qty vs Serial No Count | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:subcontract-order-summary` | erpnext | Buying | report | Subcontract Order Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:subcontracted-item-to-be-received` | erpnext | Buying | report | Subcontracted Item To Be Received | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:subcontracted-raw-materials-to-be-transferred` | erpnext | Buying | report | Subcontracted Raw Materials To Be Transferred | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:supplier-ledger-summary` | erpnext | Accounts | report | Supplier Ledger Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:supplier-quotation-comparison` | erpnext | Buying | report | Supplier Quotation Comparison | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:supplier-wise-sales-analytics` | erpnext | Stock | report | Supplier-Wise Sales Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:support-hour-distribution` | erpnext | Support | report | Support Hour Distribution | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:tax-withholding-details` | erpnext | Accounts | report | Tax Withholding Details | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:tds-computation-summary` | erpnext | Accounts | report | TDS Computation Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:territory-target-variance-based-on-item-group` | erpnext | Selling | report | Territory Target Variance Based On Item Group | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:territory-wise-sales` | erpnext | Selling | report | Territory-wise Sales | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:timesheet-billing-summary` | erpnext | Projects | report | Timesheet Billing Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:total-stock-summary` | erpnext | Stock | report | Total Stock Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:trial-balance` | erpnext | Accounts | report | Trial Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:trial-balance-for-party` | erpnext | Accounts | report | Trial Balance for Party | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:trial-balance-simple` | erpnext | Accounts | report | Trial Balance (Simple) | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:uae-vat-201` | erpnext | Regional | report | UAE VAT 201 | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:vat-audit-report` | erpnext | Regional | report | VAT Audit Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:voucher-wise-balance` | erpnext | Accounts | report | Voucher-wise Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:warehouse-wise-item-balance-age-and-value` | erpnext | Stock | report | Warehouse wise Item Balance Age and Value | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:warehouse-wise-stock-balance` | erpnext | Stock | report | Warehouse Wise Stock Balance | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:work-order-consumed-materials` | erpnext | Manufacturing | report | Work Order Consumed Materials | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:work-order-stock-report` | erpnext | Manufacturing | report | Work Order Stock Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:work-order-summary` | erpnext | Manufacturing | report | Work Order Summary | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:work-orders-in-progress` | erpnext | Manufacturing | report | Work Orders in Progress | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:report:youtube-interactions` | erpnext | Utilities | report | YouTube Interactions | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `erpnext:workspace-target:accounting:chart-profit-and-loss` | erpnext | Accounts | workspace_target | Profit and Loss | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:dashboard-accounts` | erpnext | Accounts | workspace_target | Dashboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-account` | erpnext | Accounts | workspace_target | Chart of Accounts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-accounting-dimension` | erpnext | Accounts | workspace_target | Accounting Dimension | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-accounting-period` | erpnext | Accounts | workspace_target | Accounting Period | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-accounts-settings` | erpnext | Accounts | workspace_target | Accounts Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-bank` | erpnext | Accounts | workspace_target | Bank | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-bank-account` | erpnext | Accounts | workspace_target | Bank Account | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-bank-clearance` | erpnext | Accounts | workspace_target | Bank Clearance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-bank-reconciliation-tool` | erpnext | Accounts | workspace_target | Bank Reconciliation Tool | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-budget` | erpnext | Accounts | workspace_target | Budget | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-chart-of-accounts-importer` | erpnext | Accounts | workspace_target | Chart of Accounts Importer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-company` | erpnext | Accounts | workspace_target | Company | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-cost-center` | erpnext | Accounts | workspace_target | Chart of Cost Centers | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-cost-center-allocation` | erpnext | Accounts | workspace_target | Cost Center Allocation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-currency` | erpnext | Accounts | workspace_target | Currency | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-currency-exchange` | erpnext | Accounts | workspace_target | Currency Exchange | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-exchange-rate-revaluation` | erpnext | Accounts | workspace_target | Exchange Rate Revaluation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-finance-book` | erpnext | Accounts | workspace_target | Finance Book | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-fiscal-year` | erpnext | Accounts | workspace_target | Fiscal Year | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-item-tax-template` | erpnext | Accounts | workspace_target | Item Tax Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-journal-entry` | erpnext | Accounts | workspace_target | Journal Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-journal-entry-template` | erpnext | Accounts | workspace_target | Journal Entry Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-lower-deduction-certificate` | erpnext | Accounts | workspace_target | Lower Deduction Certificate | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-mode-of-payment` | erpnext | Accounts | workspace_target | Mode of Payment | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-monthly-distribution` | erpnext | Accounts | workspace_target | Monthly Distribution | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-opening-invoice-creation-tool` | erpnext | Accounts | workspace_target | Opening Invoice Creation Tool | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-payment-entry` | erpnext | Accounts | workspace_target | Payment Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-payment-term` | erpnext | Accounts | workspace_target | Payment Term | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-period-closing-voucher` | erpnext | Accounts | workspace_target | Period Closing Voucher | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-plaid-settings` | erpnext | Accounts | workspace_target | Plaid Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-purchase-invoice` | erpnext | Accounts | workspace_target | Purchase Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-purchase-taxes-and-charges-template` | erpnext | Accounts | workspace_target | Purchase Taxes and Charges Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-sales-invoice` | erpnext | Accounts | workspace_target | Sales Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-sales-taxes-and-charges-template` | erpnext | Accounts | workspace_target | Sales Taxes and Charges Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-share-transfer` | erpnext | Accounts | workspace_target | Share Transfer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-shareholder` | erpnext | Accounts | workspace_target | Shareholder | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-subscription` | erpnext | Accounts | workspace_target | Subscription | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-subscription-plan` | erpnext | Accounts | workspace_target | Subscription Plan | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-subscription-settings` | erpnext | Accounts | workspace_target | Subscription Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-tax-category` | erpnext | Accounts | workspace_target | Tax Category | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-tax-rule` | erpnext | Accounts | workspace_target | Tax Rule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-tax-withholding-category` | erpnext | Accounts | workspace_target | Tax Withholding Category | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:doctype-terms-and-conditions` | erpnext | Accounts | workspace_target | Terms and Conditions | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:number-card-total-incoming-bills` | erpnext | Accounts | workspace_target | Total Incoming Bills | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:number-card-total-incoming-payment` | erpnext | Accounts | workspace_target | Total Incoming Payment | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:number-card-total-outgoing-bills` | erpnext | Accounts | workspace_target | Total Outgoing Bills | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:number-card-total-outgoing-payment` | erpnext | Accounts | workspace_target | Total Outgoing Payment | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:report-accounts-receivable` | erpnext | Accounts | workspace_target | Accounts Receivable | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:report-bank-reconciliation-statement` | erpnext | Accounts | workspace_target | Bank Reconciliation Statement | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:report-budget-variance-report` | erpnext | Accounts | workspace_target | Budget Variance Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:report-general-ledger` | erpnext | Accounts | workspace_target | General Ledger | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:report-share-balance` | erpnext | Accounts | workspace_target | Share Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:report-share-ledger` | erpnext | Accounts | workspace_target | Share Ledger | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:accounting:report-trial-balance` | erpnext | Accounts | workspace_target | Trial Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:chart-asset-value-analytics` | erpnext | Assets | workspace_target | Asset Value Analytics | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:dashboard-asset` | erpnext | Assets | workspace_target | Dashboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset` | erpnext | Assets | workspace_target | Asset | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset-capitalization` | erpnext | Assets | workspace_target | Asset Capitalization | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset-category` | erpnext | Assets | workspace_target | Asset Category | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset-maintenance` | erpnext | Assets | workspace_target | Asset Maintenance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset-maintenance-log` | erpnext | Assets | workspace_target | Asset Maintenance Log | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset-maintenance-team` | erpnext | Assets | workspace_target | Asset Maintenance Team | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset-movement` | erpnext | Assets | workspace_target | Asset Movement | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset-repair` | erpnext | Assets | workspace_target | Asset Repair | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-asset-value-adjustment` | erpnext | Assets | workspace_target | Asset Value Adjustment | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:doctype-location` | erpnext | Assets | workspace_target | Location | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:report-asset-activity` | erpnext | Assets | workspace_target | Asset Activity | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:report-asset-depreciation-ledger` | erpnext | Assets | workspace_target | Asset Depreciation Ledger | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:report-asset-depreciations-and-balances` | erpnext | Assets | workspace_target | Asset Depreciations and Balances | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:report-asset-maintenance` | erpnext | Assets | workspace_target | Asset Maintenance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:assets:report-fixed-asset-register` | erpnext | Assets | workspace_target | Fixed Asset Register | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:chart-purchase-order-trends` | erpnext | Buying | workspace_target | Purchase Order Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:dashboard-buying` | erpnext | Buying | workspace_target | Dashboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-address` | erpnext | Buying | workspace_target | Address | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-buying-settings` | erpnext | Buying | workspace_target | Buying Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-contact` | erpnext | Buying | workspace_target | Contact | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-import-supplier-invoice` | erpnext | Buying | workspace_target | Import Supplier Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-item` | erpnext | Buying | workspace_target | Item | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-item-group` | erpnext | Buying | workspace_target | Item Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-item-price` | erpnext | Buying | workspace_target | Item Price | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-material-request` | erpnext | Buying | workspace_target | Material Request | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-price-list` | erpnext | Buying | workspace_target | Price List | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-pricing-rule` | erpnext | Buying | workspace_target | Pricing Rule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-product-bundle` | erpnext | Buying | workspace_target | Product Bundle | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-promotional-scheme` | erpnext | Buying | workspace_target | Promotional Scheme | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-purchase-invoice` | erpnext | Buying | workspace_target | Purchase Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-purchase-order` | erpnext | Buying | workspace_target | Purchase Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-purchase-taxes-and-charges-template` | erpnext | Buying | workspace_target | Purchase Taxes and Charges Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-request-for-quotation` | erpnext | Buying | workspace_target | Request for Quotation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-supplier` | erpnext | Buying | workspace_target | Supplier | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-supplier-group` | erpnext | Buying | workspace_target | Supplier Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-supplier-quotation` | erpnext | Buying | workspace_target | Supplier Quotation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-supplier-scorecard` | erpnext | Buying | workspace_target | Supplier Scorecard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-supplier-scorecard-criteria` | erpnext | Buying | workspace_target | Supplier Scorecard Criteria | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-supplier-scorecard-standing` | erpnext | Buying | workspace_target | Supplier Scorecard Standing | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-supplier-scorecard-variable` | erpnext | Buying | workspace_target | Supplier Scorecard Variable | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:doctype-terms-and-conditions` | erpnext | Buying | workspace_target | Terms and Conditions Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-address-and-contacts` | erpnext | Buying | workspace_target | Supplier Addresses And Contacts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-item-wise-purchase-history` | erpnext | Buying | workspace_target | Item-wise Purchase History | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-items-to-be-requested` | erpnext | Buying | workspace_target | Items To Be Requested | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-material-requests-for-which-supplier-quotations-are-not-created` | erpnext | Buying | workspace_target | Material Requests for which Supplier Quotations are not created | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-procurement-tracker` | erpnext | Buying | workspace_target | Procurement Tracker | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-purchase-analytics` | erpnext | Buying | workspace_target | Purchase Analytics | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-purchase-invoice-trends` | erpnext | Buying | workspace_target | Purchase Invoice Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-purchase-order-analysis` | erpnext | Buying | workspace_target | Purchase Order Analysis | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-purchase-order-trends` | erpnext | Buying | workspace_target | Purchase Order Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-purchase-receipt-trends` | erpnext | Buying | workspace_target | Purchase Receipt Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-requested-items-to-order-and-receive` | erpnext | Buying | workspace_target | Items to Order and Receive | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-subcontracted-item-to-be-received` | erpnext | Buying | workspace_target | Subcontracted Item To Be Received | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-subcontracted-raw-materials-to-be-transferred` | erpnext | Buying | workspace_target | Subcontracted Raw Materials To Be Transferred | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-supplier-quotation-comparison` | erpnext | Buying | workspace_target | Supplier Quotation Comparison | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:buying:report-supplier-wise-sales-analytics` | erpnext | Buying | workspace_target | Supplier-Wise Sales Analytics | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:chart-territory-wise-sales` | erpnext | CRM | workspace_target | Territory Wise Sales | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:dashboard-crm` | erpnext | CRM | workspace_target | Dashboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-appointment` | erpnext | CRM | workspace_target | Appointment | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-campaign` | erpnext | CRM | workspace_target | Campaign | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-communication` | erpnext | CRM | workspace_target | Communication | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-contact` | erpnext | CRM | workspace_target | Contact | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-contract` | erpnext | CRM | workspace_target | Contract | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-crm-settings` | erpnext | CRM | workspace_target | CRM Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-customer` | erpnext | CRM | workspace_target | Customer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-customer-group` | erpnext | CRM | workspace_target | Customer Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-email-campaign` | erpnext | CRM | workspace_target | Email Campaign | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-email-group` | erpnext | CRM | workspace_target | Email Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-lead` | erpnext | CRM | workspace_target | Lead | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-lead-source` | erpnext | CRM | workspace_target | Lead Source | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-maintenance-schedule` | erpnext | CRM | workspace_target | Maintenance Schedule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-maintenance-visit` | erpnext | CRM | workspace_target | Maintenance Visit | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-newsletter` | erpnext | CRM | workspace_target | Newsletter | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-opportunity` | erpnext | CRM | workspace_target | Opportunity | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-prospect` | erpnext | CRM | workspace_target | Prospect | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-sales-person` | erpnext | CRM | workspace_target | Sales Person | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-sales-stage` | erpnext | CRM | workspace_target | Sales Stage | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-sms-center` | erpnext | CRM | workspace_target | SMS Center | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-sms-log` | erpnext | CRM | workspace_target | SMS Log | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-sms-settings` | erpnext | CRM | workspace_target | SMS Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-territory` | erpnext | CRM | workspace_target | Territory | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:doctype-warranty-claim` | erpnext | CRM | workspace_target | Warranty Claim | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:page-sales-funnel` | erpnext | CRM | workspace_target | Sales Funnel | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-campaign-efficiency` | erpnext | CRM | workspace_target | Campaign Efficiency | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-first-response-time-for-opportunity` | erpnext | CRM | workspace_target | First Response Time for Opportunity | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-inactive-customers` | erpnext | CRM | workspace_target | Inactive Customers | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-lead-details` | erpnext | CRM | workspace_target | Lead Details | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-lead-owner-efficiency` | erpnext | CRM | workspace_target | Lead Owner Efficiency | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-opportunity-summary-by-sales-stage` | erpnext | CRM | workspace_target | Opportunity Summary by Sales Stage | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-prospects-engaged-but-not-converted` | erpnext | CRM | workspace_target | Prospects Engaged But Not Converted | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-sales-analytics` | erpnext | CRM | workspace_target | Sales Analytics | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:crm:report-sales-pipeline-analytics` | erpnext | CRM | workspace_target | Sales Pipeline Analytics | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-dropbox-settings` | erpnext | ERPNext Integrations | workspace_target | Dropbox Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-google-calendar` | erpnext | ERPNext Integrations | workspace_target | Google Calendar | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-google-contacts` | erpnext | ERPNext Integrations | workspace_target | Google Contacts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-google-drive` | erpnext | ERPNext Integrations | workspace_target | Google Drive | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-google-settings` | erpnext | ERPNext Integrations | workspace_target | Google Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-ldap-settings` | erpnext | ERPNext Integrations | workspace_target | LDAP Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-oauth-client` | erpnext | ERPNext Integrations | workspace_target | OAuth Client | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-oauth-provider-settings` | erpnext | ERPNext Integrations | workspace_target | OAuth Provider Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-plaid-settings` | erpnext | ERPNext Integrations | workspace_target | Plaid Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-s3-backup-settings` | erpnext | ERPNext Integrations | workspace_target | S3 Backup Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-slack-webhook-url` | erpnext | ERPNext Integrations | workspace_target | Slack Webhook URL | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-sms-settings` | erpnext | ERPNext Integrations | workspace_target | SMS Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-social-login-key` | erpnext | ERPNext Integrations | workspace_target | Social Login | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-integrations:doctype-webhook` | erpnext | ERPNext Integrations | workspace_target | Webhook | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-about-us-settings` | erpnext | Setup | workspace_target | About Us Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-accounts-settings` | erpnext | Setup | workspace_target | Accounts Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-auto-email-report` | erpnext | Setup | workspace_target | Auto Email Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-bulk-update` | erpnext | Setup | workspace_target | Bulk Update | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-buying-settings` | erpnext | Setup | workspace_target | Buying Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-contact-us-settings` | erpnext | Setup | workspace_target | Contact Us Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-crm-settings` | erpnext | Setup | workspace_target | CRM Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-data-export` | erpnext | Setup | workspace_target | Export Data | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-data-import` | erpnext | Setup | workspace_target | Import Data | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-deleted-document` | erpnext | Setup | workspace_target | Deleted Documents | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-domain-settings` | erpnext | Setup | workspace_target | Domain Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-email-account` | erpnext | Setup | workspace_target | Email Account | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-email-domain` | erpnext | Setup | workspace_target | Email Domain | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-email-template` | erpnext | Setup | workspace_target | Email Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-global-defaults` | erpnext | Setup | workspace_target | Global Defaults | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-manufacturing-settings` | erpnext | Setup | workspace_target | Manufacturing Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-newsletter` | erpnext | Setup | workspace_target | Newsletter | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-notification` | erpnext | Setup | workspace_target | Notification | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-notification-settings` | erpnext | Setup | workspace_target | Notification Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-print-format` | erpnext | Setup | workspace_target | Print Format | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-print-settings` | erpnext | Setup | workspace_target | Print Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-print-style` | erpnext | Setup | workspace_target | Print Style | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-projects-settings` | erpnext | Setup | workspace_target | Projects Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-selling-settings` | erpnext | Setup | workspace_target | Selling Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-stock-settings` | erpnext | Setup | workspace_target | Stock Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-support-settings` | erpnext | Setup | workspace_target | Support Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-system-settings` | erpnext | Setup | workspace_target | System Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-website-script` | erpnext | Setup | workspace_target | Website Script | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-website-settings` | erpnext | Setup | workspace_target | Website Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-website-theme` | erpnext | Setup | workspace_target | Website Theme | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-workflow` | erpnext | Setup | workspace_target | Workflow | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-workflow-action` | erpnext | Setup | workspace_target | Workflow Action | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:doctype-workflow-state` | erpnext | Setup | workspace_target | Workflow State | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:page-backups` | erpnext | Setup | workspace_target | Download Backups | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:erpnext-settings:page-print-format-builder` | erpnext | Setup | workspace_target | Print Format Builder | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-address-and-contacts` | erpnext | Accounts | workspace_target | Address And Contacts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-balance-sheet` | erpnext | Accounts | workspace_target | Balance Sheet | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-cash-flow` | erpnext | Accounts | workspace_target | Cash Flow | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-consolidated-financial-statement` | erpnext | Accounts | workspace_target | Consolidated Financial Statement | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-customer-credit-balance` | erpnext | Accounts | workspace_target | Customer Credit Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-customer-ledger-summary` | erpnext | Accounts | workspace_target | Customer Ledger Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-general-ledger` | erpnext | Accounts | workspace_target | General Ledger | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-gross-profit` | erpnext | Accounts | workspace_target | Gross Profit | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-payment-period-based-on-invoice-date` | erpnext | Accounts | workspace_target | Payment Period Based On Invoice Date | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-profit-and-loss-statement` | erpnext | Accounts | workspace_target | Profit and Loss Statement | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-profitability-analysis` | erpnext | Accounts | workspace_target | Profitability Analysis | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-purchase-invoice-trends` | erpnext | Accounts | workspace_target | Purchase Invoice Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-sales-invoice-trends` | erpnext | Accounts | workspace_target | Sales Invoice Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-sales-partners-commission` | erpnext | Accounts | workspace_target | Sales Partners Commission | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-sales-payment-summary` | erpnext | Accounts | workspace_target | Sales Payment Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-supplier-ledger-summary` | erpnext | Accounts | workspace_target | Supplier Ledger Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-trial-balance` | erpnext | Accounts | workspace_target | Trial Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-trial-balance-for-party` | erpnext | Accounts | workspace_target | Trial Balance for Party | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:financial-reports:report-uae-vat-201` | erpnext | Accounts | workspace_target | UAE VAT 201 | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-account` | erpnext | Setup | workspace_target | Chart of Accounts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-brand` | erpnext | Setup | workspace_target | Brand | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-chart-of-accounts-importer` | erpnext | Setup | workspace_target | Chart of Accounts Importer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-company` | erpnext | Setup | workspace_target | Company | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-customer` | erpnext | Setup | workspace_target | Customer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-customer-group` | erpnext | Setup | workspace_target | Customer Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-data-import` | erpnext | Setup | workspace_target | Import Data | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-email-account` | erpnext | Setup | workspace_target | Email Account | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-item` | erpnext | Setup | workspace_target | Item | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-lead` | erpnext | Setup | workspace_target | Lead | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-letter-head` | erpnext | Setup | workspace_target | Letter Head | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-opening-invoice-creation-tool` | erpnext | Setup | workspace_target | Opening Invoice Creation Tool | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-sales-invoice` | erpnext | Setup | workspace_target | Sales Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-stock-reconciliation` | erpnext | Setup | workspace_target | Stock Reconciliation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-supplier` | erpnext | Setup | workspace_target | Supplier | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-territory` | erpnext | Setup | workspace_target | Territory | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-uom` | erpnext | Setup | workspace_target | Unit of Measure (UOM) | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:doctype-warehouse` | erpnext | Setup | workspace_target | Warehouse | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:home:page-leaderboard` | erpnext | Setup | workspace_target | Leaderboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:chart-profit-and-loss` | erpnext | Accounts | workspace_target | Profit and Loss | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-account` | erpnext | Accounts | workspace_target | Chart of Accounts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-accounting-dimension` | erpnext | Accounts | workspace_target | Accounting Dimension | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-accounting-period` | erpnext | Accounts | workspace_target | Accounting Period | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-accounts-settings` | erpnext | Accounts | workspace_target | Accounts Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-bank` | erpnext | Accounts | workspace_target | Bank | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-bank-account` | erpnext | Accounts | workspace_target | Bank Account | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-bank-clearance` | erpnext | Accounts | workspace_target | Bank Clearance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-bank-reconciliation-tool` | erpnext | Accounts | workspace_target | Bank Reconciliation Tool | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-budget` | erpnext | Accounts | workspace_target | Budget | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-chart-of-accounts-importer` | erpnext | Accounts | workspace_target | Chart of Accounts Importer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-company` | erpnext | Accounts | workspace_target | Company | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-cost-center` | erpnext | Accounts | workspace_target | Chart of Cost Centers | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-cost-center-allocation` | erpnext | Accounts | workspace_target | Cost Center Allocation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-currency` | erpnext | Accounts | workspace_target | Currency | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-currency-exchange` | erpnext | Accounts | workspace_target | Currency Exchange | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-exchange-rate-revaluation` | erpnext | Accounts | workspace_target | Exchange Rate Revaluation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-finance-book` | erpnext | Accounts | workspace_target | Finance Book | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-fiscal-year` | erpnext | Accounts | workspace_target | Fiscal Year | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-item-tax-template` | erpnext | Accounts | workspace_target | Item Tax Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-journal-entry` | erpnext | Accounts | workspace_target | Journal Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-journal-entry-template` | erpnext | Accounts | workspace_target | Journal Entry Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-lower-deduction-certificate` | erpnext | Accounts | workspace_target | Lower Deduction Certificate | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-mode-of-payment` | erpnext | Accounts | workspace_target | Mode of Payment | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-monthly-distribution` | erpnext | Accounts | workspace_target | Monthly Distribution | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-opening-invoice-creation-tool` | erpnext | Accounts | workspace_target | Opening Invoice Creation Tool | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-payment-entry` | erpnext | Accounts | workspace_target | Payment Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-payment-term` | erpnext | Accounts | workspace_target | Payment Term | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-period-closing-voucher` | erpnext | Accounts | workspace_target | Period Closing Voucher | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-plaid-settings` | erpnext | Accounts | workspace_target | Plaid Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-purchase-taxes-and-charges-template` | erpnext | Accounts | workspace_target | Purchase Taxes and Charges Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-sales-taxes-and-charges-template` | erpnext | Accounts | workspace_target | Sales Taxes and Charges Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-share-transfer` | erpnext | Accounts | workspace_target | Share Transfer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-shareholder` | erpnext | Accounts | workspace_target | Shareholder | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-subscription` | erpnext | Accounts | workspace_target | Subscription | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-subscription-plan` | erpnext | Accounts | workspace_target | Subscription Plan | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-subscription-settings` | erpnext | Accounts | workspace_target | Subscription Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-tax-category` | erpnext | Accounts | workspace_target | Tax Category | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-tax-rule` | erpnext | Accounts | workspace_target | Tax Rule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-tax-withholding-category` | erpnext | Accounts | workspace_target | Tax Withholding Category | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:doctype-terms-and-conditions` | erpnext | Accounts | workspace_target | Terms and Conditions | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:number-card-total-incoming-bills` | erpnext | Accounts | workspace_target | Total Incoming Bills | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:number-card-total-incoming-payment` | erpnext | Accounts | workspace_target | Total Incoming Payment | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:number-card-total-outgoing-bills` | erpnext | Accounts | workspace_target | Total Outgoing Bills | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:number-card-total-outgoing-payment` | erpnext | Accounts | workspace_target | Total Outgoing Payment | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:report-bank-reconciliation-statement` | erpnext | Accounts | workspace_target | Bank Reconciliation Statement | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:report-budget-variance-report` | erpnext | Accounts | workspace_target | Budget Variance Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:report-share-balance` | erpnext | Accounts | workspace_target | Share Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:invoicing:report-share-ledger` | erpnext | Accounts | workspace_target | Share Ledger | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-bom` | erpnext | Manufacturing | workspace_target | BOM | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-bom-creator` | erpnext | Manufacturing | workspace_target | BOM Creator | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-bom-update-tool` | erpnext | Manufacturing | workspace_target | BOM Update Tool | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-downtime-entry` | erpnext | Manufacturing | workspace_target | Downtime Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-item` | erpnext | Manufacturing | workspace_target | Item | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-job-card` | erpnext | Manufacturing | workspace_target | Job Card | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-manufacturing-settings` | erpnext | Manufacturing | workspace_target | Manufacturing Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-operation` | erpnext | Manufacturing | workspace_target | Operation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-plant-floor` | erpnext | Manufacturing | workspace_target | Plant Floor | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-production-plan` | erpnext | Manufacturing | workspace_target | Production Plan | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-routing` | erpnext | Manufacturing | workspace_target | Routing | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-stock-entry` | erpnext | Manufacturing | workspace_target | Stock Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-work-order` | erpnext | Manufacturing | workspace_target | Work Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-workstation` | erpnext | Manufacturing | workspace_target | Workstation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:doctype-workstation-type` | erpnext | Manufacturing | workspace_target | Workstation Type | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:page-bom-comparison-tool` | erpnext | Manufacturing | workspace_target | BOM Comparison Tool | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-bom-operations-time` | erpnext | Manufacturing | workspace_target | BOM Operations Time | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-bom-search` | erpnext | Manufacturing | workspace_target | BOM Search | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-bom-stock-report` | erpnext | Manufacturing | workspace_target | BOM Stock Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-downtime-analysis` | erpnext | Manufacturing | workspace_target | Downtime Analysis | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-exponential-smoothing-forecasting` | erpnext | Manufacturing | workspace_target | Forecasting | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-job-card-summary` | erpnext | Manufacturing | workspace_target | Job Card Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-production-analytics` | erpnext | Manufacturing | workspace_target | Production Analytics | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-production-planning-report` | erpnext | Manufacturing | workspace_target | Production Planning Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-quality-inspection-summary` | erpnext | Manufacturing | workspace_target | Quality Inspection Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-work-order-consumed-materials` | erpnext | Manufacturing | workspace_target | Work Order Consumed Materials | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:manufacturing:report-work-order-summary` | erpnext | Manufacturing | workspace_target | Work Order Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:doctype-journal-entry` | erpnext | Accounts | workspace_target | Journal Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:doctype-payment-entry` | erpnext | Accounts | workspace_target | Payment Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:doctype-payment-reconciliation` | erpnext | Accounts | workspace_target | Payment Reconciliation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:doctype-purchase-invoice` | erpnext | Accounts | workspace_target | Purchase Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:doctype-supplier` | erpnext | Accounts | workspace_target | Supplier | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:report-accounts-payable` | erpnext | Accounts | workspace_target | Accounts Payable | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:report-accounts-payable-summary` | erpnext | Accounts | workspace_target | Accounts Payable Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:report-item-wise-purchase-register` | erpnext | Accounts | workspace_target | Item-wise Purchase Register | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:report-purchase-order-analysis` | erpnext | Accounts | workspace_target | Purchase Order Analysis | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:report-purchase-register` | erpnext | Accounts | workspace_target | Purchase Register | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:report-received-items-to-be-billed` | erpnext | Accounts | workspace_target | Received Items To Be Billed | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:payables:report-supplier-ledger-summary` | erpnext | Accounts | workspace_target | Supplier Ledger Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:chart-project-summary` | erpnext | Projects | workspace_target | Project Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:dashboard-project` | erpnext | Projects | workspace_target | Dashboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-activity-cost` | erpnext | Projects | workspace_target | Activity Cost | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-activity-type` | erpnext | Projects | workspace_target | Activity Type | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-project` | erpnext | Projects | workspace_target | Project | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-project-template` | erpnext | Projects | workspace_target | Project Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-project-type` | erpnext | Projects | workspace_target | Project Type | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-project-update` | erpnext | Projects | workspace_target | Project Update | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-projects-settings` | erpnext | Projects | workspace_target | Projects Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-task` | erpnext | Projects | workspace_target | Task | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:doctype-timesheet` | erpnext | Projects | workspace_target | Timesheet | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:report-daily-timesheet-summary` | erpnext | Projects | workspace_target | Daily Timesheet Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:report-delayed-tasks-summary` | erpnext | Projects | workspace_target | Delayed Tasks Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:report-project-billing-summary` | erpnext | Projects | workspace_target | Project Billing Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:projects:report-project-wise-stock-tracking` | erpnext | Projects | workspace_target | Project wise Stock Tracking | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-non-conformance` | erpnext | Quality Management | workspace_target | Non Conformance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-quality-action` | erpnext | Quality Management | workspace_target | Quality Action | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-quality-feedback` | erpnext | Quality Management | workspace_target | Quality Feedback | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-quality-feedback-template` | erpnext | Quality Management | workspace_target | Quality Feedback Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-quality-goal` | erpnext | Quality Management | workspace_target | Quality Goal | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-quality-inspection` | erpnext | Quality Management | workspace_target | Quality Inspection | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-quality-meeting` | erpnext | Quality Management | workspace_target | Quality Meeting | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-quality-procedure` | erpnext | Quality Management | workspace_target | Quality Procedure | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:quality:doctype-quality-review` | erpnext | Quality Management | workspace_target | Quality Review | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-cost-center` | erpnext | Accounts | workspace_target | Cost Center | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-customer` | erpnext | Accounts | workspace_target | Customer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-dunning` | erpnext | Accounts | workspace_target | Dunning | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-dunning-type` | erpnext | Accounts | workspace_target | Dunning Type | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-journal-entry` | erpnext | Accounts | workspace_target | Journal Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-payment-entry` | erpnext | Accounts | workspace_target | Payment Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-payment-gateway-account` | erpnext | Accounts | workspace_target | Payment Gateway Account | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-payment-reconciliation` | erpnext | Accounts | workspace_target | Payment Reconciliation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-payment-request` | erpnext | Accounts | workspace_target | Payment Request | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-pos-invoice` | erpnext | Accounts | workspace_target | POS Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:doctype-sales-invoice` | erpnext | Accounts | workspace_target | Sales Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:report-accounts-receivable` | erpnext | Accounts | workspace_target | Accounts Receivable | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:report-accounts-receivable-summary` | erpnext | Accounts | workspace_target | Accounts Receivable Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:report-delivered-items-to-be-billed` | erpnext | Accounts | workspace_target | Delivered Items To Be Billed | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:report-item-wise-sales-register` | erpnext | Accounts | workspace_target | Item-wise Sales Register | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:report-sales-order-analysis` | erpnext | Accounts | workspace_target | Sales Order Analysis | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:receivables:report-sales-register` | erpnext | Accounts | workspace_target | Sales Register | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:chart-sales-order-trends` | erpnext | Selling | workspace_target | Sales Order Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:dashboard-selling` | erpnext | Selling | workspace_target | Dashboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-address` | erpnext | Selling | workspace_target | Address | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-blanket-order` | erpnext | Selling | workspace_target | Blanket Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-campaign` | erpnext | Selling | workspace_target | Campaign | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-contact` | erpnext | Selling | workspace_target | Contact | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-coupon-code` | erpnext | Selling | workspace_target | Coupon Code | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-customer` | erpnext | Selling | workspace_target | Customer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-customer-group` | erpnext | Selling | workspace_target | Customer Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-item` | erpnext | Selling | workspace_target | Item | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-item-group` | erpnext | Selling | workspace_target | Item Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-item-price` | erpnext | Selling | workspace_target | Item Price | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-lead-source` | erpnext | Selling | workspace_target | Lead Source | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-loyalty-point-entry` | erpnext | Selling | workspace_target | Loyalty Point Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-loyalty-program` | erpnext | Selling | workspace_target | Loyalty Program | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-pos-closing-entry` | erpnext | Selling | workspace_target | POS Closing Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-pos-opening-entry` | erpnext | Selling | workspace_target | POS Opening Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-pos-profile` | erpnext | Selling | workspace_target | Point-of-Sale Profile | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-pos-settings` | erpnext | Selling | workspace_target | POS Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-price-list` | erpnext | Selling | workspace_target | Price List | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-pricing-rule` | erpnext | Selling | workspace_target | Pricing Rule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-product-bundle` | erpnext | Selling | workspace_target | Product Bundle | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-promotional-scheme` | erpnext | Selling | workspace_target | Promotional Scheme | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-quotation` | erpnext | Selling | workspace_target | Quotation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-sales-invoice` | erpnext | Selling | workspace_target | Sales Invoice | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-sales-order` | erpnext | Selling | workspace_target | Sales Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-sales-partner` | erpnext | Selling | workspace_target | Sales Partner | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-sales-person` | erpnext | Selling | workspace_target | Sales Person | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-sales-taxes-and-charges-template` | erpnext | Selling | workspace_target | Sales Taxes and Charges Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-selling-settings` | erpnext | Selling | workspace_target | Selling Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-shipping-rule` | erpnext | Selling | workspace_target | Shipping Rule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-terms-and-conditions` | erpnext | Selling | workspace_target | Terms and Conditions Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:doctype-territory` | erpnext | Selling | workspace_target | Territory | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:page-point-of-sale` | erpnext | Selling | workspace_target | Point of Sale | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:page-sales-funnel` | erpnext | Selling | workspace_target | Sales Funnel | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-address-and-contacts` | erpnext | Selling | workspace_target | Customer Addresses And Contacts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-available-stock-for-packing-items` | erpnext | Selling | workspace_target | Available Stock for Packing Items | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-customer-acquisition-and-loyalty` | erpnext | Selling | workspace_target | Customer Acquisition and Loyalty | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-customer-credit-balance` | erpnext | Selling | workspace_target | Customer Credit Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-customers-without-any-sales-transactions` | erpnext | Selling | workspace_target | Customers Without Any Sales Transactions | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-delivery-note-trends` | erpnext | Selling | workspace_target | Delivery Note Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-inactive-customers` | erpnext | Selling | workspace_target | Inactive Customers | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-item-wise-sales-history` | erpnext | Selling | workspace_target | Item-wise Sales History | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-pending-so-items-for-purchase-request` | erpnext | Selling | workspace_target | Pending SO Items For Purchase Request | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-quotation-trends` | erpnext | Selling | workspace_target | Quotation Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-sales-analytics` | erpnext | Selling | workspace_target | Sales Analytics | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-sales-invoice-trends` | erpnext | Selling | workspace_target | Sales Invoice Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-sales-order-analysis` | erpnext | Selling | workspace_target | Sales Order Analysis | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-sales-order-trends` | erpnext | Selling | workspace_target | Sales Order Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-sales-partner-target-variance-based-on-item-group` | erpnext | Selling | workspace_target | Sales Partner Target Variance Based On Item Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-sales-partners-commission` | erpnext | Selling | workspace_target | Sales Partners Commission | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-sales-person-target-variance-based-on-item-group` | erpnext | Selling | workspace_target | Sales Person Target Variance Based On Item Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-sales-person-wise-transaction-summary` | erpnext | Selling | workspace_target | Sales Person-wise Transaction Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:selling:report-territory-target-variance-based-on-item-group` | erpnext | Selling | workspace_target | Territory Target Variance Based On Item Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:chart-warehouse-wise-stock-value` | erpnext | Stock | workspace_target | Warehouse wise Stock Value | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:dashboard-stock` | erpnext | Stock | workspace_target | Dashboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-batch` | erpnext | Stock | workspace_target | Batch | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-brand` | erpnext | Stock | workspace_target | Brand | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-customs-tariff-number` | erpnext | Stock | workspace_target | Customs Tariff Number | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-delivery-note` | erpnext | Stock | workspace_target | Delivery Note | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-delivery-trip` | erpnext | Stock | workspace_target | Delivery Trip | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-installation-note` | erpnext | Stock | workspace_target | Installation Note | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-item` | erpnext | Stock | workspace_target | Item | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-item-alternative` | erpnext | Stock | workspace_target | Item Alternative | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-item-attribute` | erpnext | Stock | workspace_target | Item Attribute | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-item-group` | erpnext | Stock | workspace_target | Item Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-item-manufacturer` | erpnext | Stock | workspace_target | Item Manufacturer | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-item-price` | erpnext | Stock | workspace_target | Item Price | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-item-variant-settings` | erpnext | Stock | workspace_target | Item Variant Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-landed-cost-voucher` | erpnext | Stock | workspace_target | Landed Cost Voucher | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-material-request` | erpnext | Stock | workspace_target | Material Request | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-packing-slip` | erpnext | Stock | workspace_target | Packing Slip | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-pick-list` | erpnext | Stock | workspace_target | Pick List | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-price-list` | erpnext | Stock | workspace_target | Price List | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-pricing-rule` | erpnext | Stock | workspace_target | Pricing Rule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-product-bundle` | erpnext | Stock | workspace_target | Product Bundle | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-purchase-receipt` | erpnext | Stock | workspace_target | Purchase Receipt | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-quality-inspection` | erpnext | Stock | workspace_target | Quality Inspection | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-quality-inspection-template` | erpnext | Stock | workspace_target | Quality Inspection Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-quick-stock-balance` | erpnext | Stock | workspace_target | Quick Stock Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-serial-no` | erpnext | Stock | workspace_target | Serial No | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-shipping-rule` | erpnext | Stock | workspace_target | Shipping Rule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-stock-entry` | erpnext | Stock | workspace_target | Stock Entry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-stock-reconciliation` | erpnext | Stock | workspace_target | Stock Reconciliation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-stock-settings` | erpnext | Stock | workspace_target | Stock Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-uom` | erpnext | Stock | workspace_target | Unit of Measure (UOM) | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-uom-conversion-factor` | erpnext | Stock | workspace_target | UOM Conversion Factor | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:doctype-warehouse` | erpnext | Stock | workspace_target | Warehouse | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:number-card-total-active-items` | erpnext | Stock | workspace_target | Total Active Items | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:number-card-total-stock-value` | erpnext | Stock | workspace_target | Total Stock Value | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:number-card-total-warehouses` | erpnext | Stock | workspace_target | Total Warehouses | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:page-stock-balance` | erpnext | Stock | workspace_target | Stock Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-batch-item-expiry-status` | erpnext | Stock | workspace_target | Batch Item Expiry Status | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-batch-wise-balance-history` | erpnext | Stock | workspace_target | Batch-Wise Balance History | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-delivery-note-trends` | erpnext | Stock | workspace_target | Delivery Note Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-item-price-stock` | erpnext | Stock | workspace_target | Item Price Stock | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-item-prices` | erpnext | Stock | workspace_target | Item Prices | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-item-shortage-report` | erpnext | Stock | workspace_target | Item Shortage Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-item-variant-details` | erpnext | Stock | workspace_target | Item Variant Details | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-itemwise-recommended-reorder-level` | erpnext | Stock | workspace_target | Itemwise Recommended Reorder Level | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-purchase-order-analysis` | erpnext | Stock | workspace_target | Purchase Order Analysis | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-purchase-receipt-trends` | erpnext | Stock | workspace_target | Purchase Receipt Trends | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-requested-items-to-be-transferred` | erpnext | Stock | workspace_target | Requested Items To Be Transferred | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-sales-order-analysis` | erpnext | Stock | workspace_target | Sales Order Analysis | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-serial-no-service-contract-expiry` | erpnext | Stock | workspace_target | Serial No Service Contract Expiry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-serial-no-status` | erpnext | Stock | workspace_target | Serial No Status | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-serial-no-warranty-expiry` | erpnext | Stock | workspace_target | Serial No Warranty Expiry | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-stock-ageing` | erpnext | Stock | workspace_target | Stock Ageing | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-stock-analytics` | erpnext | Stock | workspace_target | Stock Analytics | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-stock-balance` | erpnext | Stock | workspace_target | Stock Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-stock-ledger` | erpnext | Stock | workspace_target | Stock Ledger | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-stock-projected-qty` | erpnext | Stock | workspace_target | Stock Projected Qty | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-subcontracted-item-to-be-received` | erpnext | Stock | workspace_target | Subcontracted Item To Be Received | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-subcontracted-raw-materials-to-be-transferred` | erpnext | Stock | workspace_target | Subcontracted Raw Materials To Be Transferred | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:stock:report-warehouse-wise-stock-balance` | erpnext | Stock | workspace_target | Warehouse Wise Stock Balance | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:chart-subcontracting-order` | erpnext | Subcontracting | workspace_target | Subcontracting Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:doctype-purchase-order` | erpnext | Subcontracting | workspace_target | Purchase Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:doctype-sales-order` | erpnext | Subcontracting | workspace_target | Sales Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:doctype-stock-entry` | erpnext | Subcontracting | workspace_target | Subcontracting Delivery | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:doctype-subcontracting-inward-order` | erpnext | Subcontracting | workspace_target | Subcontracting Inward Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:doctype-subcontracting-order` | erpnext | Subcontracting | workspace_target | Subcontracting Outward Order | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:doctype-subcontracting-receipt` | erpnext | Subcontracting | workspace_target | Subcontracting Receipt | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:number-card-active-subcontracted-items` | erpnext | Subcontracting | workspace_target | Active Subcontracted Items | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:number-card-subcontracting-inward-order-count` | erpnext | Subcontracting | workspace_target | Subcontracting Inward Order Count | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:number-card-subcontracting-outward-order-count` | erpnext | Subcontracting | workspace_target | Subcontracting Outward Order Count | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:report-subcontract-order-summary` | erpnext | Subcontracting | workspace_target | Subcontract Order Summary | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:report-subcontracted-item-to-be-received` | erpnext | Subcontracting | workspace_target | Subcontracted Item To Be Received | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:subcontracting:report-subcontracted-raw-materials-to-be-transferred` | erpnext | Subcontracting | workspace_target | Subcontracted Raw Materials To Be Transferred | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-issue` | erpnext | Support | workspace_target | Issue | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-issue-priority` | erpnext | Support | workspace_target | Issue Priority | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-issue-type` | erpnext | Support | workspace_target | Issue Type | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-maintenance-schedule` | erpnext | Support | workspace_target | Maintenance Schedule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-maintenance-visit` | erpnext | Support | workspace_target | Maintenance Visit | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-serial-no` | erpnext | Support | workspace_target | Serial No | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-service-level-agreement` | erpnext | Support | workspace_target | Service Level Agreement | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-support-settings` | erpnext | Support | workspace_target | Support Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:doctype-warranty-claim` | erpnext | Support | workspace_target | Warranty Claim | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace-target:support:report-first-response-time-for-issues` | erpnext | Support | workspace_target | First Response Time for Issues | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `erpnext:workspace:accounting` | erpnext | Accounts | workspace | Accounting | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:assets` | erpnext | Assets | workspace | Assets | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:buying` | erpnext | Buying | workspace | Buying | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:crm` | erpnext | CRM | workspace | CRM | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:erpnext-integrations` | erpnext | ERPNext Integrations | workspace | ERPNext Integrations | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:erpnext-settings` | erpnext | Setup | workspace | ERPNext Settings | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:financial-reports` | erpnext | Accounts | workspace | Financial Reports | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:home` | erpnext | Setup | workspace | Home | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:invoicing` | erpnext | Accounts | workspace | Invoicing | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:manufacturing` | erpnext | Manufacturing | workspace | Manufacturing | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:payables` | erpnext | Accounts | workspace | Payables | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:projects` | erpnext | Projects | workspace | Projects | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:quality` | erpnext | Quality Management | workspace | Quality | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:receivables` | erpnext | Accounts | workspace | Receivables | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:selling` | erpnext | Selling | workspace | Selling | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:stock` | erpnext | Stock | workspace | Stock | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:subcontracting` | erpnext | Subcontracting | workspace | Subcontracting | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `erpnext:workspace:support` | erpnext | Support | workspace | Support | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `frappe:child-doctype:about-us-team-member` | frappe | Website | child_doctype | About Us Team Member | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:amended-document-naming-settings` | frappe | Core | child_doctype | Amended Document Naming Settings | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:assignment-rule-day` | frappe | Automation | child_doctype | Assignment Rule Day | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:assignment-rule-user` | frappe | Automation | child_doctype | Assignment Rule User | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:auto-repeat-day` | frappe | Automation | child_doctype | Auto Repeat Day | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:block-module` | frappe | Core | child_doctype | Block Module | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:communication-link` | frappe | Core | child_doctype | Communication Link | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:company-history` | frappe | Website | child_doctype | Company History | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:contact-email` | frappe | Contacts | child_doctype | Contact Email | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:contact-phone` | frappe | Contacts | child_doctype | Contact Phone | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:customize-form-field` | frappe | Custom | child_doctype | Customize Form Field | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:dashboard-chart-field` | frappe | Desk | child_doctype | Dashboard Chart Field | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:dashboard-chart-link` | frappe | Desk | child_doctype | Dashboard Chart Link | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:defaultvalue` | frappe | Core | child_doctype | DefaultValue | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:docfield` | frappe | Core | child_doctype | DocField | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:docperm` | frappe | Core | child_doctype | DocPerm | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:doctype-action` | frappe | Core | child_doctype | DocType Action | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:doctype-layout-field` | frappe | Custom | child_doctype | DocType Layout Field | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:doctype-link` | frappe | Core | child_doctype | DocType Link | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:doctype-state` | frappe | Core | child_doctype | DocType State | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:document-naming-rule-condition` | frappe | Core | child_doctype | Document Naming Rule Condition | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:dynamic-link` | frappe | Core | child_doctype | Dynamic Link | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:email-queue-recipient` | frappe | Email | child_doctype | Email Queue Recipient | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:event-notifications` | frappe | Desk | child_doctype | Event Notifications | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:event-participants` | frappe | Desk | child_doctype | Event Participants | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:form-tour-step` | frappe | Desk | child_doctype | Form Tour Step | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:global-search-doctype` | frappe | Desk | child_doctype | Global Search DocType | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:has-domain` | frappe | Core | child_doctype | Has Domain | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:has-role` | frappe | Core | child_doctype | Has Role | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:imap-folder` | frappe | Email | child_doctype | IMAP Folder | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:installed-application` | frappe | Core | child_doctype | Installed Application | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:kanban-board-column` | frappe | Desk | child_doctype | Kanban Board Column | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:ldap-group-mapping` | frappe | Integrations | child_doctype | LDAP Group Mapping | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:log-setting-user` | frappe | Core | child_doctype | Log Setting User | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:logs-to-clear` | frappe | Core | child_doctype | Logs To Clear | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:navbar-item` | frappe | Core | child_doctype | Navbar Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:newsletter-attachment` | frappe | Email | child_doctype | Newsletter Attachment | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:newsletter-email-group` | frappe | Email | child_doctype | Newsletter Email Group | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:note-seen-by` | frappe | Desk | child_doctype | Note Seen By | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:notification-recipient` | frappe | Email | child_doctype | Notification Recipient | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:notification-subscribed-document` | frappe | Desk | child_doctype | Notification Subscribed Document | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:number-card-link` | frappe | Desk | child_doctype | Number Card Link | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:oauth-client-role` | frappe | Integrations | child_doctype | OAuth Client Role | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:oauth-scope` | frappe | Integrations | child_doctype | OAuth Scope | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:onboarding-permission` | frappe | Desk | child_doctype | Onboarding Permission | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:onboarding-step-map` | frappe | Desk | child_doctype | Onboarding Step Map | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:personal-data-deletion-step` | frappe | Website | child_doctype | Personal Data Deletion Step | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:portal-menu-item` | frappe | Website | child_doctype | Portal Menu Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:query-parameters` | frappe | Integrations | child_doctype | Query Parameters | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:recorder-query` | frappe | Core | child_doctype | Recorder Query | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:recorder-suggested-index` | frappe | Core | child_doctype | Recorder Suggested Index | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:report-column` | frappe | Core | child_doctype | Report Column | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:report-filter` | frappe | Core | child_doctype | Report Filter | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:review-level` | frappe | Social | child_doctype | Review Level | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:security-settings-contact` | frappe | Core | child_doctype | Security Settings Contact | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:security-settings-language` | frappe | Core | child_doctype | Security Settings Language | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:session-default` | frappe | Core | child_doctype | Session Default | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:sms-parameter` | frappe | Core | child_doctype | SMS Parameter | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:social-link-settings` | frappe | Website | child_doctype | Social Link Settings | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:system-health-report-errors` | frappe | Desk | child_doctype | System Health Report Errors | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:system-health-report-failing-jobs` | frappe | Desk | child_doctype | System Health Report Failing Jobs | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:system-health-report-queue` | frappe | Desk | child_doctype | System Health Report Queue | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:system-health-report-tables` | frappe | Desk | child_doctype | System Health Report Tables | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:system-health-report-workers` | frappe | Desk | child_doctype | System Health Report Workers | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:top-bar-item` | frappe | Website | child_doctype | Top Bar Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:user-document-type` | frappe | Core | child_doctype | User Document Type | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:user-email` | frappe | Core | child_doctype | User Email | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:user-group-member` | frappe | Core | child_doctype | User Group Member | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:user-role` | frappe | Core | child_doctype | User Role | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:user-select-document-type` | frappe | Core | child_doctype | User Select Document Type | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:user-social-login` | frappe | Core | child_doctype | User Social Login | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:user-type-module` | frappe | Core | child_doctype | User Type Module | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:web-form-field` | frappe | Website | child_doctype | Web Form Field | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:web-form-list-column` | frappe | Website | child_doctype | Web Form List Column | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:web-page-block` | frappe | Website | child_doctype | Web Page Block | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:web-template-field` | frappe | Website | child_doctype | Web Template Field | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:webhook-data` | frappe | Integrations | child_doctype | Webhook Data | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:webhook-header` | frappe | Integrations | child_doctype | Webhook Header | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:website-meta-tag` | frappe | Website | child_doctype | Website Meta Tag | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:website-route-redirect` | frappe | Website | child_doctype | Website Route Redirect | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:website-sidebar-item` | frappe | Website | child_doctype | Website Sidebar Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:website-slideshow-item` | frappe | Website | child_doctype | Website Slideshow Item | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:website-theme-ignore-app` | frappe | Website | child_doctype | Website Theme Ignore App | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workflow-action-permitted-role` | frappe | Workflow | child_doctype | Workflow Action Permitted Role | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workflow-document-state` | frappe | Workflow | child_doctype | Workflow Document State | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workflow-transition` | frappe | Workflow | child_doctype | Workflow Transition | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workspace-chart` | frappe | Desk | child_doctype | Workspace Chart | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workspace-custom-block` | frappe | Desk | child_doctype | Workspace Custom Block | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workspace-link` | frappe | Desk | child_doctype | Workspace Link | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workspace-number-card` | frappe | Desk | child_doctype | Workspace Number Card | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workspace-quick-list` | frappe | Desk | child_doctype | Workspace Quick List | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:child-doctype:workspace-shortcut` | frappe | Desk | child_doctype | Workspace Shortcut | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:dashboard-chart:background-job-activity` | frappe | Core | dashboard_chart | Background Job Activity | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `frappe:dashboard-chart:email-activity` | frappe | Desk | dashboard_chart | Email Activity | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `frappe:dashboard-chart:login` | frappe | Desk | dashboard_chart | Login | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `frappe:dashboard-chart:login-activity` | frappe | Desk | dashboard_chart | Login Activity | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `frappe:dashboard-chart:notifications-by-type` | frappe | Core | dashboard_chart | Notifications By Type | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `frappe:dashboard-chart:webpage-views` | frappe | Website | dashboard_chart | Webpage Views | C | Yes | — | Not implemented | Chart view not implemented in Retail ERP |
| `frappe:dashboard-connection:core-doctype-user-type-user-type-dashboard-py:user-type` | frappe |  | dashboard_connection | User Type Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `frappe:dashboard-connection:desk-doctype-dashboard-test-dashboard-py:test` | frappe |  | dashboard_connection | Test Dashboard | C | Yes | — | Not implemented | Dashboard connections and related-document actions require Retail ERP detail integration |
| `frappe:doctype:about-us-settings` | frappe | Website | doctype | About Us Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:access-log` | frappe | Core | doctype | Access Log | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:activity-log` | frappe | Core | doctype | Activity Log | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:address` | frappe | Contacts | doctype | Address | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:address-template` | frappe | Contacts | doctype | Address Template | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:assignment-rule` | frappe | Automation | doctype | Assignment Rule | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:audit-trail` | frappe | Core | doctype | Audit Trail | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:auto-email-report` | frappe | Email | doctype | Auto Email Report | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:auto-repeat` | frappe | Automation | doctype | Auto Repeat | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:blog-category` | frappe | Website | doctype | Blog Category | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:blog-post` | frappe | Website | doctype | Blog Post | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:blog-settings` | frappe | Website | doctype | Blog Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:blogger` | frappe | Website | doctype | Blogger | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:bulk-update` | frappe | Desk | doctype | Bulk Update | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:calendar-view` | frappe | Desk | doctype | Calendar View | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:changelog-feed` | frappe | Desk | doctype | Changelog Feed | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:client-script` | frappe | Custom | doctype | Client Script | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:color` | frappe | Website | doctype | Color | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:comment` | frappe | Core | doctype | Comment | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:communication` | frappe | Core | doctype | Communication | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:connected-app` | frappe | Integrations | doctype | Connected App | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:console-log` | frappe | Desk | doctype | Console Log | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:contact` | frappe | Contacts | doctype | Contact | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:contact-us-settings` | frappe | Website | doctype | Contact Us Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:country` | frappe | Geo | doctype | Country | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:currency` | frappe | Geo | doctype | Currency | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:custom-docperm` | frappe | Core | doctype | Custom DocPerm | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:custom-field` | frappe | Custom | doctype | Custom Field | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:custom-html-block` | frappe | Desk | doctype | Custom HTML Block | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:custom-role` | frappe | Core | doctype | Custom Role | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:customize-form` | frappe | Custom | doctype | Customize Form | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:dashboard` | frappe | Desk | doctype | Dashboard | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:dashboard-chart` | frappe | Desk | doctype | Dashboard Chart | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:dashboard-chart-source` | frappe | Desk | doctype | Dashboard Chart Source | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:dashboard-settings` | frappe | Desk | doctype | Dashboard Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:data-export` | frappe | Core | doctype | Data Export | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:data-import` | frappe | Core | doctype | Data Import | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:data-import-log` | frappe | Core | doctype | Data Import Log | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:deleted-document` | frappe | Core | doctype | Deleted Document | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:desktop-icon` | frappe | Desk | doctype | Desktop Icon | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:discussion-reply` | frappe | Website | doctype | Discussion Reply | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:discussion-topic` | frappe | Website | doctype | Discussion Topic | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:docshare` | frappe | Core | doctype | DocShare | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:doctype` | frappe | Core | doctype | DocType | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:doctype-layout` | frappe | Custom | doctype | DocType Layout | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:document-follow` | frappe | Email | doctype | Document Follow | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:document-naming-rule` | frappe | Core | doctype | Document Naming Rule | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:document-naming-settings` | frappe | Core | doctype | Document Naming Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:document-share-key` | frappe | Core | doctype | Document Share Key | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:domain` | frappe | Core | doctype | Domain | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:domain-settings` | frappe | Core | doctype | Domain Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:dropbox-settings` | frappe | Integrations | doctype | Dropbox Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-account` | frappe | Email | doctype | Email Account | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-domain` | frappe | Email | doctype | Email Domain | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-flag-queue` | frappe | Email | doctype | Email Flag Queue | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-group` | frappe | Email | doctype | Email Group | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-group-member` | frappe | Email | doctype | Email Group Member | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-queue` | frappe | Email | doctype | Email Queue | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-rule` | frappe | Email | doctype | Email Rule | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-template` | frappe | Email | doctype | Email Template | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:email-unsubscribe` | frappe | Email | doctype | Email Unsubscribe | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:energy-point-log` | frappe | Social | doctype | Energy Point Log | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:energy-point-rule` | frappe | Social | doctype | Energy Point Rule | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:energy-point-settings` | frappe | Social | doctype | Energy Point Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:error-log` | frappe | Core | doctype | Error Log | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:event` | frappe | Desk | doctype | Event | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:file` | frappe | Core | doctype | File | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:form-tour` | frappe | Desk | doctype | Form Tour | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:gender` | frappe | Contacts | doctype | Gender | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:global-search-settings` | frappe | Desk | doctype | Global Search Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:google-calendar` | frappe | Integrations | doctype | Google Calendar | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:google-contacts` | frappe | Integrations | doctype | Google Contacts | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:google-drive` | frappe | Integrations | doctype | Google Drive | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:google-settings` | frappe | Integrations | doctype | Google Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:help-article` | frappe | Website | doctype | Help Article | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:help-category` | frappe | Website | doctype | Help Category | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:installed-applications` | frappe | Core | doctype | Installed Applications | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:integration-request` | frappe | Integrations | doctype | Integration Request | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:kanban-board` | frappe | Desk | doctype | Kanban Board | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:language` | frappe | Core | doctype | Language | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:ldap-settings` | frappe | Integrations | doctype | LDAP Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:letter-head` | frappe | Printing | doctype | Letter Head | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:list-filter` | frappe | Desk | doctype | List Filter | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:list-view-settings` | frappe | Desk | doctype | List View Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:log-settings` | frappe | Core | doctype | Log Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:marketing-campaign` | frappe | Website | doctype | Marketing Campaign | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:milestone` | frappe | Automation | doctype | Milestone | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:milestone-tracker` | frappe | Automation | doctype | Milestone Tracker | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:module-def` | frappe | Core | doctype | Module Def | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:module-onboarding` | frappe | Desk | doctype | Module Onboarding | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:module-profile` | frappe | Core | doctype | Module Profile | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:navbar-settings` | frappe | Core | doctype | Navbar Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:network-printer-settings` | frappe | Printing | doctype | Network Printer Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:newsletter` | frappe | Email | doctype | Newsletter | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:note` | frappe | Desk | doctype | Note | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:notification` | frappe | Email | doctype | Notification | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:notification-log` | frappe | Desk | doctype | Notification Log | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:notification-settings` | frappe | Desk | doctype | Notification Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:number-card` | frappe | Desk | doctype | Number Card | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:oauth-authorization-code` | frappe | Integrations | doctype | OAuth Authorization Code | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:oauth-bearer-token` | frappe | Integrations | doctype | OAuth Bearer Token | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:oauth-client` | frappe | Integrations | doctype | OAuth Client | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:oauth-provider-settings` | frappe | Integrations | doctype | OAuth Provider Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:onboarding-step` | frappe | Desk | doctype | Onboarding Step | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:package` | frappe | Core | doctype | Package | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:package-import` | frappe | Core | doctype | Package Import | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:package-release` | frappe | Core | doctype | Package Release | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:page` | frappe | Core | doctype | Page | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:patch-log` | frappe | Core | doctype | Patch Log | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:permission-inspector` | frappe | Core | doctype | Permission Inspector | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:personal-data-deletion-request` | frappe | Website | doctype | Personal Data Deletion Request | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:personal-data-download-request` | frappe | Website | doctype | Personal Data Download Request | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:portal-settings` | frappe | Website | doctype | Portal Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:prepared-report` | frappe | Core | doctype | Prepared Report | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:print-format` | frappe | Printing | doctype | Print Format | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:print-format-field-template` | frappe | Printing | doctype | Print Format Field Template | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:print-settings` | frappe | Printing | doctype | Print Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:print-style` | frappe | Printing | doctype | Print Style | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:property-setter` | frappe | Custom | doctype | Property Setter | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:push-notification-settings` | frappe | Integrations | doctype | Push Notification Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:recorder` | frappe | Core | doctype | Recorder | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:reminder` | frappe | Automation | doctype | Reminder | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:report` | frappe | Core | doctype | Report | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:role` | frappe | Core | doctype | Role | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:role-permission-for-page-and-report` | frappe | Core | doctype | Role Permission for Page and Report | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:role-profile` | frappe | Core | doctype | Role Profile | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:route-history` | frappe | Desk | doctype | Route History | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:rq-job` | frappe | Core | doctype | RQ Job | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:rq-worker` | frappe | Core | doctype | RQ Worker | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:s3-backup-settings` | frappe | Integrations | doctype | S3 Backup Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:salutation` | frappe | Contacts | doctype | Salutation | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:scheduled-job-log` | frappe | Core | doctype | Scheduled Job Log | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:scheduled-job-type` | frappe | Core | doctype | Scheduled Job Type | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:scheduler-event` | frappe | Core | doctype | Scheduler Event | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:security-settings` | frappe | Core | doctype | Security Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:server-script` | frappe | Core | doctype | Server Script | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:session-default-settings` | frappe | Core | doctype | Session Default Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:slack-webhook-url` | frappe | Integrations | doctype | Slack Webhook URL | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:sms-settings` | frappe | Core | doctype | SMS Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:social-login-key` | frappe | Integrations | doctype | Social Login Key | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:submission-queue` | frappe | Core | doctype | Submission Queue | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:success-action` | frappe | Core | doctype | Success Action | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:system-console` | frappe | Desk | doctype | System Console | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:system-health-report` | frappe | Desk | doctype | System Health Report | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:system-settings` | frappe | Core | doctype | System Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:tag` | frappe | Desk | doctype | Tag | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:tag-link` | frappe | Desk | doctype | Tag Link | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:todo` | frappe | Desk | doctype | ToDo | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:token-cache` | frappe | Integrations | doctype | Token Cache | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:transaction-log` | frappe | Core | doctype | Transaction Log | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:translation` | frappe | Core | doctype | Translation | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:unhandled-email` | frappe | Email | doctype | Unhandled Email | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:user` | frappe | Core | doctype | User | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:user-group` | frappe | Core | doctype | User Group | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:user-invitation` | frappe | Core | doctype | User Invitation | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:user-permission` | frappe | Core | doctype | User Permission | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:user-type` | frappe | Core | doctype | User Type | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:version` | frappe | Core | doctype | Version | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:view-log` | frappe | Core | doctype | View Log | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:web-form` | frappe | Website | doctype | Web Form | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:web-page` | frappe | Website | doctype | Web Page | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:web-page-view` | frappe | Website | doctype | Web Page View | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:web-template` | frappe | Website | doctype | Web Template | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:webhook` | frappe | Integrations | doctype | Webhook | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:webhook-request-log` | frappe | Integrations | doctype | Webhook Request Log | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `frappe:doctype:website-route-meta` | frappe | Website | doctype | Website Route Meta | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:website-script` | frappe | Website | doctype | Website Script | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:website-settings` | frappe | Website | doctype | Website Settings | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:website-sidebar` | frappe | Website | doctype | Website Sidebar | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:website-slideshow` | frappe | Website | doctype | Website Slideshow | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:website-theme` | frappe | Website | doctype | Website Theme | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:workflow` | frappe | Workflow | doctype | Workflow | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:workflow-action` | frappe | Workflow | doctype | Workflow Action | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:workflow-action-master` | frappe | Workflow | doctype | Workflow Action Master | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:workflow-state` | frappe | Workflow | doctype | Workflow State | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:doctype:workspace` | frappe | Desk | doctype | Workspace | E | Yes | — | Not implemented | Required for ordinary-user parity |
| `frappe:document-action:access-log:make-access-log` | frappe | Core | document_action | Make Access Log | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:address:0-1` | frappe | Contacts | document_action | {0}: {1} | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:auto-email-report:download` | frappe | Email | document_action | Download | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:auto-email-report:send-now` | frappe | Email | document_action | Send Now | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:auto-repeat:make-auto-repeat` | frappe | Automation | document_action | Make Auto Repeat | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:blog-post:make-route` | frappe | Website | document_action | Make Route | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:bulk-update:submit-cancel-or-update-docs` | frappe | Desk | document_action | Submit Cancel Or Update Docs | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:calendar-view:show-calendar` | frappe | Desk | document_action | Show Calendar | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:client-script:add-script-for-child-table` | frappe | Custom | document_action | Add script for Child Table | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:client-script:compare-versions` | frappe | Custom | document_action | Compare Versions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:client-script:go-to-0` | frappe | Custom | document_action | Go to {0} | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:add-contact` | frappe | Core | document_action | Add Contact | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:close` | frappe | Core | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:contact` | frappe | Core | document_action | Contact | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:forward` | frappe | Core | document_action | Forward | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:mark-as-spam` | frappe | Core | document_action | Mark as Spam | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:move` | frappe | Core | document_action | Move | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:move-to-trash` | frappe | Core | document_action | Move To Trash | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:relink` | frappe | Core | document_action | Relink | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:reopen` | frappe | Core | document_action | Reopen | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:reply` | frappe | Core | document_action | Reply | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:communication:reply-all` | frappe | Core | document_action | Reply All | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:connected-app:connect-to` | frappe | Integrations | document_action | Connect to {} | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:connected-app:get-openid-configuration` | frappe | Integrations | document_action | Get OpenID Configuration | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:console-log:re-run-in-console` | frappe | Desk | document_action | Re-Run in Console | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:contact:0-1` | frappe | Contacts | document_action | {0}: {1} | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:contact:call` | frappe | Contacts | document_action | Call | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:contact:invite-as-user` | frappe | Contacts | document_action | Invite as User | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:custom-field:rename-fieldname` | frappe | Custom | document_action | Rename Fieldname | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:customize-form:export-customizations` | frappe | Custom | document_action | Export Customizations | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:customize-form:go-to-0-list` | frappe | Custom | document_action | Go to {0} List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:customize-form:reload` | frappe | Custom | document_action | Reload | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:customize-form:reset-all-customizations` | frappe | Custom | document_action | Reset All Customizations | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:customize-form:reset-layout` | frappe | Custom | document_action | Reset Layout | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:customize-form:set-permissions` | frappe | Custom | document_action | Set Permissions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:customize-form:trim-table` | frappe | Custom | document_action | Trim Table | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:dashboard-chart:add-chart-to-dashboard` | frappe | Desk | document_action | Add Chart to Dashboard | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:dashboard-chart:create-dashboard-chart` | frappe | Desk | document_action | Create Dashboard Chart | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:dashboard-chart:create-report-chart` | frappe | Desk | document_action | Create Report Chart | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:dashboard-settings:create-dashboard-settings` | frappe | Desk | document_action | Create Dashboard Settings | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:dashboard:show-dashboard` | frappe | Desk | document_action | Show Dashboard | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:data-import:export-errored-rows` | frappe | Core | document_action | Export Errored Rows | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:data-import:export-import-log` | frappe | Core | document_action | Export Import Log | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:data-import:go-to-0-list` | frappe | Core | document_action | Go to {0} List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:data-import:report-error` | frappe | Core | document_action | Report Error | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:deleted-document:open` | frappe | Core | document_action | Open | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:deleted-document:restore` | frappe | Core | document_action | Restore | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:discussion-topic:submit-discussion` | frappe | Website | document_action | Submit Discussion | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:doctype-layout:go-to-0-list` | frappe | Custom | document_action | Go to {0} List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:doctype-layout:sync-0-fields` | frappe | Custom | document_action | Sync {0} Fields | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:doctype:go-to-0` | frappe | Core | document_action | Go to {0} | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:doctype:go-to-0-list` | frappe | Core | document_action | Go to {0} List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:dropbox-settings:take-backup-now` | frappe | Integrations | document_action | Take Backup Now | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:email-account:pull-emails` | frappe | Email | document_action | Pull Emails | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:email-group:add-subscribers` | frappe | Email | document_action | Add Subscribers | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:email-group:import-subscribers` | frappe | Email | document_action | Import Subscribers | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:email-group:new-newsletter` | frappe | Email | document_action | New Newsletter | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:email-queue:retry-sending` | frappe | Email | document_action | Retry Sending | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:email-queue:send-now` | frappe | Email | document_action | Send Now | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:energy-point-log:revert` | frappe | Social | document_action | Revert | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:energy-point-settings:give-review-points` | frappe | Social | document_action | Give Review Points | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:error-log:show-related-errors` | frappe | Core | document_action | Show Related Errors | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:event:add-contacts` | frappe | Desk | document_action | Add Contacts | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:file:download` | frappe | Core | document_action | Download | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:file:optimize` | frappe | Core | document_action | Optimize | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:file:unzip` | frappe | Core | document_action | Unzip | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:file:view-file` | frappe | Core | document_action | View File | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:form-tour:reset` | frappe | Desk | document_action | Reset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:form-tour:show-tour` | frappe | Desk | document_action | Show Tour | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:global-search-settings:reset` | frappe | Desk | document_action | Reset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:google-calendar:sync-calendar` | frappe | Integrations | document_action | Sync Calendar | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:google-contacts:sync-contacts` | frappe | Integrations | document_action | Sync Contacts | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:google-drive:take-backup` | frappe | Integrations | document_action | Take Backup | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:installed-applications:update-hooks-resolution-order` | frappe | Core | document_action | Update Hooks Resolution Order | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:kanban-board:show-board` | frappe | Desk | document_action | Show Board | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:module-onboarding:reset` | frappe | Desk | document_action | Reset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:newsletter:check-broken-links` | frappe | Email | document_action | Check broken links | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:newsletter:schedule-sending` | frappe | Email | document_action | Schedule sending | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:newsletter:send-a-test-email` | frappe | Email | document_action | Send a test email | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:newsletter:send-now` | frappe | Email | document_action | Send now | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:notification-settings:go-to-notification-settings-list` | frappe | Desk | document_action | Go to Notification Settings List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:notification:get-alerts-for-today` | frappe | Email | document_action | Get Alerts for Today | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:number-card:add-card-to-dashboard` | frappe | Desk | document_action | Add Card to Dashboard | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:number-card:create-number-card` | frappe | Desk | document_action | Create Number Card | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:number-card:create-report-number-card` | frappe | Desk | document_action | Create Report Number Card | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:page:go-to-0-page` | frappe | Core | document_action | Go to {0} Page | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:personal-data-deletion-request:delete-data` | frappe | Website | document_action | Delete Data | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:personal-data-deletion-request:put-on-hold` | frappe | Website | document_action | Put on Hold | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:portal-settings:reset` | frappe | Website | document_action | Reset | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:prepared-report:download-as-csv` | frappe | Core | document_action | Download as CSV | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:prepared-report:make-prepared-report` | frappe | Core | document_action | Make Prepared Report | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:print-format:edit-format` | frappe | Printing | document_action | Edit Format | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:print-format:make-default` | frappe | Printing | document_action | Make Default | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:print-format:set-as-default` | frappe | Printing | document_action | Set as Default | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:print-style:print-settings` | frappe | Printing | document_action | Print Settings | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:recorder:add-indexes` | frappe | Core | document_action | Add Indexes | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:recorder:suggest-optimizations` | frappe | Core | document_action | Suggest Optimizations | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:reminder:create-new-reminder` | frappe | Automation | document_action | Create New Reminder | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:report:show-report` | frappe | Core | document_action | Show Report | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:role-permission-for-page-and-report:reset-to-defaults` | frappe | Core | document_action | Reset to defaults | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:role:role-permissions-manager` | frappe | Core | document_action | Role Permissions Manager | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:role:show-users` | frappe | Core | document_action | Show Users | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:rq-job:force-stop-job` | frappe | Core | document_action | Force Stop job | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:s3-backup-settings:take-backup-now` | frappe | Integrations | document_action | Take Backup Now | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:scheduled-job-type:frappe-core-doctype-scheduled-job-type-scheduled-job-type-execute-event` | frappe | Core | document_action | Execute | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:server-script:compare-versions` | frappe | Core | document_action | Compare Versions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:submission-queue:unlock-reference-document` | frappe | Core | document_action | Unlock Reference Document | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:system-console:app-console-log` | frappe | Desk | document_action | Logs | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:system-console:frappe-desk-doctype-system-console-system-console-execute-code` | frappe | Desk | document_action | Execute | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:todo:close` | frappe | Desk | document_action | Close | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:todo:new` | frappe | Desk | document_action | New | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:todo:reopen` | frappe | Desk | document_action | Reopen | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user-invitation:cancel` | frappe | Core | document_action | Cancel | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user-invitation:cancel-invite` | frappe | Core | document_action | Cancel Invite | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user-permission:view-permitted-documents` | frappe | Core | document_action | View Permitted Documents | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user:create-user-email` | frappe | Core | document_action | Create User Email | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user:impersonate` | frappe | Core | document_action | Impersonate | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user:reset-ldap-password` | frappe | Core | document_action | Reset LDAP Password | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user:reset-otp-secret` | frappe | Core | document_action | Reset OTP Secret | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user:reset-password` | frappe | Core | document_action | Reset Password | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user:set-user-permissions` | frappe | Core | document_action | Set User Permissions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:user:view-permitted-documents` | frappe | Core | document_action | View Permitted Documents | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:version:show-all-versions` | frappe | Core | document_action | Show all Versions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:web-form:get-fields` | frappe | Website | document_action | Get Fields | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:web-page-view:make-view-log` | frappe | Website | document_action | Make View Log | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:website-route-meta:visit-web-page` | frappe | Website | document_action | Visit Web Page | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:website-settings:frappe-sessions-clear` | frappe | Website | document_action | Clear Cache | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:website-settings:view-website` | frappe | Website | document_action | View Website | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:website-slideshow:fetch-attached-images-from-document` | frappe | Website | document_action | Fetch attached images from document | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:website-theme:set-as-default-theme` | frappe | Website | document_action | Set as Default Theme | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:document-action:workflow:go-to-0-list` | frappe | Workflow | document_action | Go to {0} List | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `frappe:installed-app:frappe` | frappe | frappe | installed_app | frappe | E | Yes | — | Not implemented | Installed app capabilities require classified Retail ERP routes or safe embedding |
| `frappe:number-card:active-rq-worker` | frappe | Core | number_card | Active RQ Worker | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:number-card:error-logs` | frappe | Core | number_card | Error Logs | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:number-card:failed-login-attempts` | frappe | Desk | number_card | Failed Login Attempts | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:number-card:published-web-forms` | frappe | Desk | number_card | Published Web Forms | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:number-card:published-web-pages` | frappe | Desk | number_card | Published Web Pages | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:number-card:scheduled-jobs` | frappe | Core | number_card | Scheduled Jobs | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:number-card:total-website-users` | frappe | Desk | number_card | Total Website Users | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:number-card:users` | frappe | Desk | number_card | Users | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:number-card:website-themes-available` | frappe | Website | number_card | Website Themes Available | C | Yes | — | Not implemented | Dashboard view not implemented in Retail ERP |
| `frappe:page:backups` | frappe | Desk | page | backups | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:dashboard-view` | frappe | Core | page | dashboard-view | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:desktop` | frappe | Desk | page | desktop | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:leaderboard` | frappe | Desk | page | leaderboard | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:permission-manager` | frappe | Core | page | permission-manager | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:print` | frappe | Printing | page | print | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:print-format-builder` | frappe | Printing | page | print-format-builder | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:print-format-builder-beta` | frappe | Printing | page | print-format-builder-beta | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:setup-wizard` | frappe | Desk | page | setup-wizard | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:user-profile` | frappe | Desk | page | user-profile | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:page:workflow-builder` | frappe | Workflow | page | workflow-builder | E | Yes | — | Not implemented | Required or safe integration route must be designed |
| `frappe:platform-capability:assignments` | frappe | Desk | platform_capability | Assignments | A | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:attachments` | frappe | Desk | platform_capability | Attachments | A | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:bulk-rename` | frappe | Desk | platform_capability | Bulk Rename | E | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:bulk-update` | frappe | Desk | platform_capability | Bulk Update | E | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:comments` | frappe | Desk | platform_capability | Comments | A | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:data-export` | frappe | Desk | platform_capability | Data Export | E | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:data-import` | frappe | Desk | platform_capability | Data Import | E | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:document-email` | frappe | Desk | platform_capability | Document Email | E | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:document-print-preview` | frappe | Desk | platform_capability | Document Print Preview | E | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:document-sharing` | frappe | Desk | platform_capability | Document Sharing | E | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:likes-and-follows` | frappe | Desk | platform_capability | Likes and Follows | A | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:list-bulk-actions` | frappe | Desk | platform_capability | List Bulk Actions | A | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:list-export` | frappe | Desk | platform_capability | List Export | A | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:pdf-download` | frappe | Desk | platform_capability | PDF Download | E | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:tags` | frappe | Desk | platform_capability | Tags | A | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:platform-capability:version-history` | frappe | Desk | platform_capability | Version History | A | Yes | — | Not implemented | Shared platform capability is not fully implemented in Retail ERP |
| `frappe:report:addresses-and-contacts` | frappe | Contacts | report | Addresses And Contacts | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:audit-system-hooks` | frappe | Custom | report | Audit System Hooks | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:database-storage-usage-by-tables` | frappe | Core | report | Database Storage Usage By Tables | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:document-share-report` | frappe | Core | report | Document Share Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:permitted-documents-for-user` | frappe | Core | report | Permitted Documents For User | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:prepared-report-analytics` | frappe | Core | report | Prepared Report Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:todo` | frappe | Desk | report | ToDo | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:transaction-log-report` | frappe | Core | report | Transaction Log Report | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:user-doctype-permissions` | frappe | Core | report | User Doctype Permissions | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:report:website-analytics` | frappe | Website | report | Website Analytics | D | Yes | — | Not implemented | Required: no Retail ERP report adapter |
| `frappe:source-only-report:user-activity-report` | frappe | Core | source_only_report | User Activity Report | D | No | — | Not implemented | None until the Report is installed/enabled on this site |
| `frappe:source-only-report:user-activity-report-without-sort` | frappe | Core | source_only_report | User Activity Report Without Sort | D | No | — | Not implemented | None until the Report is installed/enabled on this site |
| `frappe:workspace-target:build:doctype-activity-log` | frappe | Core | workspace_target | Activity Log | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-client-script` | frappe | Core | workspace_target | Client Script | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-communication` | frappe | Core | workspace_target | Communication Logs | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-custom-field` | frappe | Core | workspace_target | Custom Field | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-customize-form` | frappe | Core | workspace_target | Customize Form | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-dashboard` | frappe | Core | workspace_target | Dashboard | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-dashboard-chart` | frappe | Core | workspace_target | Dashboard Chart | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-doctype` | frappe | Core | workspace_target | DocType | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-error-log` | frappe | Core | workspace_target | Error Logs | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-module-def` | frappe | Core | workspace_target | Module Def | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-module-onboarding` | frappe | Core | workspace_target | Module Onboarding | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-navbar-settings` | frappe | Core | workspace_target | Navbar Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-package` | frappe | Core | workspace_target | Package | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-package-import` | frappe | Core | workspace_target | Package Import | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-page` | frappe | Core | workspace_target | Page | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-print-format` | frappe | Core | workspace_target | Print Format | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-report` | frappe | Core | workspace_target | Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-rq-job` | frappe | Core | workspace_target | Background Jobs | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-scheduled-job-log` | frappe | Core | workspace_target | Scheduled Jobs Logs | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-scheduled-job-type` | frappe | Core | workspace_target | Scheduled Job Type | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-server-script` | frappe | Core | workspace_target | Server Script | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-translation` | frappe | Core | workspace_target | Custom Translation | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-webhook-request-log` | frappe | Core | workspace_target | Webhook Request Log | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:build:doctype-workspace` | frappe | Core | workspace_target | Workspace | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-google-calendar` | frappe | Integrations | workspace_target | Google Calendar | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-google-contacts` | frappe | Integrations | workspace_target | Google Contacts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-google-settings` | frappe | Integrations | workspace_target | Google Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-ldap-settings` | frappe | Integrations | workspace_target | LDAP Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-oauth-client` | frappe | Integrations | workspace_target | OAuth Client | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-oauth-provider-settings` | frappe | Integrations | workspace_target | OAuth Provider Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-push-notification-settings` | frappe | Integrations | workspace_target | Push Notification Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-slack-webhook-url` | frappe | Integrations | workspace_target | Slack Webhook URL | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-sms-settings` | frappe | Integrations | workspace_target | SMS Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-social-login-key` | frappe | Integrations | workspace_target | Social Login Key | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:integrations:doctype-webhook` | frappe | Integrations | workspace_target | Webhook | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-assignment-rule` | frappe | Automation | workspace_target | Assignment Rule | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-auto-email-report` | frappe | Automation | workspace_target | Auto Email Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-auto-repeat` | frappe | Automation | workspace_target | Auto Repeat | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-bulk-update` | frappe | Automation | workspace_target | Bulk Update | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-data-export` | frappe | Automation | workspace_target | Export Data | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-data-import` | frappe | Automation | workspace_target | Import Data | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-deleted-document` | frappe | Automation | workspace_target | Deleted Documents | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-email-account` | frappe | Automation | workspace_target | Email Account | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-email-domain` | frappe | Automation | workspace_target | Email Domain | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-email-group` | frappe | Automation | workspace_target | Email Group | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-email-template` | frappe | Automation | workspace_target | Email Template | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-event` | frappe | Automation | workspace_target | Calendar | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-file` | frappe | Automation | workspace_target | File | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-milestone` | frappe | Automation | workspace_target | Milestone | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-newsletter` | frappe | Automation | workspace_target | Newsletter | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-note` | frappe | Automation | workspace_target | Note | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-notification` | frappe | Automation | workspace_target | Notification | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-notification-settings` | frappe | Automation | workspace_target | Notification Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-print-heading` | frappe | Automation | workspace_target | Print Heading | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-print-settings` | frappe | Automation | workspace_target | Print Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:doctype-todo` | frappe | Automation | workspace_target | ToDo | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:page-backups` | frappe | Automation | workspace_target | Download Backups | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:page-print-format-builder` | frappe | Automation | workspace_target | Print Format Builder | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:tools:page-print-format-builder-beta` | frappe | Automation | workspace_target | Print Format Builder (New) | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:chart-login` | frappe | Core | workspace_target | Login | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:doctype-access-log` | frappe | Core | workspace_target | Access Log | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:doctype-activity-log` | frappe | Core | workspace_target | Activity Log | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:doctype-role-permission-for-page-and-report` | frappe | Core | workspace_target | Role Permission for Page and Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:doctype-user-permission` | frappe | Core | workspace_target | User Permissions | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:number-card-failed-login-attempts` | frappe | Core | workspace_target | Failed Login Attempts | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:number-card-total-website-users` | frappe | Core | workspace_target | Total Website Users | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:number-card-users` | frappe | Core | workspace_target | Users | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:page-permission-manager` | frappe | Core | workspace_target | Role Permissions Manager | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:report-document-share-report` | frappe | Core | workspace_target | Document Share Report | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:users:report-permitted-documents-for-user` | frappe | Core | workspace_target | Permitted Documents For User | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:chart-webpage-views` | frappe | Website | workspace_target | Webpage Views | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:doctype-about-us-settings` | frappe | Website | workspace_target | About Us Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:doctype-contact-us-settings` | frappe | Website | workspace_target | Contact Us Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:doctype-help-article` | frappe | Website | workspace_target | Help Article | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:doctype-help-category` | frappe | Website | workspace_target | Help Category | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:doctype-website-script` | frappe | Website | workspace_target | Website Script | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:doctype-website-settings` | frappe | Website | workspace_target | Website Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:doctype-website-theme` | frappe | Website | workspace_target | Website Theme | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:number-card-published-web-forms` | frappe | Website | workspace_target | Published Web Forms | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:number-card-published-web-pages` | frappe | Website | workspace_target | Published Web Pages | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace-target:website:number-card-website-themes-available` | frappe | Website | workspace_target | Website Themes Available | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `frappe:workspace:build` | frappe | Core | workspace | Build | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `frappe:workspace:integrations` | frappe | Integrations | workspace | Integrations | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `frappe:workspace:tools` | frappe | Automation | workspace | Tools | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `frappe:workspace:users` | frappe | Core | workspace | Users | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `frappe:workspace:website` | frappe | Website | workspace | Website | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `frappe:workspace:welcome-workspace` | frappe | Core | workspace | Welcome Workspace | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `my-store-ui:custom-field:item:item-custom-additional-cost` | my_store_ui | Stock | custom_field | Item-custom_additional_cost | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-product-material` | my_store_ui | Stock | custom_field | Item-custom_product_material | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-product-size` | my_store_ui | Stock | custom_field | Item-custom_product_size | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-purchase-price` | my_store_ui | Stock | custom_field | Item-custom_purchase_price | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-retail-price` | my_store_ui | Stock | custom_field | Item-custom_retail_price | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-retail-profit-percentage` | my_store_ui | Stock | custom_field | Item-custom_retail_profit_percentage | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-sku-prefix` | my_store_ui | Stock | custom_field | Item-custom_sku_prefix | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-supplier` | my_store_ui | Stock | custom_field | Item-custom_supplier | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-total-cost` | my_store_ui | Stock | custom_field | Item-custom_total_cost | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-wholesale-price` | my_store_ui | Stock | custom_field | Item-custom_wholesale_price | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:custom-field:item:item-custom-wholesale-profit-percentage` | my_store_ui | Stock | custom_field | Item-custom_wholesale_profit_percentage | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `my-store-ui:installed-app:my-store-ui` | my_store_ui | my_store_ui | installed_app | my_store_ui | E | Yes | /retail-erp | SPA shell implemented; app feature parity incomplete | Installed app capabilities require classified Retail ERP routes or safe embedding |
| `my-store-ui:page:retail-erp` | my_store_ui | My Store UI | page | retail-erp | C | Yes | /retail-erp | SPA shell implemented; feature coverage partial | Partial modules remain |
| `my-store-ui:page:smart-sales` | my_store_ui | My Store UI | page | smart-sales | C | Yes | — | Not implemented | Required or safe integration route must be designed |
| `posawesome:child-doctype:delivery-charges-pos-profile` | posawesome | POSAwesome | child_doctype | Delivery Charges POS Profile | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-allowed-expense-account` | posawesome | POSAwesome | child_doctype | POS Allowed Expense Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-allowed-source-account` | posawesome | POSAwesome | child_doctype | POS Allowed Source Account | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-awesome-print-format-rule` | posawesome | Posawesome | child_doctype | POS Awesome Print Format Rule | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-closing-shift-detail` | posawesome | POSAwesome | child_doctype | POS Closing Shift Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-closing-shift-taxes` | posawesome | POSAwesome | child_doctype | POS Closing Shift Taxes | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-coupon-detail` | posawesome | POSAwesome | child_doctype | POS Coupon Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-gift-card-redemption` | posawesome | POSAwesome | child_doctype | POS Gift Card Redemption | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-gift-card-transaction` | posawesome | POSAwesome | child_doctype | POS Gift Card Transaction | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-offer-detail` | posawesome | POSAwesome | child_doctype | POS Offer Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-opening-shift-detail` | posawesome | POSAwesome | child_doctype | POS Opening Shift Detail | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:pos-payment-entry-reference` | posawesome | POSAwesome | child_doctype | POS Payment Entry Reference | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:posa-sales-person-filter` | posawesome | POSAwesome | child_doctype | POSA Sales Person Filter | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:child-doctype:sales-invoice-reference` | posawesome | POSAwesome | child_doctype | Sales Invoice Reference | G | No | — | Not implemented | None: excluded from independent frontend routing |
| `posawesome:custom-field:address:address-posa-delivery-charges` | posawesome | Contacts | custom_field | Address-posa_delivery_charges | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:batch:batch-posa-batch-price` | posawesome | Stock | custom_field | Batch-posa_batch_price | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:company:company-posa-auto-referral` | posawesome | Setup | custom_field | Company-posa_auto_referral | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:company:company-posa-column-break-22` | posawesome | Setup | custom_field | Company-posa_column_break_22 | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:company:company-posa-customer-offer` | posawesome | Setup | custom_field | Company-posa_customer_offer | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:company:company-posa-primary-offer` | posawesome | Setup | custom_field | Company-posa_primary_offer | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:company:company-posa-referral-campaign` | posawesome | Setup | custom_field | Company-posa_referral_campaign | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:company:company-posa-referral-section` | posawesome | Setup | custom_field | Company-posa_referral_section | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:customer:customer-posa-birthday` | posawesome | Selling | custom_field | Customer-posa_birthday | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:customer:customer-posa-discount` | posawesome | Selling | custom_field | Customer-posa_discount | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:customer:customer-posa-referral-code` | posawesome | Selling | custom_field | Customer-posa_referral_code | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:customer:customer-posa-referral-company` | posawesome | Selling | custom_field | Customer-posa_referral_company | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:customer:customer-posa-referral-section` | posawesome | Selling | custom_field | Customer-posa_referral_section | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:payment-entry:payment-entry-posa-client-request-id` | posawesome | Accounts | custom_field | Payment Entry-posa_client_request_id | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice-item:pos-invoice-item-posa-delivery-date` | posawesome | Accounts | custom_field | POS Invoice Item-posa_delivery_date | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice-item:pos-invoice-item-posa-is-offer` | posawesome | Accounts | custom_field | POS Invoice Item-posa_is_offer | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice-item:pos-invoice-item-posa-is-replace` | posawesome | Accounts | custom_field | POS Invoice Item-posa_is_replace | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice-item:pos-invoice-item-posa-notes` | posawesome | Accounts | custom_field | POS Invoice Item-posa_notes | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice-item:pos-invoice-item-posa-offer-applied` | posawesome | Accounts | custom_field | POS Invoice Item-posa_offer_applied | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice-item:pos-invoice-item-posa-offers` | posawesome | Accounts | custom_field | POS Invoice Item-posa_offers | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice-item:pos-invoice-item-posa-row-id` | posawesome | Accounts | custom_field | POS Invoice Item-posa_row_id | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-gift-card-redemptions` | posawesome | Accounts | custom_field | POS Invoice-gift_card_redemptions | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-additional-notes-section` | posawesome | Accounts | custom_field | POS Invoice-posa_additional_notes_section | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-authorization-code` | posawesome | Accounts | custom_field | POS Invoice-posa_authorization_code | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-client-request-id` | posawesome | Accounts | custom_field | POS Invoice-posa_client_request_id | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-column-break-111` | posawesome | Accounts | custom_field | POS Invoice-posa_column_break_111 | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-coupons` | posawesome | Accounts | custom_field | POS Invoice-posa_coupons | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-delivery-charges` | posawesome | Accounts | custom_field | POS Invoice-posa_delivery_charges | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-delivery-charges-rate` | posawesome | Accounts | custom_field | POS Invoice-posa_delivery_charges_rate | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-delivery-date` | posawesome | Accounts | custom_field | POS Invoice-posa_delivery_date | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-is-printed` | posawesome | Accounts | custom_field | POS Invoice-posa_is_printed | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-notes` | posawesome | Accounts | custom_field | POS Invoice-posa_notes | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-offers` | posawesome | Accounts | custom_field | POS Invoice-posa_offers | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-pos-opening-shift` | posawesome | Accounts | custom_field | POS Invoice-posa_pos_opening_shift | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-invoice:pos-invoice-posa-return-valid-upto` | posawesome | Accounts | custom_field | POS Invoice-posa_return_valid_upto | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-column-break-anyol` | posawesome | Accounts | custom_field | POS Profile-column_break_anyol | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-column-break-dqsba` | posawesome | Accounts | custom_field | POS Profile-column_break_dqsba | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-column-break-uolvm` | posawesome | Accounts | custom_field | POS Profile-column_break_uolvm | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-create-pos-invoice-instead-of-sales-invoice` | posawesome | Accounts | custom_field | POS Profile-create_pos_invoice_instead_of_sales_invoice | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-custom-allow-create-quotation` | posawesome | Accounts | custom_field | POS Profile-custom_allow_create_quotation | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-custom-allow-select-sales-order` | posawesome | Accounts | custom_field | POS Profile-custom_allow_select_sales_order | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-hide-expected-amount` | posawesome | Accounts | custom_field | POS Profile-hide_expected_amount | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-pos-awesome-payments` | posawesome | Accounts | custom_field | POS Profile-pos_awesome_payments | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-cancel-submitted-cash-movement` | posawesome | Accounts | custom_field | POS Profile-posa_allow_cancel_submitted_cash_movement | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-cash-deposit` | posawesome | Accounts | custom_field | POS Profile-posa_allow_cash_deposit | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-change-posting-date` | posawesome | Accounts | custom_field | POS Profile-posa_allow_change_posting_date | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-create-purchase-items` | posawesome | Accounts | custom_field | POS Profile-posa_allow_create_purchase_items | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-create-purchase-suppliers` | posawesome | Accounts | custom_field | POS Profile-posa_allow_create_purchase_suppliers | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-credit-sale` | posawesome | Accounts | custom_field | POS Profile-posa_allow_credit_sale | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-customer-purchase-order` | posawesome | Accounts | custom_field | POS Profile-posa_allow_customer_purchase_order | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-delete` | posawesome | Accounts | custom_field | POS Profile-posa_allow_delete | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-delete-cancelled-cash-movement` | posawesome | Accounts | custom_field | POS Profile-posa_allow_delete_cancelled_cash_movement | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-delete-offline-invoice` | posawesome | Accounts | custom_field | POS Profile-posa_allow_delete_offline_invoice | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-duplicate-customer-names` | posawesome | Accounts | custom_field | POS Profile-posa_allow_duplicate_customer_names | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-free-batch-return` | posawesome | Accounts | custom_field | POS Profile-posa_allow_free_batch_return | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-line-item-name-override` | posawesome | Accounts | custom_field | POS Profile-posa_allow_line_item_name_override | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-make-new-payments` | posawesome | Accounts | custom_field | POS Profile-posa_allow_make_new_payments | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-mpesa-reconcile-payments` | posawesome | Accounts | custom_field | POS Profile-posa_allow_mpesa_reconcile_payments | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-multi-currency` | posawesome | Accounts | custom_field | POS Profile-posa_allow_multi_currency | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-offline-sale-without-stock-verification` | posawesome | Accounts | custom_field | POS Profile-posa_allow_offline_sale_without_stock_verification | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-partial-payment` | posawesome | Accounts | custom_field | POS Profile-posa_allow_partial_payment | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-pos-expense` | posawesome | Accounts | custom_field | POS Profile-posa_allow_pos_expense | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-price-list-rate-change` | posawesome | Accounts | custom_field | POS Profile-posa_allow_price_list_rate_change | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-print-draft-invoices` | posawesome | Accounts | custom_field | POS Profile-posa_allow_print_draft_invoices | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-print-last-invoice` | posawesome | Accounts | custom_field | POS Profile-posa_allow_print_last_invoice | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-purchase-order` | posawesome | Accounts | custom_field | POS Profile-posa_allow_purchase_order | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-purchase-receipt` | posawesome | Accounts | custom_field | POS Profile-posa_allow_purchase_receipt | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-reconcile-payments` | posawesome | Accounts | custom_field | POS Profile-posa_allow_reconcile_payments | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-return` | posawesome | Accounts | custom_field | POS Profile-posa_allow_return | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-return-without-invoice` | posawesome | Accounts | custom_field | POS Profile-posa_allow_return_without_invoice | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-sales-order` | posawesome | Accounts | custom_field | POS Profile-posa_allow_sales_order | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-select-print-format-in-payments` | posawesome | Accounts | custom_field | POS Profile-posa_allow_select_print_format_in_payments | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-submissions-in-background-job` | posawesome | Accounts | custom_field | POS Profile-posa_allow_submissions_in_background_job | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-supervisor-manage-gift-cards` | posawesome | Accounts | custom_field | POS Profile-posa_allow_supervisor_manage_gift_cards | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-user-to-edit-additional-discount` | posawesome | Accounts | custom_field | POS Profile-posa_allow_user_to_edit_additional_discount | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-user-to-edit-item-discount` | posawesome | Accounts | custom_field | POS Profile-posa_allow_user_to_edit_item_discount | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-user-to-edit-rate` | posawesome | Accounts | custom_field | POS Profile-posa_allow_user_to_edit_rate | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-write-off-change` | posawesome | Accounts | custom_field | POS Profile-posa_allow_write_off_change | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-allow-zero-rated-items` | posawesome | Accounts | custom_field | POS Profile-posa_allow_zero_rated_items | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-apply-customer-discount` | posawesome | Accounts | custom_field | POS Profile-posa_apply_customer_discount | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-auto-set-batch` | posawesome | Accounts | custom_field | POS Profile-posa_auto_set_batch | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-auto-set-delivery-charges` | posawesome | Accounts | custom_field | POS Profile-posa_auto_set_delivery_charges | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-back-office-cash-account` | posawesome | Accounts | custom_field | POS Profile-posa_back_office_cash_account | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-block-sale-beyond-available-qty` | posawesome | Accounts | custom_field | POS Profile-posa_block_sale_beyond_available_qty | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-camera-scan-type` | posawesome | Accounts | custom_field | POS Profile-posa_camera_scan_type | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-cash-mode-of-payment` | posawesome | Accounts | custom_field | POS Profile-posa_cash_mode_of_payment | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-cash-movement-max-amount` | posawesome | Accounts | custom_field | POS Profile-posa_cash_movement_max_amount | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-col-1` | posawesome | Accounts | custom_field | POS Profile-posa_col_1 | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-column-break-112` | posawesome | Accounts | custom_field | POS Profile-posa_column_break_112 | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-create-only-sales-order` | posawesome | Accounts | custom_field | POS Profile-posa_create_only_sales_order | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-decimal-precision` | posawesome | Accounts | custom_field | POS Profile-posa_decimal_precision | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-default-card-view` | posawesome | Accounts | custom_field | POS Profile-posa_default_card_view | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-default-country` | posawesome | Accounts | custom_field | POS Profile-posa_default_country | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-default-expense-account` | posawesome | Accounts | custom_field | POS Profile-posa_default_expense_account | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-default-sales-order` | posawesome | Accounts | custom_field | POS Profile-posa_default_sales_order | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-display-additional-notes` | posawesome | Accounts | custom_field | POS Profile-posa_display_additional_notes | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-display-authorization-code` | posawesome | Accounts | custom_field | POS Profile-posa_display_authorization_code | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-display-discount-amount` | posawesome | Accounts | custom_field | POS Profile-posa_display_discount_amount | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-display-discount-percentage` | posawesome | Accounts | custom_field | POS Profile-posa_display_discount_percentage | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-display-item-code` | posawesome | Accounts | custom_field | POS Profile-posa_display_item_code | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-display-items-in-stock` | posawesome | Accounts | custom_field | POS Profile-posa_display_items_in_stock | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-enable-camera-scanning` | posawesome | Accounts | custom_field | POS Profile-posa_enable_camera_scanning | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-enable-cash-movement` | posawesome | Accounts | custom_field | POS Profile-posa_enable_cash_movement | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-enable-return-validity` | posawesome | Accounts | custom_field | POS Profile-posa_enable_return_validity | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-fetch-coupon` | posawesome | Accounts | custom_field | POS Profile-posa_fetch_coupon | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-force-price-from-customer-price-list` | posawesome | Accounts | custom_field | POS Profile-posa_force_price_from_customer_price_list | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-force-reload-items` | posawesome | Accounts | custom_field | POS Profile-posa_force_reload_items | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-force-server-items` | posawesome | Accounts | custom_field | POS Profile-posa_force_server_items | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-gift-card-liability-account` | posawesome | Accounts | custom_field | POS Profile-posa_gift_card_liability_account | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-hide-closing-shift` | posawesome | Accounts | custom_field | POS Profile-posa_hide_closing_shift | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-hide-variants-items` | posawesome | Accounts | custom_field | POS Profile-posa_hide_variants_items | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-input-qty` | posawesome | Accounts | custom_field | POS Profile-posa_input_qty | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-language` | posawesome | Accounts | custom_field | POS Profile-posa_language | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-local-storage` | posawesome | Accounts | custom_field | POS Profile-posa_local_storage | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-max-discount-allowed` | posawesome | Accounts | custom_field | POS Profile-posa_max_discount_allowed | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-new-line` | posawesome | Accounts | custom_field | POS Profile-posa_new_line | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-open-print-in-new-tab` | posawesome | Accounts | custom_field | POS Profile-posa_open_print_in_new_tab | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-pos-awesome-advance-settings` | posawesome | Accounts | custom_field | POS Profile-posa_pos_awesome_advance_settings | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-pos-awesome-settings` | posawesome | Accounts | custom_field | POS Profile-posa_pos_awesome_settings | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-print-format-rules` | posawesome | Accounts | custom_field | POS Profile-posa_print_format_rules | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-require-cash-movement-remarks` | posawesome | Accounts | custom_field | POS Profile-posa_require_cash_movement_remarks | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-return-validity-days` | posawesome | Accounts | custom_field | POS Profile-posa_return_validity_days | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-sales-persons` | posawesome | Accounts | custom_field | POS Profile-posa_sales_persons | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-search-batch-no` | posawesome | Accounts | custom_field | POS Profile-posa_search_batch_no | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-search-limit` | posawesome | Accounts | custom_field | POS Profile-posa_search_limit | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-search-serial-no` | posawesome | Accounts | custom_field | POS Profile-posa_search_serial_no | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-section-cash-movement` | posawesome | Accounts | custom_field | POS Profile-posa_section_cash_movement | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-section-inventory-controls` | posawesome | Accounts | custom_field | POS Profile-posa_section_inventory_controls | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-section-pricing-controls` | posawesome | Accounts | custom_field | POS Profile-posa_section_pricing_controls | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-section-print-delivery` | posawesome | Accounts | custom_field | POS Profile-posa_section_print_delivery | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-section-sales-purchase` | posawesome | Accounts | custom_field | POS Profile-posa_section_sales_purchase | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-section-sales-returns` | posawesome | Accounts | custom_field | POS Profile-posa_section_sales_returns | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-server-cache-duration` | posawesome | Accounts | custom_field | POS Profile-posa_server_cache_duration | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-show-custom-name-marker-on-print` | posawesome | Accounts | custom_field | POS Profile-posa_show_custom_name_marker_on_print | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-show-customer-balance` | posawesome | Accounts | custom_field | POS Profile-posa_show_customer_balance | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-show-template-items` | posawesome | Accounts | custom_field | POS Profile-posa_show_template_items | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-silent-print` | posawesome | Accounts | custom_field | POS Profile-posa_silent_print | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-smart-reload-mode` | posawesome | Accounts | custom_field | POS Profile-posa_smart_reload_mode | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-tax-inclusive` | posawesome | Accounts | custom_field | POS Profile-posa_tax_inclusive | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-use-delivery-charges` | posawesome | Accounts | custom_field | POS Profile-posa_use_delivery_charges | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-use-gift-cards` | posawesome | Accounts | custom_field | POS Profile-posa_use_gift_cards | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-use-percentage-discount` | posawesome | Accounts | custom_field | POS Profile-posa_use_percentage_discount | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-use-pos-awesome-payments` | posawesome | Accounts | custom_field | POS Profile-posa_use_pos_awesome_payments | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-posa-use-server-cache` | posawesome | Accounts | custom_field | POS Profile-posa_use_server_cache | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-pose-use-limit-search` | posawesome | Accounts | custom_field | POS Profile-pose_use_limit_search | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-use-cashback` | posawesome | Accounts | custom_field | POS Profile-use_cashback | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-profile:pos-profile-use-customer-credit` | posawesome | Accounts | custom_field | POS Profile-use_customer_credit | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-settings:pos-settings-posa-enable-return-validity` | posawesome | Accounts | custom_field | POS Settings-posa_enable_return_validity | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:pos-settings:pos-settings-posa-return-validity-days` | posawesome | Accounts | custom_field | POS Settings-posa_return_validity_days | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-item:sales-invoice-item-name-overridden` | posawesome | Accounts | custom_field | Sales Invoice Item-name_overridden | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-item:sales-invoice-item-posa-delivery-date` | posawesome | Accounts | custom_field | Sales Invoice Item-posa_delivery_date | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-item:sales-invoice-item-posa-is-offer` | posawesome | Accounts | custom_field | Sales Invoice Item-posa_is_offer | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-item:sales-invoice-item-posa-is-replace` | posawesome | Accounts | custom_field | Sales Invoice Item-posa_is_replace | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-item:sales-invoice-item-posa-notes` | posawesome | Accounts | custom_field | Sales Invoice Item-posa_notes | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-item:sales-invoice-item-posa-offer-applied` | posawesome | Accounts | custom_field | Sales Invoice Item-posa_offer_applied | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-item:sales-invoice-item-posa-offers` | posawesome | Accounts | custom_field | Sales Invoice Item-posa_offers | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-item:sales-invoice-item-posa-row-id` | posawesome | Accounts | custom_field | Sales Invoice Item-posa_row_id | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice-reference:sales-invoice-reference-pos-invoice` | posawesome | POSAwesome | custom_field | Sales Invoice Reference-pos_invoice | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-gift-card-redemptions` | posawesome | Accounts | custom_field | Sales Invoice-gift_card_redemptions | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-additional-notes-section` | posawesome | Accounts | custom_field | Sales Invoice-posa_additional_notes_section | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-authorization-code` | posawesome | Accounts | custom_field | Sales Invoice-posa_authorization_code | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-client-request-id` | posawesome | Accounts | custom_field | Sales Invoice-posa_client_request_id | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-column-break-111` | posawesome | Accounts | custom_field | Sales Invoice-posa_column_break_111 | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-coupons` | posawesome | Accounts | custom_field | Sales Invoice-posa_coupons | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-delivery-charges` | posawesome | Accounts | custom_field | Sales Invoice-posa_delivery_charges | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-delivery-charges-rate` | posawesome | Accounts | custom_field | Sales Invoice-posa_delivery_charges_rate | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-delivery-date` | posawesome | Accounts | custom_field | Sales Invoice-posa_delivery_date | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-is-printed` | posawesome | Accounts | custom_field | Sales Invoice-posa_is_printed | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-notes` | posawesome | Accounts | custom_field | Sales Invoice-posa_notes | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-offers` | posawesome | Accounts | custom_field | Sales Invoice-posa_offers | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-pos-opening-shift` | posawesome | Accounts | custom_field | Sales Invoice-posa_pos_opening_shift | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-invoice:sales-invoice-posa-return-valid-upto` | posawesome | Accounts | custom_field | Sales Invoice-posa_return_valid_upto | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-order-item:sales-order-item-posa-notes` | posawesome | Selling | custom_field | Sales Order Item-posa_notes | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-order-item:sales-order-item-posa-row-id` | posawesome | Selling | custom_field | Sales Order Item-posa_row_id | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-order:sales-order-posa-additional-notes-section` | posawesome | Selling | custom_field | Sales Order-posa_additional_notes_section | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-order:sales-order-posa-coupons` | posawesome | Selling | custom_field | Sales Order-posa_coupons | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-order:sales-order-posa-notes` | posawesome | Selling | custom_field | Sales Order-posa_notes | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:sales-order:sales-order-posa-offers` | posawesome | Selling | custom_field | Sales Order-posa_offers | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:custom-field:user:user-posa-pos-pin` | posawesome | Core | custom_field | User-posa_pos_pin | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:doctype:delivery-charges` | posawesome | POSAwesome | doctype | Delivery Charges | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:mpesa-c2b-register-url` | posawesome | POSAwesome | doctype | Mpesa C2B Register URL | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:mpesa-payment-register` | posawesome | POSAwesome | doctype | Mpesa Payment Register | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:pos-cash-movement` | posawesome | POSAwesome | doctype | POS Cash Movement | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:pos-closing-shift` | posawesome | POSAwesome | doctype | POS Closing Shift | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:pos-coupon` | posawesome | POSAwesome | doctype | POS Coupon | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:pos-gift-card` | posawesome | POSAwesome | doctype | POS Gift Card | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:pos-invoice-submission-ledger` | posawesome | POSAwesome | doctype | POS Invoice Submission Ledger | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:pos-offer` | posawesome | POSAwesome | doctype | POS Offer | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:pos-opening-shift` | posawesome | POSAwesome | doctype | POS Opening Shift | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:referral-code` | posawesome | POSAwesome | doctype | Referral Code | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:doctype:scale-barcode-settings` | posawesome | POSAwesome | doctype | Scale Barcode Settings | A | Yes | — | Not implemented | Required for ordinary-user parity |
| `posawesome:document-action:pos-closing-shift:make-closing-shift-from-opening` | posawesome | POSAwesome | document_action | Make Closing Shift From Opening | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `posawesome:document-action:pos-closing-shift:submit-closing-shift` | posawesome | POSAwesome | document_action | Submit Closing Shift | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `posawesome:document-action:pos-coupon:add-edit-coupon-conditions` | posawesome | POSAwesome | document_action | Add/Edit Coupon Conditions | B | Yes | — | Not implemented | Action not implemented in Retail ERP |
| `posawesome:installed-app:posawesome` | posawesome | posawesome | installed_app | posawesome | F | Yes | — | Not implemented | Installed app capabilities require classified Retail ERP routes or safe embedding |
| `posawesome:page:pos` | posawesome | POSAwesome | page | pos | F | Yes | — | Not implemented | Required or safe integration route must be designed |
| `posawesome:page:posapp` | posawesome | POSAwesome | page | posapp | F | Yes | — | Not implemented | Required or safe integration route must be designed |
| `posawesome:property-setter:pos-invoice:pos-invoice-posa-pos-opening-shift-no-copy` | posawesome | Accounts | property_setter | POS Invoice-posa_pos_opening_shift-no_copy | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:property-setter:sales-invoice-reference:sales-invoice-reference-sales-invoice-reqd` | posawesome | POSAwesome | property_setter | Sales Invoice Reference-sales_invoice-reqd | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:property-setter:sales-invoice:sales-invoice-posa-pos-opening-shift-no-copy` | posawesome | Accounts | property_setter | Sales Invoice-posa_pos_opening_shift-no_copy | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:property-setter:sales-invoice:sales-invoice-update-outstanding-for-self-default` | posawesome | Accounts | property_setter | Sales Invoice-update_outstanding_for_self-default | E | Yes | — | Not implemented | Customization must be represented by approved Retail ERP schema/administration |
| `posawesome:workspace-target:pos-awesome:doctype-delivery-charges` | posawesome | POSAwesome | workspace_target | Delivery Charges | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-pos-cash-movement` | posawesome | POSAwesome | workspace_target | Cash Movement | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-pos-closing-shift` | posawesome | POSAwesome | workspace_target | Closing Shift | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-pos-coupon` | posawesome | POSAwesome | workspace_target | Coupons | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-pos-gift-card` | posawesome | POSAwesome | workspace_target | Gift Cards | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-pos-invoice-submission-ledger` | posawesome | POSAwesome | workspace_target | Invoice Submission Ledger | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-pos-offer` | posawesome | POSAwesome | workspace_target | Offers | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-pos-opening-shift` | posawesome | POSAwesome | workspace_target | Opening Shift | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-pos-profile` | posawesome | POSAwesome | workspace_target | POS Profile | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-promotional-scheme` | posawesome | POSAwesome | workspace_target | Promotional Schemes | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-referral-code` | posawesome | POSAwesome | workspace_target | Referral Code | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:doctype-scale-barcode-settings` | posawesome | POSAwesome | workspace_target | Scale Barcode Settings | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace-target:pos-awesome:page-posapp` | posawesome | POSAwesome | workspace_target | POS Awesome | C | Yes | — | Not implemented | Target must resolve to a classified Retail ERP feature |
| `posawesome:workspace:pos-awesome` | posawesome | POSAwesome | workspace | POS Awesome | C | Yes | — | Not implemented | Workspace targets require Retail ERP launchers/routes |
| `smj-theme:installed-app:smj-theme` | smj_theme | smj_theme | installed_app | smj_theme | F | Yes | — | Not implemented | Installed app capabilities require classified Retail ERP routes or safe embedding |
| `unknown:print-format:journal-entry:payment-receipt-voucher` | unknown | Printing | print_format | Payment Receipt Voucher | E | Yes | — | Not implemented | Print preview/PDF selector not implemented |
