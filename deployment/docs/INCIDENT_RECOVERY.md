# Incident Recovery

## Bad deploy
- Smoke test fails → deploy leaves maintenance mode ON. Investigate logs
  (`docker compose logs backend`). Roll back: `scripts/rollback.sh <previous:tag>`.

## Data corruption / loss
- Restore the latest good backup into a fresh site, verify, then cut over. Requires
  DB root (external). See BACKUP_STRATEGY.md and restore-test.sh.

## Never
- `docker compose down -v` (deletes DB volume).
- Direct SQL edits to fix ledgers — use standard controllers / documented tools.

## Escalation
- Capture `docker compose ps`, `scripts/health-check.sh` output, and the failing
  smoke-test log before any destructive step.
