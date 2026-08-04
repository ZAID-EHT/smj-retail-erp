# SMJ Retail ERP — Final Production-Readiness Report

Mission: final production-readiness completion. Date: 2026-07-27.
Branch: `full-feature-parity`. Start commit: `8202289`. Candidate: `2b40c49`.
Recovery tag: `pre-smj-final-readiness-20260726-1848`. Backup:
`20260726_184814-staging_local-*`.

## Phase status (all 16)

| Phase | Status |
|-------|--------|
| 0 Preflight/backup/state | ✅ done |
| 1 Baseline reverify | ✅ 164 → (final 333) green |
| 2 Live two-process concurrency | ✅ verified (no over-reservation) |
| 3 Continuous reservation lifecycle | ✅ verified (invariants hold every step) |
| 4 Wider role-denial matrix | ✅ 7 tests, 9 roles × 10 endpoints |
| 5 Seven Product fields | ✅ implemented + 4 tests |
| 6 P&L opening-stock | ✅ root-caused + reconciled (dry-run); apply held for accountant |
| 7 First-time setup wizard | ✅ code + 6 tests; fresh-site run env-blocked |
| 8 Printing & Branding | ✅ landing + preview + 6 tests |
| 9 Email & Notifications | ✅ status/templates/coverage + 4 tests |
| 10 Data import/export | ✅ allowlisted + 7 tests |
| 11 Finance frontend | ✅ audited — already covered by generated + adapters |
| 12 System health/backups | ✅ read-only dashboard + 5 tests |
| 13 Launch frontend audit | ✅ matrix, no launch-critical gap |
| 14 Acceptance suite (24) | ✅ all have results; 11 original fully verified |
| 15 Full regression | ✅ 333 tests / 42 modules green |
| 16 Six-viewport browser | ✅ 90/90, 0 problems |

## Verification totals
- Backend: **333 tests, 42 modules, 0 failures**.
- Frontend build: **clean**.
- Browser: **90/90** across six viewports (15 pages).

## Environment / external requirements (not code gaps)
1. **MariaDB root password** — needed for isolated QA (`financefix.local`) and
   fresh-install (`freshsetup.local`) sites. Mitigated with savepoint reconciliation
   and controller-level testing.
2. **SMTP credentials** — email delivery. System usable via admin-set passwords.
3. **Accountant sign-off** — the opening-stock reclassification booking.
4. **Hetzner / DNS** — deployment.

## Ordinary remaining development (not launch-critical)
- Two-company end-to-end separation test on a fresh site.
- Live second-session session-revocation demonstration.
- Scheduled reports; storefront/integrations (not needed for wholesale launch).

## Safety confirmations
- `site1.local` never written.
- No direct GL/SLE/Bin/outstanding writes; opening-stock correction is a standard JE.
- No permission bypass; no `ignore_permissions` in endpoints.
- No credentials committed; test credentials generated per run, never persisted.
- No Windows Chrome; browser closed via Playwright API; no process killed by name.
- Backups exist; rollback tag + backup recorded.
- Staging clean: no residual test users/items/companies; three empty test warehouses
  disabled (cannot hard-delete due to cancelled-SLE history — purging SLEs is forbidden).

## Status ladder (precise — no overstatement)

| Item | State |
|------|-------|
| Code implemented | ✅ |
| Backend verified (333+ tests) | ✅ |
| Browser verified (90/90, 6 viewports) | ✅ |
| Financial correction **designed** | ✅ |
| Financial correction **QA-tested (dry-run / savepoint)** | ✅ reconciles to 4,048,006 |
| Financial correction **applied** | ❌ not applied — held for accountant sign-off |
| **Accountant approved** | ❌ external |
| Fresh-site **code** verified (savepoint/controller) | ✅ |
| Fresh-site **on a physically empty site** | ❌ external (MariaDB root) |
| SMTP configured | ❌ external |
| Hetzner rehearsal deployed | ❌ external (package prepared) |
| Client UAT completed | ❌ external |
| Production live | ❌ external |

