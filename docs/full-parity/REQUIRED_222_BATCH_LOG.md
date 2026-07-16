# Required-222 Batch Log

Every count below was verified by running
`my_store_ui.audit.parity_registry.corrected_production_parity_audit()`.

| # | Batch | Gap before → after | Commit |
|---|---|---:|---|
| 0 | Verified branch/worktree/baseline and created recovery tag | 222 | `ee4fbf4`; tag `pre-complete-required-222-20260716-2109` |
| 1 | 28 Dashboard Charts, 25 Number Cards and 6 Dashboards using live permission-checked data | 222 → 163 | `55a4d3e` |
| 2 | Generic permission-filtered dashboard Connections; dead-credit and duplicate Supplier-key correction | 163 → 144 | `7f2aae1` |
| 3 | Bank Clearance controller adapter, Pegged Currencies editor and Single-DocType loading | 144 → 140 | `8201749` |
| 4 | Sales Funnel and Warehouse Capacity Summary analytics pages | 140 → 138 | `264a151` |
| 5 | Buying actions and mappings | 138 → 115 | `c3973ac` |
| 6 | Accounts, payment, banking, share and subscription actions | 115 → 69 | `3bbbedf` |
| 7 | Stock, Material Request, Pick List, Purchase Receipt, SABB and reconciliation actions | 69 → 36 | `b64aecc` |
| 8 | CRM, Selling, Setup, Contacts, Printing and Maintenance actions; final helper classifications | 36 → **0** | `325527b` |

Final generated audit fingerprint:
`029f8e0d2a940f071d20a66010f820fbd8083401ae4eae6f906f0a909b0562d0`.

Final corrected result:

- `required_but_missing = 0`
- `unclassified = 0`
- `verified_complete = 0`
- `implemented_unverified = 469`
- `generated_provisional = 805`

No capability was credited with an empty route or arbitrary-method RPC. Where
the scanner attributed an internal helper to the wrong parent DocType, the
registry records a source-specific explanation. Regional and platform-only
behaviour remains explicitly classified rather than presented as a fake Retail
ERP action.

Verification was performed against `site1.local`, with focused suites run in
isolated Frappe processes where older test modules call `frappe.destroy()`.
Browser verification remains unavailable and is not claimed.
