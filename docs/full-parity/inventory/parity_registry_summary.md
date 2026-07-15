# Authoritative Parity Registry Summary (Stage 2)

- Source inventory fingerprint: `abc8d8130154fd6f75da36ff342915eb2d9050f53c7233de1052f56245395cc4`
- Registry entries (one per user-facing feature): **2482**
- Validation: **PASS** (0 errors)
- Implemented in some form (custom/provisional/adapter/unverified): **987**

> A route alone is never counted as completion. `unavailable_with_reason`, `not_required` and `internal` are NOT implemented functionality.

## By status

| Status | Meaning | Count |
|---|---|---:|
| generated_provisional | Generic engine exposes it; specialised behaviour unverified | 790 |
| implemented_unverified | Implemented, lacks browser/role/business verification | 197 |
| internal | Technical/internal, no user route required | 976 |
| not_required | Not needed for this business | 181 |
| unavailable_with_reason | Inventoried, intentionally not yet available (planned) | 338 |

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
| external_app_adapter | 22 |
| generated_dashboard | 73 |
| generated_doctype | 570 |
| generated_print | 36 |
| generated_report | 184 |
| internal | 976 |
| not_required | 181 |
| special_adapter | 168 |
| unavailable_with_reason | 265 |

## Reproduce / validate

```bash
bench --site site1.local execute my_store_ui.audit.parity_registry.generate
bench --site site1.local execute my_store_ui.audit.parity_registry.validate_parity_registry
```

