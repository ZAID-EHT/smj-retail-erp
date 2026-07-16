# Authoritative Parity Registry Summary (Stage 2)

- Source inventory fingerprint: `029f8e0d2a940f071d20a66010f820fbd8083401ae4eae6f906f0a909b0562d0`
- Registry entries (one per user-facing feature): **2482**
- Validation: **PASS** (0 errors)
- Implemented in some form (custom/provisional/adapter/unverified): **1274**

> A route alone is never counted as completion. `unavailable_with_reason`, `not_required` and `internal` are NOT implemented functionality.

## By status

| Status | Meaning | Count |
|---|---|---:|
| generated_provisional | Generic engine exposes it; specialised behaviour unverified | 805 |
| implemented_unverified | Implemented, lacks browser/role/business verification | 469 |
| internal | Technical/internal, no user route required | 976 |
| not_required | Not needed for this business | 179 |
| unavailable_with_reason | Inventoried, intentionally not yet available (planned) | 53 |

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
| custom_override | 7 |
| external_app_adapter | 25 |
| generated_dashboard | 14 |
| generated_doctype | 585 |
| generated_print | 36 |
| generated_report | 184 |
| internal | 976 |
| not_required | 179 |
| special_adapter | 437 |
| unavailable_with_reason | 39 |

## Reproduce / validate

```bash
bench --site site1.local execute my_store_ui.audit.parity_registry.generate
bench --site site1.local execute my_store_ui.audit.parity_registry.validate_parity_registry
```

