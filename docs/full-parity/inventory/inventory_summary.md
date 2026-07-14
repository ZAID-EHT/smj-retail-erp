# Full-Parity Inventory Summary (Stage 1)

- Captured: 2026-07-14 12:07
- Site: `site1.local`
- Canonical source: `docs/erpnext-v15-complete-inventory.json`
- Inventory fingerprint: `c88223dfd99f9f658a6c25a0225d7bcab1a357c5364433d24d6ca72434fa3a22`

## Headline counts

| Metric | Value |
|---|---:|
| Total atomic features | 2841 |
| User-facing features | 2482 |
| System-internal exclusions | 359 |
| Currently mapped (has custom route) | 709 |
| Unmapped user-facing | 1773 |
| Strict route coverage | 28.57% |
| Generic engine candidates (class A) | 249 |
| Specialised interfaces (class B+C) | 1481 |
| Installed non-core app features | 244 |
| Strict audit status | **FAIL** |

## User-facing features by application

| Application | User-facing features |
|---|---:|
| erpnext | 1681 |
| frappe | 434 |
| posawesome | 215 |
| custom | 122 |
| my_store_ui | 14 |
| erpnext_gemini_integration | 11 |
| erpnext_chatgpt | 3 |
| smj_theme | 1 |
| unknown | 1 |

## User-facing features by type

| Feature type | Count |
|---|---:|
| document_action | 634 |
| workspace_target | 597 |
| doctype | 452 |
| custom_field | 212 |
| report | 197 |
| property_setter | 101 |
| dashboard_connection | 68 |
| number_card | 50 |
| dashboard_chart | 49 |
| print_format | 40 |
| workspace | 25 |
| page | 22 |
| platform_capability | 16 |
| dashboard | 9 |
| installed_app | 7 |
| notification | 2 |
| client_script | 1 |

## User-facing features by implementation class

| Class | Meaning | User-facing count |
|---|---|---:|
| A | Generic list/detail/form engine | 249 |
| B | Specialized transaction interface | 662 |
| C | Specialized visual view | 819 |
| D | Report engine | 197 |
| E | Administrative interface | 548 |
| F | Safe embedded integration | 7 |
| G | System-internal (not user-facing) | 0 |

## Top modules by unmapped user-facing features

| Module | Unmapped |
|---|---:|
| Accounts | 437 |
| Stock | 196 |
| Core | 154 |
| Selling | 118 |
| Manufacturing | 91 |
| Buying | 89 |
| Setup | 81 |
| Desk | 81 |
| (none) | 68 |
| CRM | 54 |
| Website | 52 |
| Integrations | 35 |
| Automation | 32 |
| POSAwesome | 32 |
| Assets | 31 |
| Subcontracting | 25 |
| Email | 25 |
| Projects | 22 |
| Custom | 20 |
| ERPNext Integrations | 19 |
| Printing | 16 |
| Support | 13 |
| Contacts | 9 |
| Maintenance | 9 |
| ERPNext Gemini Integration | 8 |

