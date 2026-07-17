# SMJ Master Mission — Blockers

Only genuine external blockers go here (per the mission's own rule: "Do not
classify ordinary unfinished coding work as externally blocked"). Anything
listed here has already had all safe local work completed around it.

---

## BLOCKER-001: Redis memory overcommit warning

- **Type:** OS-level, requires sudo (no passwordless sudo on this machine).
- **Impact:** Cosmetic warning only. Does not stop Redis, does not stop
  Bench, does not affect data integrity or any test in this mission.
- **Exact command for the user to run:**
  ```
  sudo sysctl -w vm.overcommit_memory=1
  echo "vm.overcommit_memory = 1" | sudo tee /etc/sysctl.d/99-redis-overcommit.conf
  sudo sysctl --system
  ```
- **Status:** Documented, not re-attempted each session, does not block
  any mission phase.

## BLOCKER-002: RQ library version drift (Python 3.14 deprecation warnings)

- **Type:** Environment dependency drift, not a code bug.
- **Detail:** Installed `rq==1.15.1`; Frappe's own `pyproject.toml`
  declares `rq (2.10.0)` as the intended version. The older RQ calls the
  now-deprecated `datetime.datetime.utcnow()`, which Python 3.14 warns
  about on every scheduler tick.
- **Why not fixed automatically:** RQ underpins the job queue for the
  *entire* bench (every app, both sites), not just this project. The
  mission's own rule against "uncontrolled package upgrades" applies
  directly — this needs a deliberate, tested upgrade decision, not a
  silent one buried inside a demo-data mission.
- **Exact command if the user wants it fixed:**
  ```
  ./env/bin/pip install "rq==2.10.0"
  ```
  then restart `bench start` and confirm scheduler/worker still process
  jobs correctly (test with a simple enqueued job) before trusting it in
  production-adjacent use.
- **Status:** Documented, confirmed non-blocking (scheduler and worker
  remain alive despite the warning, confirmed across multiple observed
  bench restarts this session).

## BLOCKER-003: No working headless Chrome in this container (blocks Phase 6 visual layer + browser/responsive verification)

- **Type:** Environment/tooling gap, confirmed by direct attempt (not
  assumed).
- **Detail:** The `accesslint` MCP server's `audit_live` tool attempts to
  auto-launch a headless Chrome via `@accesslint/chrome` when none is
  reachable. Attempted against the app's own reachable shell URL
  (`http://127.0.0.1:8000/retail_erp`, confirmed separately to return
  `200` with real HTML). Result: `Could not start a debuggable Chrome:
  Launched Chrome (pid 67142) but discovery never answered on
  127.0.0.1:9222` — Chrome starts but never becomes CDP-debuggable,
  consistent with a minimal WSL container missing sandbox/GPU
  dependencies Chrome needs even in headless mode.
- **Impact:** Blocks the visual/interactive/responsive portion of Phase
  6 (18 workspace UI audit) and the mission's separate 6-breakpoint
  browser verification requirement. Does **not** block any backend/API/
  data verification — all of that was completed for all 18 workspaces
  (see `docs/ui/audits/SMJ_PHASE6_BACKEND_LAYER_AUDIT.md`).
- **Exact remediation options for the user:**
  1. Install Chrome's headless dependencies in this container
     (`apt-get install -y libnss3 libatk-bridge2.0-0 libgtk-3-0
     libgbm1 libasound2` — the typical missing set on minimal Debian/
     Ubuntu images; requires sudo, not attempted automatically per the
     "no sudo" mission rule), then retry `audit_live`.
  2. Enable a Playwright-based browser-automation tool for this session
     (if available in the harness) instead of `accesslint`.
  3. Perform a manual QA pass with a real browser (the method a prior
     session in this project used: a Windows-host Chrome via WSL
     interop) against the 18 workspaces × 6 breakpoints, using the
     project's existing E2E test file structure convention
     (`FRONTEND.md`) as the checklist.
- **Status:** Documented, confirmed via direct attempt, not silently
  worked around.

## Production-readiness external blockers (anticipated, not yet reached)

These are named in the mission prompt itself as things that cannot be
completed by local autonomous work regardless of how much code gets
written. Listed here pre-emptively so the final scorecard doesn't
mischaracterize them as coding gaps:

- Client UAT — requires the actual business owner/staff to use the system.
- Accountant sign-off — requires a qualified accountant to review the
  chart of accounts, tax setup, and financial reports against real
  regulatory requirements for a Sri Lankan wholesale business.
- Real staging hardware / HTTPS / off-server backups / monitoring /
  email configuration — requires real infrastructure and credentials
  this environment does not have and should not fabricate.
- Staff training, deployment rehearsal, rollback rehearsal — require
  scheduled time with real people, not code.
