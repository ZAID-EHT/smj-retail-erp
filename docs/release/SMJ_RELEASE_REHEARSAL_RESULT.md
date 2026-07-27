# SMJ Release Rehearsal Result

Run 2026-07-27 on `staging.local`. Commit `9876572`, branch `full-feature-parity`.

## Checks

| Item | Result |
|------|--------|
| Worktree clean | ✅ |
| Migrations (`bench migrate`) | ✅ clean (fixtures applied) |
| Frontend production build | ✅ clean |
| Secret scan (private keys / tokens / db_password / committed .env / backups) | ✅ **none found** |
| Committed scratch/temp/.log files | ✅ none |
| Residual test users (smj-%@example.com) | ✅ none |
| Residual test items (SMJ-%TEST% / %PROBE%) | ✅ none |
| Disabled non-group warehouses | ✅ none (re-enabled after the regression they caused) |
| Submitted opening-stock correction JE | ✅ 0 (correctly unapplied — awaiting sign-off) |
| Draft opening-stock correction JE | ✅ 0 (create on demand via prepare_draft) |
| Deployment compose (static) | ✅ valid; DB/Redis unpublished; frontend localhost-bound |
| Deployment scripts (bash -n) | ✅ all 8 pass |

## Defect fixed during rehearsal
The prior mission's warehouse-disabling cleanup had broken 5 test modules
(disabled warehouses are rejected in transactions). Re-enabling the three empty test
warehouses restored the full green suite. Documented; they cannot be hard-deleted
(cancelled-SLE history) so they remain enabled and empty.

## Secret scan detail (paths only, no values)
- BEGIN … PRIVATE KEY in tracked files: none
- AWS/GitHub token patterns: none
- Non-placeholder db_password assignments: none
- Committed .env / .sql / .sql.gz / .pem / .key / cookies / backups: none
