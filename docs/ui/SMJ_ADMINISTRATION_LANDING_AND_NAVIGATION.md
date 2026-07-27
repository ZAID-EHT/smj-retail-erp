# SMJ Administration Landing & Navigation

Route: `/retail-erp/admin`. Backend: `my_store_ui/admin_landing.py`
(`get_admin_landing`). Tests: `test_admin_landing` (5, green).

## Cards (permission-aware)
Companies & Setup, Users & Access, Printing & Branding, Email & Notifications,
Data Management, Finance Setup, Scheduled Reports, System Operations, Launch
Readiness. Each card is returned **only** if the caller passes the server-side gate
(System Manager, or the relevant DocType read permission). A Sales User sees none of
the manager-gated cards.

## Each card carries a live status
- Email: "Configured" / "Email not configured"
- Finance: "Accountant approval pending" (with a warning) / "Correction applied"
- Companies: "N company(ies)" / "Setup required"
- System: "Healthy" / "Scheduler disabled"
- plus a primary action route and an optional secondary route.

No infrastructure or financial detail is returned to a non-manager. Guest is
rejected.

## Route/permission/state coverage
Every admin area has a canonical `/retail-erp/...` route registered server-side and
in the SPA, is System-Manager gated where appropriate, and renders loading / empty /
error / permission-denied states. Browser-verified across six viewports (see the RC4
browser matrix). No redirection to the standard ERPNext Desk.
