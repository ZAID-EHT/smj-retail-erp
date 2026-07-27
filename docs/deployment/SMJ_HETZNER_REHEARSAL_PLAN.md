# SMJ Hetzner Rehearsal Plan

## Status: package complete + statically validated; live deploy is external

Docker is not installed in this environment, so `docker compose config` could not run
here; the compose file was **statically validated** (valid YAML; 10 services; DB/Redis
unpublished; frontend bound to 127.0.0.1). All 8 scripts pass `bash -n`.

## Rehearsal steps (on a Hetzner staging server — external credentials)
1. Provision + harden the server; install Docker (see docs/HETZNER_SETUP.md).
2. Build + push the immutable image from `deployment/apps.json` (apps.pinning.md).
3. Copy `deployment/`, set `.env`, `scripts/preflight.sh`.
4. Create the site inside the `sites` volume; `scripts/deploy.sh`.
5. `scripts/smoke-test.sh` → frappe.ping + readiness + HTTP 200.
6. `scripts/backup.sh` then `scripts/restore-test.sh` (drill into a throwaway site).
7. `scripts/rollback.sh <prev:tag>` to rehearse rollback.

External: Hetzner + registry + DNS credentials.
