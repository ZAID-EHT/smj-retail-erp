# SMJ Final Readiness — Blockers

## Environment limitations (not code defects)

### QA/fresh site creation requires MariaDB root password
- **Requirement:** `bench new-site financefix.local` and `bench new-site freshsetup.local`
  need `--mariadb-root-password`. No root password exists in any site config, and
  guessing it is (correctly) blocked in this environment.
- **Owner steps to unblock:** provide the local MariaDB root password (or run
  `bench new-site financefix.local --db-root-password <pw>` themselves), then this
  mission's guarded correction/setup scripts can be replayed on the QA site.
- **Mitigation applied:** Phase 6 uses a read-only audit on staging plus a dry-run,
  reversible, savepoint-verified correction; Phase 7 builds the wizard against the
  real ERPNext Company controller and unit-tests the empty-system code path.

## External requirements (not completable from this repository)

### Real SMTP credentials
- No outgoing `Email Account` exists on staging. Welcome/reset email cannot be
  delivered. Onboarding uses an administrator-set password. Owner must create an
  Email Account with working SMTP credentials (Phase 9 builds the safe admin UI for
  it, but cannot supply the credentials).

### Accountant / business-owner sign-off
- The opening-stock financial correction (Phase 6) is applied and reconciled
  technically, but the final acceptance of corrected figures is an accountant
  judgement recorded as external sign-off.

### Hetzner / DNS / deployment
- Out of scope for this repository; recorded in the release deployment checklist.
