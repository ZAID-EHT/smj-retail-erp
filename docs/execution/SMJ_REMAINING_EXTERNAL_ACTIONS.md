# SMJ Master Mission — Remaining External Actions

Everything below requires a human decision, external infrastructure, or
credentials this environment doesn't have. None of it is "unfinished
coding work" — it's genuinely outside what an autonomous agent can or
should complete alone.

## Decisions needed from the business owner / project lead

1. **P&L data-quality correction** — the demo dataset's Profit and Loss
   Statement overstates profit by ~11.8M LKR due to opening-stock
   postings hitting the wrong account type. Fix path documented in
   `docs/verification/SMJ_ACCOUNTING_VERIFICATION.md`. Requires a
   decision on whether to regenerate the demo data (clean fix, but
   discards current staging state) or apply a live correction (riskier,
   needs care around the 100+ documents built on top of the affected
   entries since).
2. **Role-scoping choices** flagged in `docs/security/SMJ_SECURITY_BLOCKERS.md`
   — whether `Purchase Manager` should see Purchase Receipts/Invoices,
   and whether `System Manager` alone should touch business
   transactions. Both are ERPNext defaults, not bugs; changing them is a
   business policy decision.
3. **UX hardening priority** — the reservation-race and
   naming-series-contention findings (both data-safe, but surface a raw
   deadlock error to a losing user on the first attempt) — whether to
   prioritize the recommended bounded-retry wrapper before go-live.

## Infrastructure the client must provide

4. Real staging/production hardware, HTTPS, off-server backups,
   monitoring, and email configuration — this environment has none of
   these and should not fabricate them.
5. **BLOCKER-001**: `sudo sysctl -w vm.overcommit_memory=1` (cosmetic
   Redis warning only, not urgent).
6. **BLOCKER-002**: RQ version alignment (`rq==2.10.0`) — a deliberate,
   tested upgrade decision, not performed automatically per this
   project's "no uncontrolled upgrades" rule.

## Human processes, not code

7. **Client UAT** — the actual business owner/staff need to use the
   system.
8. **Accountant sign-off** — a qualified accountant needs to review the
   chart of accounts, tax setup, and financial reports (including the
   P&L finding above) against real Sri Lankan regulatory requirements.
9. **Staff training, deployment rehearsal, rollback rehearsal** — need
   scheduled time with real people.

## What is NOT on this list (because it's done)

GATE 4 (`bench run-tests`) and GATE 5 (browser verification) — both
closed this mission with real evidence, not flagged here as pending.
The full-year demo dataset, wholesale workflow, security matrix,
accounting report reconciliation, import/purchasing chains, and
backup-restore/load/concurrency testing are all complete with real,
documented evidence under `docs/`.

---

## Update 2026-07-27 (final-readiness mission)

1. **P&L opening-stock correction** — root cause confirmed and a guarded, reversible
   correction built + reconciled via dry-run (profit 15.87M → 4.05M, Trial Balance
   balanced). **Apply is one command, held for accountant sign-off** — see
   `docs/finance/SMJ_OPENING_STOCK_QA_RESULT.md` and
   `docs/release/SMJ_ACCOUNTANT_SIGNOFF_CHECKLIST.md`.
2. **SMTP credentials** — still external; email admin + status built
   (`docs/email/SMJ_EMAIL_SETUP.md`).
3. **MariaDB root password** — needed for isolated QA / fresh-install sites.
4. **Scheduler** — enable in production (staging shows it disabled).
5. **Hetzner / DNS** — deployment, separate.
