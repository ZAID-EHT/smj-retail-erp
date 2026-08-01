# SMJ Wholesale Operations — Batch Log

## Phase 0 — preflight (2026-08-01)

- Audited worktree: 3 modified test files + 7 untracked docs were present and unverified.
- Found and fixed a dead-coverage defect: `test_quick_entry_security._base()` still sent
  `department_price`, which `_clean()` rejects since `637f999`. `_clean()` runs before the
  permission gate, so all four permission tests were failing on `Unsupported field` instead
  of asserting `PermissionError`. Committed as `8311990` after verifying 39 tests green.
- Recovery tag `pre-smj-wholesale-operations-20260801-1121`; full staging backup taken.
- site1.local fingerprint recorded read-only (SHA256 f51fedb5…d9c3).
- Confirmed `v1.0.0-rc7` does not exist; previous mission incomplete.
