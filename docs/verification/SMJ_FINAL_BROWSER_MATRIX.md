# SMJ Final Six-Viewport Browser Matrix

Run 2026-07-27 on `staging.local`. Harness: `frontend/e2e/viewport_matrix.mjs`,
Linux-native Playwright Chromium located via `chromium.executablePath()` — never a
guessed path, never Windows Chrome; the browser is closed through the Playwright API
and no process is killed by name.

## Result: 90/90 checks, 0 problems

| Viewport | Result |
|----------|--------|
| 1920 × 1080 | 15/15 |
| 1440 × 900 | 15/15 |
| 1024 × 768 | 15/15 |
| 768 × 1024 | 15/15 |
| 390 × 844 | 15/15 |
| 360 × 800 | 15/15 |

## Pages covered (15)

Home, Smart Sales, Product form (7 new fields + pricing), Customer form, Effective
Access, User Permissions, Roles, Role Profiles, Users (generated), Companies, Setup
wizard, Printing & Branding, Email admin, Data Management, System Operations.

## Checks per page × viewport

- HTTP status (no unexpected 500),
- dead route detection (no "Page not found" on a real page),
- horizontal overflow (`scrollWidth − clientWidth ≤ 1px`),
- console errors and page errors (zero),
- sensitive-data leak heuristic in the DOM (zero).

## Authentication

Each context authenticates through the real `/api/method/login` as a throwaway
System Manager whose password is generated per run and printed to stdout only — never
written to a document or the repo. The account is removed after the run.

## Notes

- Desktop (1920/1440/1024), tablet (768) and mobile (390/360) all pass with no
  clipping and no horizontal overflow.
- The earlier dead-route and optional-group-500 classes of defect (found in the prior
  mission's browser run) stayed fixed — every new admin route resolves and renders.

---

## Re-run 2026-07-27 (finance/deployment mission)

Re-verified after the finance/deployment work: **90/90 checks, 0 problems** across all
six viewports and the same 15 pages. No regressions from the correction package,
deployment package or documentation changes. Throwaway System Manager removed after
the run; `site1.local` fingerprint re-confirmed identical to the Phase 0 baseline.
