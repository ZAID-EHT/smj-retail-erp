# SMJ RC4 Six-Viewport Browser Matrix

Run 2026-07-27 on `staging.local`. Linux-native Playwright Chromium via
`chromium.executablePath()`; browser closed through the Playwright API; no process
killed by name. Throwaway System Manager (per-run password) removed afterwards.

## Result: 96/96 checks, 0 problems

| Viewport | Result |
|----------|--------|
| 1920 × 1080 | 16/16 |
| 1440 × 900 | 16/16 |
| 1024 × 768 | 16/16 |
| 768 × 1024 | 16/16 |
| 390 × 844 | 16/16 |
| 360 × 800 | 16/16 |

## Pages (16)
Home, Smart Sales, Product form, Customer form, **Administration landing**, Effective
Access, Roles, Users, Companies, Setup wizard, Printing & Branding, Email admin, Data
Management, **Scheduled Reports**, System Operations, **Launch Readiness**.

## Per page × viewport
HTTP status, dead-route, horizontal overflow, console + page errors, DOM secret-leak
heuristic — all clean. Desktop/tablet/mobile all pass; no clipping, no overflow, no
dead routes, no HTTP 500, no console errors, no sensitive-data exposure.