## Verdict
**Code-complete release candidate awaiting accountant-approved financial
reclassification, genuine fresh-install verification (needs MariaDB root), SMTP
configuration, deployment rehearsal and client UAT.** No launch-critical *development*
item remains open; the outstanding items are external (credentials, accountant, DNS).
The opening-stock correction is designed and QA-verified (dry-run reconciles to
4,048,006) but **not applied** — it is a draft awaiting sign-off.

---

## RC4 update (2026-07-27, tag v1.0.0-rc4, commit b527b04)

Added and verified locally: two-company end-to-end separation (8 tests),
Administration landing + navigation, secure PDF download, scheduled-report
management, and a **truthful launch-readiness dashboard** (`/admin/readiness`).
**369 backend tests, 0 failures; browser 96/96; secret scan clean; site1 untouched.**

Status unchanged where external: accountant approval (finance JE not applied), SMTP,
MariaDB root (fresh site), Hetzner/DNS, client UAT. The launch-readiness dashboard
now reports each of these truthfully in-app.

---

# Wholesale Operations Update — v1.0.0-rc8 (2026-08-01)

Branch `full-feature-parity`. Mission base `8311990`. Recovery tag
`pre-smj-wholesale-operations-20260801-1121`. Backup
`20260801_112204-staging_local-*`.

## What is implemented and locally verified

The complete wholesale chain runs on standard ERPNext controllers and mappings. No
GL Entry, Stock Ledger Entry, Payment Ledger Entry or Bin row is written directly
anywhere in the application.

**Sales.** Customer -> Smart Sales (Price Category pricing, Unit or Carton,
Available-to-Sell) -> Sales Order -> reservation -> payment or credit approval ->
FIFO Delivery Note -> final Sales Invoice with advance allocation -> payment
allocation -> completion. Reservation reduces Available-to-Sell, never physical
stock; delivery reduces physical stock once, through the standard Stock Ledger.
Non-Credit customers are gated on real payment, with a manager override that records
an audited reason. Credit is defended twice: ERPNext refuses to submit an over-limit
order, and the delivery gate covers arrears and limit breaches afterwards.

**Purchasing.** Purchase Order -> (partial) Purchase Receipt with batch creation ->
Purchase Invoice -> supplier payment. Landed Cost Vouchers apply freight, customs and
clearing to valuation through the standard voucher. Supplier returns produce a Return
Purchase Receipt and Debit Note.

**Returns.** Return Delivery Note restores stock; the Credit Note reduces the
receivable. Reason is mandatory, quantities are protected against over-return, and
duplicates are refused.

**Visibility.** Transaction register (delivery, invoice, payment, return and
reservation status; eleven filters; lifecycle timeline) and a daily operations
dashboard across sales, inventory, purchasing and finance. Financial figures are
withheld server-side from users without a finance role.

## Evidence

| Check | Result |
|---|---|
| Backend suite | 540 tests, 0 failures, 6 skipped |
| New tests this mission | +140 |
| End-to-end acceptance scenarios | 14, all green |
| Frontend production build | clean |
| Browser matrix | 162/162 across six viewports, zero console errors |
| Secret scan | clean |
| site1.local integrity | fingerprint identical to pre-mission baseline |

The 6 skips are environmental: staging.local has a single Company, so cross-company
warehouse cases skip there. Cross-company separation is covered by suites that create
their own second company.

## Known limitation in the test environment

`bench schedule` and `bench worker` run against the same database as the test suite on
this bench. During a ~7-minute full run this produced MariaDB deadlocks (error 1213) in
one module on one occasion. That module passes in isolation and the whole suite passed
clean on re-run, so it is contention, not a defect. Workers were deliberately left
running (no process is killed by name).

## Remaining ordinary development (not blockers)

- A dedicated replenishment screen. Re-Stock Qty already writes a standard Item Reorder
  row, which drives ERPNext's own reorder process.
- Frontend surfaces for some newly added backend endpoints (delivery preparation,
  landed cost). The register, dashboard and existing document pages cover the primary
  flows and are browser-verified.

## External requirements — owner action needed

