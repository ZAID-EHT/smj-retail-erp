# DNS and TLS (external — requires DNS access)

1. **DNS** (external): create an A/AAAA record for `erp.example.com` → the Hetzner
   server IP.
2. **TLS**: use the `compose.override.example.yaml` Caddy proxy (auto-Let's-Encrypt)
   or Traefik/nginx. Copy `Caddyfile.example` → `Caddyfile`, set the real domain.
3. Only 80/443 are published by the proxy; `frontend` stays bound to 127.0.0.1:8080.
4. Verify: `https://erp.example.com/api/method/frappe.ping` returns `{"message":"pong"}`.
5. HSTS and security headers are set in the Caddyfile.

DNS record creation and the public domain are external requirements.
