# Full-Parity Inventory Summary (Stage 1)

- Captured: 2026-07-15 19:10
- Site: `site1.local`
- Canonical source: `docs/erpnext-v15-complete-inventory.json`
- Inventory fingerprint: `abc8d8130154fd6f75da36ff342915eb2d9050f53c7233de1052f56245395cc4`

## Headline counts

| Metric | Value |
|---|---:|
| Total atomic features | 2841 |
| User-facing features | 2482 |
| System-internal exclusions | 359 |
| Currently mapped (has custom route) | 788 |
| Unmapped user-facing | 1694 |
| Strict route coverage | 31.75% |
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
| Accounts | 414 |
| Stock | 191 |
| Core | 153 |
| Selling | 112 |
| Manufacturing | 91 |
| Buying | 85 |
| Desk | 81 |
| (none) | 68 |
| Setup | 62 |
| CRM | 54 |
| Website | 52 |
| Integrations | 35 |
| Assets | 31 |
| Automation | 31 |
| Subcontracting | 25 |
| Email | 25 |
| Projects | 22 |
| POSAwesome | 22 |
| Custom | 20 |
| ERPNext Integrations | 19 |
| Support | 13 |
| Maintenance | 9 |
| Printing | 9 |
| Contacts | 8 |
| ERPNext Gemini Integration | 8 |

