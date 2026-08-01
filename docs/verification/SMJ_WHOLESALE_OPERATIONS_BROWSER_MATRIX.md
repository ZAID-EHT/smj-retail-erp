# SMJ Wholesale Operations — Browser Matrix

Harness: `frontend/e2e/viewport_matrix.mjs`. Linux-native Playwright Chromium only
(`~/.cache/ms-playwright/chromium-1228`), located through
`chromium.executablePath()` — never a guessed path, never Windows Chrome. The
browser is always closed through the Playwright API; no process is killed by name.

Authentication uses a throwaway staging-only user created per run
(`dev_scripts/browser_check_user.py`) with a password generated per run and printed
to stdout only. It is removed after the run.

## Result — 2026-08-01

| Viewport | Size | Checks | Failures |
|---|---|---|---|
| desktop-1920 | 1920 × 1080 | 27 | 0 |
| desktop-1440 | 1440 × 900 | 27 | 0 |
| laptop-1024 | 1024 × 768 | 27 | 0 |
| tablet-768 | 768 × 1024 | 27 | 0 |
| mobile-390 | 390 × 844 | 27 | 0 |
| mobile-360 | 360 × 800 | 27 | 0 |
| **Total** | | **162** | **0** |

## Routes covered (27)

Home, Smart Sales, Product quick-create, Customer quick-create, Product list,
Customer list, **Wholesale transaction register**, **Sales Orders**, **Delivery
Notes**, **Sales Invoices**, **Payment Entries**, **Purchase Orders**, **Purchase
Receipts**, **Purchase Invoices**, **Suppliers**, Administration landing, Effective
Access, Roles, Users, Companies, Setup wizard, Printing & Branding, Email admin,
Data Management, Scheduled Reports, System Operations, Launch Readiness.

(The nine bold routes were added by this mission.)

## Checked per route, per viewport

- HTTP status (no 4xx/5xx)
- No console errors and no page errors
- No "page not found" — catches routes that exist in Vue but are not registered in
  the server-side `ROUTE_REGISTRY`
- No unintended "permission denied"
- No horizontal overflow (`scrollWidth − clientWidth`)
- Heading structure present
- Touch-target sizing on mobile widths
- No stored secret rendered into the DOM

## Defects this matrix found

Both were invisible to the 540-test backend suite:

1. **Transaction register: console 403.** The route guard admitted any signed-in
   user while `get_wholesale_transactions` requires Sales Order read, so the page
   rendered and then failed. Root cause: the special route carried no `doctype`, and
   **System Manager is a Frappe role that grants no ERPNext selling rights**. Fixed
   by declaring `Sales Order` on the route; pinned by
   `test_register_route_permission`.

2. **Smart Sales: 404.** `get_bootstrap` raised `DoesNotExistError` because
   `get_navigation()` links to the POS Awesome page, which is not installed, and
   `frappe.has_permission(doc=...)` throws for a missing record instead of returning
   False — breaking the whole bootstrap rather than one menu link. Fixed by dropping
   links to absent optional records; pinned by `test_navigation_missing_page`.

## Reproducing

```bash
cd /home/zaidh/frappe-bench
CREDS=$(bench --site staging.local execute my_store_ui.dev_scripts.browser_check_user.create)
export ERP_USER=... ERP_PW=...        # from CREDS, stdout only
cd apps/my_store_ui/frontend
NODE_PATH=/home/zaidh/.npm/_npx/e41f203b7505f1fb/node_modules \
PLAYWRIGHT_PATH=/home/zaidh/.npm/_npx/e41f203b7505f1fb/node_modules/playwright \
  node e2e/viewport_matrix.mjs
bench --site staging.local execute my_store_ui.dev_scripts.browser_check_user.remove
```
