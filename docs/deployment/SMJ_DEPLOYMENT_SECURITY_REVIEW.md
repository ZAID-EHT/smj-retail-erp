# SMJ Deployment Security Review

| Control | Status |
|---------|--------|
| MariaDB not published | ✅ no `ports:` on `db` (asserted) |
| Redis not published | ✅ no `ports:` on redis-cache/redis-queue (asserted) |
| App bound to localhost | ✅ frontend `127.0.0.1:8080` only; TLS proxy fronts it (asserted) |
| Firewall: only SSH/80/443 | ✅ documented (HETZNER_SETUP.md) |
| Secrets not committed | ✅ `.env`, `Caddyfile`, `*.key/*.pem`, override git-ignored; `.env.example` placeholders only |
| Immutable image (no floating latest) | ✅ preflight refuses `:latest`; apps pinned |
| No destructive volume ops | ✅ scripts avoid `down -v`; rollback documents the risk |
| TLS + HSTS + security headers | ✅ Caddyfile.example |
| Restore is deliberate, not web-exposed | ✅ restore-test.sh is manual, into a throwaway site |
| No secrets printed | ✅ scripts source `.env`, never echo secrets |

External credentials (Hetzner, registry, DNS, SMTP) are required to execute the deploy
but not to review or prepare the package.
