# Authoritative Parity Registry Summary (Stage 2)

- Source inventory fingerprint: `c8cab9468d2eb48aa5f29f2a7a570c096f78366e60502a59c22c3fc5dcb17d14`
- Registry entries (one per user-facing feature): **2482**
- Validation: **PASS** (0 errors)
- Implemented in some form (custom/provisional/adapter/unverified): **176**

> A route alone is never counted as completion. `unavailable_with_reason`, `not_required` and `internal` are NOT implemented functionality.

## By status

| Status | Meaning | Count |
|---|---|---:|
| generated_provisional | Generic engine exposes it; specialised behaviour unverified | 77 |
| implemented_unverified | Implemented, lacks browser/role/business verification | 99 |
| internal | Technical/internal, no user route required | 1212 |
| not_required | Not needed for this business | 197 |
| unavailable_with_reason | Inventoried, intentionally not yet available (planned) | 897 |

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
| generated_doctype | 51 |
| generated_report | 164 |
| internal | 1212 |
| not_required | 197 |
| special_adapter | 93 |
| unavailable_with_reason | 667 |

## Reproduce / validate

```bash
bench --site site1.local execute my_store_ui.audit.parity_registry.generate
bench --site site1.local execute my_store_ui.audit.parity_registry.validate_parity_registry
```

