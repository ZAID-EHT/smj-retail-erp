# SMJ v1.0.0-rc2 Deployment Checklist

## Pre-deploy (verify)
- [ ] Branch `full-feature-parity`, worktree clean.
- [ ] `bench --site <site> migrate` runs clean (no pending patches).
- [ ] `cd frontend && npm run build` clean; assets deployed.
- [ ] 333 backend tests green (`bench --site <site> run-tests --app my_store_ui`).
- [ ] No credentials committed; no test users/items in the target site.

## Production configuration (external)
- [ ] **Enable the scheduler** (`bench --site <site> enable-scheduler`) — required for
      reservation-expiry release and scheduled jobs. (Staging shows it disabled.)
- [ ] Configure an **outgoing Email Account** with real SMTP credentials so welcome /
      reset emails send (System Operations → email status flips to configured).
- [ ] Set `developer_mode = 0`.
- [ ] Confirm HTTPS and production web server config.
- [ ] Schedule regular backups; copy offsite.

## First-time data (per business)
- [ ] Run `/retail-erp/setup` on the fresh site: create Company (CoA, warehouses,
      price lists auto-built).
- [ ] Load master data via `/admin/data` (Customer/Supplier/Item/Item Price).
- [ ] Enter **opening stock** via Stock Reconciliation against a **balance-sheet**
      account (NOT the Expense Stock Adjustment — see finance docs).
- [ ] Enter opening balances via standard opening tools.
- [ ] Accountant reviews P&L / Balance Sheet before go-live.

## Deploy
- [ ] Tag the release; deploy to Hetzner (separate, requires server credentials).
- [ ] Smoke-test `/retail-erp` login and Smart Sales on the production host.
