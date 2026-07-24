# SMJ Core Wholesale Workflow — Mission State

**Resumable state.** Machine-readable companion: `SMJ_CORE_WORKFLOW_MISSION_STATE.json`.
Do not rely only on conversation history — update this after every logical batch.

## Repository
- Starting branch: `full-feature-parity`
- Starting commit: `e15c37e`
- Recovery tag: `pre-smj-core-workflow-20260724-1140`
- Test site (all writes): `staging.local`
- Dev site (read-only confirmation only): `site1.local`
- Staging backup taken before write testing: `20260724_114030-staging_local-*` under `sites/staging.local/private/backups/`

## Scope map (prompt phases → this repo)
| Phase | Requirement | Primary code |
|-------|-------------|--------------|
| 1 | Customer-first Smart Sales | `frontend/src/pages/priority/SmartSalesPage.vue`, `my_store_ui/api.py` |
| 2 | Customer-specific pricing | `my_store_ui/api.py` (`get_bootstrap`, new price endpoint), ERPNext pricing engine |
| 3 | Actual/Reserved/Available + concurrency | `my_store_ui/api.py`, `my_store_ui/wholesale/reservation.py` |
| 4 | FIFO valuation | Stock Settings + controlled staging test items |
| 5 | Purchase Order data + workflow | universal form engine + PO metadata |
| 6 | `+ Create` header menu | `frontend/src/components/shell/*`, route registry |
| 7 | Simplified entry forms | `universal/api.py` (`SIMPLE_CREATE_*`), `UniversalFormPage.vue` |
| 8 | User/role/access management | `universal/api.py`, `services/permissions.py` |

## Status
See the JSON file for the authoritative live status. Summary of confirmed
defects found during audit:
1. Customer-first not enforced (Add-to-cart works with no customer).
2. Catalogue pricing is not customer-specific.
3. No available-to-sell recheck on draft Sales Order creation.
4. Reservation losing-side raw deadlock UX (previously documented hardening item).

## Safety invariants held this mission
- Writes only to `staging.local`; `site1.local` business data untouched.
- No `ignore_permissions=True` in endpoints; standard ERPNext controllers only.
- No direct GL/SLE/Bin/outstanding writes; no Vue-side valuation.
- No sudo / killall / pkill / taskkill / Windows Chrome.
