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
