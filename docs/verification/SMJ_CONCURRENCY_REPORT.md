# SMJ Retail ERP — Concurrency Report (Phase 10 summary)

**Date:** 2026-07-18 · **Site:** staging.local

This is the mission's system-wide concurrency summary, pulling together
two independent real concurrency tests run in this project (both used
genuine separate OS processes, never simulated):

## 1. Wholesale stock reservation race (Phase 4)

Full detail: `docs/workflows/SMJ_WHOLESALE_CONCURRENCY_REPORT.md`.

Two processes raced to reserve 8 units each of a 10-unit stock item.
Result: one succeeded (8 reserved), one hit a clean InnoDB deadlock and
rolled back, a retry then correctly reserved the true remaining amount
(2). **Total reserved never exceeded 10 — no over-reservation under real
concurrent load.**

## 2. General write-contention test (Phase 10)

Full detail: `docs/verification/SMJ_LOAD_TEST_REPORT.md`.

10 processes simultaneously inserted documents that all needed the same
naming-series counter. 1 succeeded immediately, 9 hit a clean deadlock.
**Zero data corruption** — confirmed directly, exactly one document
existed after the batch. All 9 failed workers succeeded cleanly on a
sequential retry with correct, gap-free numbering.

## Combined finding

Both tests hit the **same underlying mechanism**: MySQL/InnoDB row
locking correctly prevents two simultaneous writers from corrupting each
other's data, at the cost of the losing writer receiving a raw deadlock
error rather than a graceful "please retry" response. This is consistent
core ERPNext/Frappe behavior (not specific to this project's
customizations) and was observed identically in two unrelated code paths
(stock reservation, naming-series document creation) — strong evidence
it is a general framework characteristic, not an isolated bug.

**Data safety verdict: PASS in both tests.** No corruption, no
over-commitment, no silently-lost writes anywhere.

**UX hardening recommendation (not applied in this mission, consistent
with both individual reports):** any high-contention insert/reserve path
exposed directly to end users should wrap its call in a bounded
retry-on-deadlock loop (catch `pymysql` error 1213/1020, retry once or
twice with a short backoff) so a losing request resolves automatically
instead of surfacing a raw 500-class error on the user's first click.
This applies generally, not to one specific feature.

## Read-side concurrency

20 concurrent reads and 15 concurrent aggregate-report reads both
succeeded 100% of the time with fully consistent results across every
worker (see `SMJ_LOAD_TEST_REPORT.md`) — read-side concurrency has no
issues at the volumes tested.
