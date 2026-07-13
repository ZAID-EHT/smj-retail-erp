# Standalone Retail ERP routing and authentication

## Entry points

- `/` resolves request-locally to the app-owned `retail_erp` website page.
- `/retail-erp` and `/retail-erp/<path>` resolve to the same no-cache Vue entry.
- The website entry loads content-hashed assets from `public/frontend/.vite/manifest.json`.
- Stable `retail-erp.js` and `retail-erp.css` copies are retained only for the temporary Desk Page mount.

No Frappe or ERPNext core route is modified. The prefix rule does not match APIs, assets, files, print/PDF, password reset, OTP, webhooks, sockets or integration callbacks.

## Authentication

The custom login posts to `/api/method/login`. OTP continuation posts `otp` and `tmp_id` to the same endpoint. Password reset uses `frappe.core.doctype.user.user.reset_password`. Logout posts to `/api/method/logout`.

The browser stores no password, SID, CSRF token or session secret in localStorage/sessionStorage. The app-owned `get_session_bootstrap` response contains no identity, role, permission or business data for Guest. Authenticated responses include only identity display fields, roles, company, server-selected landing, permission-filtered navigation and the current session CSRF token.

Modal dialogs use the shared focus manager for Tab containment, Escape close and focus restoration. The standalone shell also provides a skip-to-content link and retains labelled login controls and visible focus states.

## Route authorization

`my_store_ui.services.frontend_routes.ROUTE_REGISTRY` owns every implemented route, feature identifier and required DocType permission. Unknown routes show custom 404, known unavailable features show Feature Unavailable, and denied routes show Permission Denied. Document APIs separately enforce document-level permission and avoid existence leaks.

Role precedence selects only the initial landing; it grants no permission. Navigation is filtered by current server permissions.

## Desk blocking and emergency access

HTML GET navigation under `/app` is redirected with a non-cacheable 302. AJAX, non-HTML requests and all non-Desk prefixes are untouched. Known DocType routes map to custom pages; other Desk routes map to Feature Unavailable.

`allow_emergency_standard_desk` is absent/false, so emergency Desk is disabled. If a separately approved site configuration change enables it, only Administrator with `?retail_emergency=1` may bypass the guard, the attempt is logged, and no menu exposes it. System Manager cannot use this bypass.

## Known verification limitation

The site has only Administrator and one enabled non-Administrator System User; both have System Manager plus multiple business roles. Dedicated single-role browser verification therefore requires approved temporary users. Automated tests cover landing precedence and permission outcomes without changing user records.
