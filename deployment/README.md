# SMJ Retail ERP — Production Deployment (Hetzner)

Immutable-image, official-frappe_docker-based production stack. **Not** for local dev;
does not use `bench start`. MariaDB and Redis are internal-only; a TLS reverse proxy
publishes 80/443.

## Files
- `apps.json` / `apps.pinning.md` — apps to build into the image + version pinning.
- `compose.yaml` — production services (backend, configurator, frontend, websocket,
  scheduler, two queue workers, db, redis-cache, redis-queue).
- `compose.override.example.yaml` + `Caddyfile.example` — optional auto-TLS proxy.
- `.env.example` — placeholders only (copy to `.env`, never commit real secrets).
- `scripts/` — preflight, deploy, migrate, smoke-test, backup, restore-test, rollback, health-check.
- `docs/` — Hetzner setup, DNS/TLS, backup strategy, incident recovery.

## Flow
1. Build + push the immutable image (see `apps.pinning.md`).
2. On the host: copy `.env.example` → `.env`, fill secrets; set up the proxy.
3. First deploy: `scripts/preflight.sh`, then create the site inside the `sites`
   volume, then `scripts/deploy.sh`.
4. Subsequent deploys: bump `IMAGE` tag, `scripts/deploy.sh` (maintenance-mode wrapped,
   smoke-tested, auto-rollback-able).

## Safety
- No `docker compose down -v` (would delete the DB volume).
- DB/Redis never published; firewall allows only SSH + 80/443.
- Secrets only in `.env` (git-ignored). Restore is a deliberate manual drill.
