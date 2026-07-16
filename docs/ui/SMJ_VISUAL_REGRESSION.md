# SMJ Retail ERP — Visual Regression / Screenshot Evidence

**No screenshots were captured in this pass.** Playwright is not installed
in this environment:

```
$ python3 -c "import playwright"
ModuleNotFoundError: No module named 'playwright'
$ npx playwright --version
npm error UNABLE_TO_VERIFY_LEAF_SIGNATURE
```

Installing it would mean a network package install in an environment where
that already failed on a certificate error, and the mission's own
instructions say not to install system packages without approval. So this
step was skipped rather than faked.

What *was* verified, every time a batch of CSS/component changes landed:

```
cd apps/my_store_ui/frontend && npm run build
```

— which succeeded on every run (111 → 171 modules once icons were wired
in), meaning there are no Vue compilation errors, no broken imports, and no
syntax errors across the ~55 new icon components and every touched
stylesheet.

`bench serve` was confirmed running and reachable (`curl` → `200`) but no
authenticated page render was captured.

## For a follow-up session

1. Install Playwright (with approval) or use whatever browser automation is
   already configured for this project.
2. Log in, then screenshot Home, Smart Sales, Sales Orders, Products,
   Customers, Purchases, Finance, Transaction Register, Reports, a
   universal DocType list/detail/form, and Bank/Payment Reconciliation at
   1440×900, 768×1024 and 390×844.
3. Compare against `SMJ_Retail_ERP_UI_Design_Pack/01_generated_previews/*`
   and adjust spacing/density where they diverge — the token values will
   already match, so any remaining differences will be layout composition,
   not colour or typography.

## 2026-07-16 — install attempted with explicit user approval, still blocked

The user approved a Playwright install attempt this session. It still
failed, but for a more specific reason than "no network":

```
$ npm install -D @playwright/test --fetch-timeout=15000 --fetch-retries=0
npm error code UNABLE_TO_VERIFY_LEAF_SIGNATURE
npm error request to https://registry.npmjs.org/@playwright%2ftest failed,
  reason: unable to verify the first certificate; if the root CA is
  installed locally, try running Node.js with --use-system-ca

$ NODE_OPTIONS="--use-system-ca" npm install -D @playwright/test ...
# same error — ruled out "missing system CA" as the cause

$ curl -sS --cacert /etc/ssl/certs/ca-certificates.crt \
    https://registry.npmjs.org/playwright
curl: (60) unable to get local issuer certificate

$ curl -sS http://registry.npmjs.org/playwright   # plain HTTP, no TLS
HTTP/1.1 403 Forbidden
```

TCP connects fine, DNS resolves fine, but TLS verification fails against
the *standard* system CA bundle and plain HTTP gets an explicit `403`. That
combination — reachable host, failed cert, active rejection on the
fallback protocol — points at an egress proxy specific to this sandbox that
terminates/inspects outbound HTTPS and rejects package-registry traffic,
not a fixable local misconfiguration. `--insecure` / disabling TLS
verification was deliberately not attempted: even if it "worked" it would
mean trusting an unknown intercepting certificate, and the `403` on plain
HTTP suggests the request would be rejected regardless. This is an
environment/infrastructure limit, not a permission one — re-attempting
install from a different network (e.g., the user's own machine, per the
"you install it, then I verify" option that was offered but not chosen)
is the only way forward.
