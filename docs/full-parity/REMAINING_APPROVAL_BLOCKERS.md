# Remaining Approval/Environment Blockers — Required-222 Mission

Per mission Section 17: ordinary unstarted development work must **not**
be relabelled as "blocked" merely to make the mission look finished. This
file lists only the items that are genuinely blocked by something outside
normal coding — approval, credentials, or an environment dependency this
session could not resolve. Everything else in the 144-item remaining list
is **not_started**, plain and simple.

## Genuinely blocked (carried over from BLOCKERS.md, unchanged by this session)

These predate this mission and were not re-attempted here, since none of
them were required to make progress on the 222 registry — they gate the
separately-scoped wholesale core (reservation, credit, transaction
register), which already has its own honest tracking in `BLOCKERS.md`:

1. **Custom Fields for Customer credit/non-credit + wholesale transaction ID**
   (GATE 2/3) — requires explicit approval to add fixtures; not attempted.
2. **`enable_stock_reservation`** on a non-production site (GATE 1) — not
   attempted.
3. **Test environment** (`allow_tests` or a staging site) (GATE 4) — not
   attempted; this session's new tests ran as standalone scripts via
   `bench execute` against real site1 data instead, same workaround every
   prior session in this project has used.
4. **Browser automation** (Playwright/Chromium) (GATE 5) — confirmed still
   unavailable this session (no re-attempt needed; the network-egress
   diagnosis from `docs/ui/SMJ_VISUAL_REGRESSION.md` was not re-run since
   nothing in this environment changed).

None of these four gates blocked any of the 78 items completed this
session — Batches 1 and 2 were both read-only-verifiable via `bench
execute` against real data, with no schema or site-config change.

## Of the 144 remaining required-222 items: how many are actually blocked?

**Best current estimate: 0–2, not 144.** Specifically:

- **Bank Clearance / Pegged Currencies** (2 `doctype` items) — **not
  blocked**, just not yet implemented. Both are ordinary Single DocTypes
  with a normal permission model (`Accounts User` / `System Manager`
  respectively); nothing about them requires an approval or an unavailable
  dependency. They need the universal engine's document-loading path
  extended to handle `issingle=1` doctypes (currently untested for
  Singles), which is real but ordinary engineering.
- **The 140 remaining `document_action` items** — **not blocked**. Every
  one of them is a standard ERPNext button calling a standard ERPNext
  controller method already present in the installed `erpnext` app. None
  of them were found this session to require a schema change, a new
  Custom Field, external credentials, or a payment gateway. (The two
  exceptions worth flagging for the *next* session to double-check:
  `Company.create_transaction_deletion_request`/`delete_transactions` may
  touch ERPNext's own destructive bulk-delete tooling and should get
  extra scrutiny before wiring a button to it, and
  `Bank Statement Import` actions genuinely need a real bank statement
  file format decision, not an approval gate — worth a product decision,
  not a blocker.)
- **Sales Funnel / Warehouse Capacity Summary** (2 `page` items) — **not
  blocked**. Same live-data-analytics pattern as the Batch 1 dashboards;
  simply not reached this session.

## Bottom line

This session's 144-item remainder is **backlog, not blockers**. Nothing
here should be marked `approval_blocked` or `environment_blocked` in the
registry — that would misrepresent ordinary unstarted work as something
requiring a decision from someone outside engineering, which the mission
explicitly forbids. The honest status for all 144 is `unavailable_with_reason`
(→ "Pending implementation; standard Desk mapping remains source of
truth."), exactly what the registry already shows them as.
