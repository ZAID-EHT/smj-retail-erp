# Standalone browser verification — 2026-07-13

## Automated HTTP and build checks

- `/`, `/retail-erp/home`, nested form routes and encoded document routes return the standalone shell with no Desk markup.
- Guest bootstrap returns only `{authenticated: false}`.
- Invalid and blank login attempts return Frappe authentication failures; the custom page normalizes them to a non-enumerating message.
- API and asset routes are not redirected. A missing hashed asset returns 404 rather than the SPA.
- Password-reset, print/PDF and file prefixes are not intercepted by the Desk guard.
- `/app`, known Desk list/form routes, old `/app/retail-erp/*` routes and an unmapped Workspace route return non-cacheable 302 redirects to clean Retail ERP routes.
- Direct clean-route refresh returns HTTP 200 and the current hashed JS/CSS from the Vite manifest.
- Production Vue build and the full Python regression suite pass.

## Browser routes opened

- `/`
- `/retail-erp/home`
- `/retail-erp/sales/orders/new`
- `/retail-erp/sales/invoices/ACC-SINV-2026-00010`
- `/retail-erp/finance/payments/new`

## Manual verification still required

Interactive browser automation is not installed in this WSL environment. The following checks are therefore not claimed complete:

- actual valid-password and OTP entry (site-wide 2FA is currently disabled);
- disabled-user login (no disabled test user exists);
- logout/Back and forced session-expiry behavior in Chrome and Edge;
- dedicated Sales, Stock, Purchase and Accounts single-role landing behavior (no such test users exist);
- console, wheel/touch/keyboard scroll and layout inspection at 320, 375, 390 and 768 px;
- visual checks at 80%, 100%, 125% and 150% zoom;
- interactive confirmation of the implemented Tab loop, Escape close and focus restoration across every legacy transaction dialog.

No temporary user or permission change was made. Creating dedicated browser-test users requires explicit approval.

## Environment warning

The server currently reports that `wkhtmltopdf` is unavailable, so PDF generation cannot be visually verified even though permission checks and the standard protected PDF endpoint remain wired. This is an environment dependency, not a browser-generated invoice fallback.
