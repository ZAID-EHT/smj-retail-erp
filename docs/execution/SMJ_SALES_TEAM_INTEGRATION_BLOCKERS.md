# SMJ Sales Team Integration — Blockers and External Requirements

Anything that genuinely cannot be completed locally. Ordinary development is never
listed here.

## External requirements

| # | Requirement | Why it is external | What was done instead |
|---|---|---|---|
| 1 | Commission payout posting (Payment Entry / Journal Entry / payroll to a sales person) | Creating a real financial posting against an employee needs an accountant's approval and confirmed accounting rules — which expense account, which party type, which payout cycle. None exist. | Commission is calculated, snapshotted, reported and exportable, and carries an approval status. The payout step stops at `Approved`. Documented in `docs/sales/SMJ_COMMISSION_PAYOUT_BOUNDARY.md`. |
| 2 | Cross-company enforcement proven against a second real company | `staging.local` has exactly one Company (`SMJ Retail ERP`). | The guard is implemented and unit-tested against a throwaway company created and removed inside the test, so the rule is proven without inventing production data. |
| 3 | Pushing the branch and the release tag | No git remote credentials are available in this environment. | Commits and the tag are created locally. Push is left to whoever holds the credentials. |

## Confirmed *not* blockers

| Item | Why it is ordinary development |
|---|---|
| Backfilling submitted historical documents | 103 submitted Sales Orders predate the feature and hold no team evidence. Guessing a team for them would fabricate commission history. They are exported for manual review instead — a deliberate design decision, not a blocker. |
| The single-company staging site | Company scoping is implemented and tested; only a *production-scale* multi-company proof is unavailable. |
