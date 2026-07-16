# Required-222 Batch Log

Chronological log of this mission's batches. Each row's counts were
verified by re-running `my_store_ui.audit.parity_registry.
corrected_production_parity_audit()` live against the current repository
state immediately before and after the batch — never assumed, never
carried forward from a stale file.

| # | Batch | required_but_missing before → after | Commit |
|---|---|---|---|
| 0 | Verified git state (clean except one pending regression-test file, which was reviewed and committed), confirmed branch/commit/tag match the mission brief, confirmed the live audit exactly matches the 222 snapshot (`user_facing_required=1266`, `mapped_required=991`), created recovery tag | — | `ee4fbf4` (pending test), tag `pre-complete-required-222-20260716-2109` |
| 1 | All 59 required Dashboard Charts (28) + Number Cards (25) + Dashboards (6) — new `my_store_ui/module_dashboards.py`, wired into `ModuleDashboardPage.vue`, new `DASHBOARD_ANALYTICS_ADAPTERS` registry credit table, 10 tests | 222 → 163 | `55a4d3e` |
| 2 | Dead-credit: 20 document-actions were ERPNext dashboard "Connections" tiles, not JS buttons — new generic `get_dashboard_connections()` adapter, wired into `UniversalDetailPage.vue`, 19/20 credited (1 stays pending — Blanket Order isn't routed). Also fixed a real duplicate-dict-key bug (`Supplier` entry silently overwritten, `hold`/`resume` were dead code). 6 tests | 163 → 144 | `7f2aae1` |

**Net this session: 222 → 144 (78 items, 35%), 2 feature commits + 1
pending-test commit, all with passing tests and a passing `npm run build`.**

## Investigated but not implemented this session

- **Bank Clearance / Pegged Currencies Single DocType pages** — metadata
  read and permission model confirmed (both `issingle=1`, Accounts module;
  Bank Clearance needs its two real actions `get_payment_entries`/
  `update_clearance_date` wired through a Single-DocType-aware load path
  that the universal engine does not have yet). Not started, to avoid
  rushing document-loading-path changes late in a long session. See
  Recommended next-session order item 1 in
  [REQUIRED_222_COMPLETION_REPORT.md](REQUIRED_222_COMPLETION_REPORT.md).
- **Sales Funnel / Warehouse Capacity Summary pages** — not investigated
  this session; flagged for the next batch as the same pattern as Batch 1.

## Why the mission did not reach zero in one session

Batches 1 and 2 succeeded quickly because they were genuinely shared
patterns — one backend module covered 59 registry entries, one adapter
covered 20. The remaining 144 are ~80 distinct (doctype, action) pairs with
no such shared pattern; each one requires reading the real ERPNext
controller/JS source, confirming the exact method signature, writing a
fixed-purpose adapter (never a generic method-path RPC, per this project's
own standing security rule), wiring a frontend action, and testing it
against real data — the same rigor every batch in this project's git
history has applied. That is inherently one-at-a-time work. Committing to
finish all 144 in the same pass would have meant cutting that verification
short, which is exactly the "fake parity" this mission explicitly forbids
(Section 2: no guessed method names, no generic backdoor, no crediting
without verifying the destination actually executes the workflow).
