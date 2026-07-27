# SMJ Retail ERP — v1.0.0-rc2 Release Notes

Branch: `full-feature-parity` · Candidate commit: `2b40c49`
Recovery tag: `pre-smj-final-readiness-20260726-1848`

## Highlights since rc1 / prior mission

### Stock reservation (now fully verified)
- **Live two-process concurrency** proven: 10 stock, two orders for 8 each reserve 10
  total, never 16; loser retries within bounds, no raw deadlock. (`test_reservation_concurrency`, live harness)
- **Continuous lifecycle trace**: receipt → SO → reserve → release → re-reserve →
  partial delivery → full delivery → return, Available = Actual − Reserved at every
  step. (`test_reservation_lifecycle`)

### Access & security
- **Complete role-denial matrix**: 9 non-manager roles × 10 endpoints all denied;
  no privilege escalation; disabled users cannot authenticate. (`test_role_denial_matrix`)

### Product
- **Seven remaining fields** added: Colour, Published, Purchase UOM, Selling UOM,
  Safety Stock, Default Warehouse, Reorder Level/Qty (child-table-backed, no dup on
  edit). Item Price sync preserved. (`test_product_fields`)

### New admin surfaces
- **First-time setup wizard** (`/setup`) — empty-system detection + standard-controller
  company creation.
- **Printing & Branding** (`/admin/printing`) — letter heads, formats, permission-safe preview.
- **Email & Notifications** (`/admin/email`) — truthful delivery status, templates, coverage.
- **Data Management** (`/admin/data`) — allowlisted, permission-filtered import/export.
- **System Operations** (`/admin/system`) — read-only health, readiness, backups.

### Finance
- **Opening-stock P&L overstatement** root-caused and a guarded, reversible correction
  built and reconciled via dry-run (profit 15.87M → 4.05M; Trial Balance balanced).
  Staging application held for accountant sign-off.

## Verification
- **333 backend tests / 42 modules — all green.**
- **Frontend build clean.**
- **Browser matrix 90/90 across six viewports.**

## Known external requirements
- SMTP credentials (email delivery). Onboarding works via admin-set passwords.
- MariaDB root password (isolated QA / fresh-install sites).
- Accountant sign-off (opening-stock reclassification booking).
- Hetzner/DNS (deployment).
