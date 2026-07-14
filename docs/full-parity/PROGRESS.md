# Full Feature Parity — Progress

_Last updated: 2026-07-14 (batch: print formats)_

## Headline metrics

| Metric | Starting | Current |
|---|---:|---:|
| User-facing capabilities (source of truth) | 2482 | 2482 |
| Unmapped user-facing (route-based strict audit) | 2396 | **1746** |
| Currently routed features | 86 | **736** |
| Strict route coverage | 3.46% | **29.65%** |
| Authoritative registry entries | 0 | **2482** |

_Batch "generated DocType masters": added 116 in-scope standard parent DocTypes to
`ENTITY_ROUTES`, genuinely served by the universal metadata engine (verified
server-side: 170 served / 0 failures). Fixed a universal list-engine `KeyError`
that crashed doctypes whose default columns include text/hidden fields. Ledger/
system tables, single Settings/Tools and the POS family were intentionally
excluded. All 116 are `generated_provisional` (route + engine work; behavioural
browser/role verification still pending)._

> The route-based strict audit is intentionally unchanged: this batch added the
> authoritative registry and the Stage 0–2 capture without inventing any routes.
> Reducing `unmapped_user_facing` by mass-assigning routes would be the exact
> "fake parity" the mission forbids. Real coverage advances only as features are
> genuinely implemented and verified.

## Authoritative registry — status distribution (of 2482 user-facing)

| Status | Count |
|---|---:|
| implemented_unverified | 99 |
| generated_provisional | 77 |
| special_adapter (mapped actions on handcrafted docs) | 93 |
| verified_complete | 0 |
| blocked | 0 |
| unavailable_with_reason (planned; Desk owns it) | 897 |
| not_required (out of wholesale scope) | 197 |
| internal (fields, property setters, workspace links, platform) | 1212 |

Note: `special_adapter` (93) overlaps the `implemented_unverified`/document-action
buckets in strategy terms; see `inventory/parity_registry_summary.md` for the
strategy breakdown. "Implemented in some form" total: **176**.

## Business priority distribution

| Priority | Count |
|---|---:|
| P0_go_live | 54 |
| P1_required | 1290 |
| P2_important | 255 |
| P3_optional | 359 |
| not_required | 259 |
| internal | 265 |

## Verification state

| Check | Result |
|---|---|
| Vue build (`npm run build`, `npm run check`) | PASS |
| Registry validation (`validate_parity_registry`) | PASS (0 errors) |
| Registry tests (`test_parity_registry`, standalone) | PASS (7/7) |
| Frappe test suite (`run-tests`) | BLOCKED — `allow_tests` disabled on site1.local |
| Browser verification | UNAVAILABLE — no Chrome/Chromium/Playwright/Cypress/Selenium |
| Live wholesale flow (reservation/credit) | NOT IMPLEMENTED — gated on approvals |

## Current commit chain (branch `full-feature-parity`)

- `chore: capture starting state for full feature parity`
- `chore: capture current complete feature inventory`
- `feat: establish authoritative full parity registry`
- `docs: full-parity tracking, blockers and approval proposals` (this batch)

## Completed batch

Stage 0 (checkpoint), Stage 1 (live inventory capture), Stage 2 (authoritative
registry + validation tests), Stage 12 tracking docs, Stage 6 approval proposals.

## Next batch (BLOCKED on approvals — see BLOCKERS.md)

1. Stock reservation + Available-to-Sell (needs `enable_stock_reservation` + policy).
2. Customer Credit/Non-Credit model (needs Custom Fields).
3. Wholesale Transaction ID / register (needs Custom Fields).
4. End-to-end regression on an approved test site (needs `allow_tests` / staging site).

Independent, non-gated implementation (generic-engine hardening for in-scope
masters/reports) can proceed in parallel but cannot be marked `verified_complete`
until a test/browser environment exists.