| # | Requirement | Owner action |
|---|---|---|
| 1 | Opening-stock financial correction | Accountant approval before the guarded correction is submitted |
| 2 | Outgoing email | Real SMTP credentials |
| 3 | Production database | MariaDB administrative credentials |
| 4 | Production hosting | Hetzner / DNS credentials |
| 5 | Bank feeds | Real bank credentials |
| 6 | Sign-off | Client UAT participation |

## Status

All wholesale operational workflows are implemented and locally verified. Go-live
remains gated on the six external requirements above, which cannot be satisfied from
this environment.

---

# Sales Teams, Snapshot and Commission (2026-08-04, v1.0.0-rc9)

## Status: complete locally, except commission payout

| Area | State |
|---|---|
| Sales Team master | complete |
| Customer assignment, detail, filters | complete |
| Smart Sales auto-load + override | complete |
| Sales Order immutable snapshot | complete |
| Delivery Note / Sales Invoice continuity | complete |
| Credit note reversal | complete |
| Commission calculation | complete |
| Commission register + export | complete |
| Existing-data backfill | complete (nothing to backfill, by design) |
| Permissions | complete |
| **Commission payout posting** | **deferred — accountant approval required** |

## Verification

| Check | Result |
|---|---|
| Backend suite | **736 tests, 0 failures, 0 errors, 6 skipped** |
| Sales Team browser | 73/73 |
| Six-viewport matrix | 228/228 |
| Customer picker | 15/15 |
| Button audit | 10, 0 failures |
| Frontend build | clean |
| Secret scan | clean |
| Backfill dry run | clean, 0 writes |
| site1.local | fingerprint identical to the mission start |
| Staging residue | none |

## Safety

- No direct GL Entry, Stock Ledger Entry, Payment Ledger Entry or Bin write.
- No separate accounting or commission ledger. Every figure is standard ERPNext
  fields plus retail-owned snapshot rows.
- No `ignore_permissions=True` in any production API added here.
- No submitted document rewritten, in code or by the backfill.
- No credentials, backups or test data committed.
- Linux-native Playwright Chromium only; no process killed by name; no `sudo`.

## The one external requirement

**Accountant approval before commission can be paid.** Required: the commission
expense account, the payee party type, whether commission is earned on invoicing or
on collection, the payout cycle, and withholding treatment. None exists in writing,
and guessing any of them would produce authoritative-looking, wrong accounting.

Until then the register calculates, reports and exports, and stops at `Earned` /
`Reversed`. There is deliberately **no `Paid` status**, because nothing in the
system can verify that money left the business.

See `docs/sales/SMJ_COMMISSION_PAYOUT_BOUNDARY.md`.

## Ordinary development remaining

- Per-transaction **percentage** override. Deliberately withheld: the requirement
  gates it behind an approved permission that does not exist. The enforcement it
  would need already exists.
- Assigning teams to the 29 unassigned customers — a business decision, listed in
  `docs/data/SMJ_SALES_TEAM_MIGRATION_RESULT.md`.
- Setting a commission rate on `STM-00014`, which is currently 0.

---

## 2026-08-04 — Commission closing and payout preparation (v1.0.0-rc10)

| Area | State |
|---|---|
| Commission calculation, register, snapshots | complete (rc9) |
| Commission policy configuration | complete |
| Policy simulation over real transactions | complete |
| Period closing, approval, statements | complete |
| Adjustments and exceptions | complete |
| Payout preparation and accounting preview | complete |
| Historical review | complete |
| **Commission accounting posting** | **blocked — 8 accountant decisions** |

Backend 810 tests, 0 failures, 6 skipped. Browser 396 checks, 0 failures, six
viewports. Frontend build clean. Secret scan clean. Staging left without residue.
site1.local fingerprint identical to the pre-mission read.

**Local implementation of everything that can be built without an accountant: complete.**
**Local verification: complete.**

What remains is not development. It is eight decisions listed in
`docs/execution/SMJ_COMMISSION_PAYOUT_BLOCKERS.md`, plus the accounting-document
choice that follows from two of them. Until they are made, the system prepares
commission fully and refuses to post it — by design, in the API, in the doctype
status ladder and in the UI, all three.
