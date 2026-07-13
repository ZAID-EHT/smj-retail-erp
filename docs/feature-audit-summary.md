# Feature audit summary

This audit is a discovery baseline, not a parity claim. The automated parity check currently fails until every permitted user-facing feature has a tested Retail ERP implementation or an evidence-backed exclusion.

## Required totals

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
| Previous Matrix Rows Observed | 104 |
| Missing Features Added | 2052 |
| Duplicate Rows Detected | 0 |
| Specialized Interfaces | 1481 |
| Generic Engine Features | 249 |
| Installed App Features | 244 |
| Remaining Desk Dependencies | 2482 |
| Unclassified Features | 0 |
| Features Total | 2841 |

## Automated parity audit

Result: **FAIL**

| Failure class | Count |
|---|---:|
| Unclassified User Facing | 0 |
| Unmapped User Facing | 2477 |
| Undocumented Actions | 0 |
| Complete Without Tests | 0 |
| Unhandled Active Workflows | 0 |

## Universal generated UX review (2026-07-13)

The shared generated list, form and detail engines now use the Retail ERP
presentation system, bounded primary filters, a More Filters drawer, active
chips, column preferences, grouped forms, responsive cards, collaboration
adapters and standard Frappe print discovery. The 20 provisional DocTypes all
passed Administrator list/configuration smoke checks. The existing
non-Administrator user could read 17; Department, Project and UOM were denied
by current permissions. Guest access remained denied.

Graduated to `generated_complete`: **0**. All 20 remain provisional because
per-feature collaboration writes and interactive browser viewport checks are
incomplete, and protected PDF output cannot be visually verified while
`wkhtmltopdf` is missing. This UX work does not reduce the strict unmapped count
or inflate the approximately 19% project-wide strict completion estimate.

## Reconciliation

- User-supplied previous matrix count: **98**.
- Observed hand-authored rows before generation: **104**.
- Machine-discovered user-facing features not represented by the hand-authored matrix: **2052**.
- Exact duplicate legacy rows detected: **0**.
- Existing manual rows were preserved. The generated appendix is canonical for completeness checks.

### Representation by discovered feature type

| Feature type | Total | Already represented | Missing user-facing | Excluded |
|---|---:|---:|---:|---:|
| Child Doctype | 335 | 2 | 0 | 335 |
| Client Script | 1 | 0 | 1 | 0 |
| Custom Field | 212 | 0 | 212 | 0 |
| Dashboard | 9 | 7 | 2 | 0 |
| Dashboard Chart | 49 | 5 | 44 | 0 |
| Dashboard Connection | 68 | 0 | 68 | 0 |
| Doctype | 467 | 76 | 376 | 15 |
| Document Action | 634 | 132 | 502 | 0 |
| Installed App | 7 | 1 | 6 | 0 |
| Notification | 4 | 0 | 2 | 2 |
| Number Card | 50 | 1 | 49 | 0 |
| Page | 22 | 3 | 19 | 0 |
| Platform Capability | 16 | 3 | 13 | 0 |
| Print Format | 44 | 2 | 38 | 4 |
| Property Setter | 101 | 0 | 101 | 0 |
| Report | 198 | 22 | 175 | 1 |
| Source Only Report | 2 | 0 | 0 | 2 |
| Workspace | 25 | 16 | 9 | 0 |
| Workspace Target | 597 | 162 | 435 | 0 |

### Implementation classification

| Class | Meaning | Count |
|---|---|---:|
| A | Generic list/detail/form engine | 249 |
| B | Specialized transaction interface | 662 |
| C | Specialized visual view | 819 |
| D | Report engine | 200 |
| E | Administrative interface | 554 |
| F | Safe embedded integration | 7 |
| G | System-internal and not user-facing | 350 |

## Rerun commands

```bash
bench --site site1.local execute my_store_ui.audit.feature_inventory.generate_complete_inventory
bench --site site1.local execute my_store_ui.audit.feature_inventory.audit_feature_parity
```

The first command refreshes all generated documents. The second intentionally exits non-zero until the parity contract is met.

## Discovery limitations requiring implementation-time review

- Source action discovery identifies whitelisted controller actions and custom buttons, but complex runtime conditions and dynamically constructed buttons still require controller-specific review.
- Disabled/domain-restricted features remain inventoried; their runtime visibility depends on current user permissions, domains, module profiles and settings.
- Child DocTypes are classified as non-independent routes, not discarded; they remain attached to parent form requirements.
- Workspace blocks are resolved from stored content where target metadata is explicit. Unresolved blocks remain in the unmapped report.
