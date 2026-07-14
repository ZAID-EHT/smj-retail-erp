# Authoritative Parity Registry Summary (Stage 2)

- Source inventory fingerprint: `87b439c3eb8c2d1f210cd791b6a33b1c403ad4a802d5cc2a2ba3e963241a32b6`
- Registry entries (one per user-facing feature): **2482**
- Validation: **PASS** (0 errors)
- Implemented in some form (custom/provisional/adapter/unverified): **829**

> A route alone is never counted as completion. `unavailable_with_reason`, `not_required` and `internal` are NOT implemented functionality.

## By status

| Status | Meaning | Count |
|---|---|---:|
| generated_provisional | Generic engine exposes it; specialised behaviour unverified | 728 |
| implemented_unverified | Implemented, lacks browser/role/business verification | 101 |
| internal | Technical/internal, no user route required | 858 |
| not_required | Not needed for this business | 175 |
| unavailable_with_reason | Inventoried, intentionally not yet available (planned) | 620 |

## By business priority

| Priority | Meaning | Count |
|---|---|---:|
| P0_go_live | Blocks the fixed wholesale go-live flow | 54 |
| P1_required | Required before client go-live | 1290 |
| P2_important | Important, not day-one blocking | 255 |
| P3_optional | Optional / after go-live | 359 |
| internal | Technical component, not a user route | 265 |
| not_required | Outside the wholesale importing/selling scope | 259 |

## By implementation strategy

| Strategy | Count |
|---|---:|
| custom_override | 6 |
| generated_dashboard | 92 |
| generated_doctype | 519 |
| generated_print | 27 |
| generated_report | 186 |
| internal | 858 |
| not_required | 175 |
| special_adapter | 95 |
| unavailable_with_reason | 524 |

## Reproduce / validate

```bash
bench --site site1.local execute my_store_ui.audit.parity_registry.generate
bench --site site1.local execute my_store_ui.audit.parity_registry.validate_parity_registry
```

