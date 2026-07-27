# SMJ Finance / Deployment — Batch Log

## Phase 0 (2026-07-27)
- Verified HEAD 13b3da1 = v1.0.0-rc2, branch full-feature-parity, worktree clean.
- Tag pre-smj-finance-deployment-20260727-0941 created.
- Backup 20260727_094121-staging_local-* taken.
- site1.local fingerprint recorded (read-only): SMJ + SMJ (Demo), 0 test users,
  0 correction JEs, admin modified 2026-05-28, latest GL 2026-12-10.

## Phases 1-11 (2026-07-27)
- Phase 1: reproduced baseline; found + fixed a regression (3 test warehouses disabled
  by prior cleanup broke 5 modules; re-enabled → green).
- Phase 2: finance figures re-verified from GL (before 15,868,706; overstatement
  11,820,700; corrected 4,048,006; TB balanced). Impossible figure 4,048,825,204 is
  NOT in the repo (concatenation artifact).
- Phase 3: single root cause confirmed at voucher level (3 Material Receipts crediting
  Expense Stock Adjustment).
- Phase 4: guarded correction package (inspect/dry_run/prepare_draft/verify_after/apply)
  + 5 tests. Apply requires confirm token (accountant sign-off).
- Phase 5: QA site credential-blocked; savepoint reconciliation done.
- Phase 6: staging correction runbook (submission external).
- Phase 7: corrected release status language (status ladder; scorecard rows).
- Phase 8: fresh-install script (static-validated; refuses protected sites); live blocked.
- Phase 9: SMTP security verified (4 tests) + production checklist.
- Phase 10: Hetzner deployment package (compose statically valid; 8 scripts bash -n; secrets git-ignored).
- Phase 11: release rehearsal — secret scan clean, staging residue-free, correction unapplied.
