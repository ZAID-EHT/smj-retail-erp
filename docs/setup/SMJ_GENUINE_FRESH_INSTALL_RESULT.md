# SMJ Genuine Fresh-Install Result

Script: `scripts/verify_fresh_install.sh`
Last exercised: 2026-08-04

## Status: dry run passed. A real fresh install has **not** been performed.

That distinction is the point of this page. The script existing is not a rehearsal,
and a dry run that creates nothing is not proof the install works. Both are useful;
neither is the thing.

| | State |
|---|---|
| Script exists and is syntax-clean | Yes (`bash -n`) |
| Guards exercised, not merely read | Yes |
| `--dry-run` executed | Yes — passed, created nothing, asked for no credential |
| `--create` executed against a real empty site | **No — MariaDB administrative credential unavailable** |
| Machine-readable result produced | Yes |

## Modes

| Mode | Behaviour |
|---|---|
| `--dry-run` | Runs every guard, reports exactly what would happen, creates nothing, needs no database credential. The only mode safe to run unattended. |
| `--create` | Creates the new site, installs apps, migrates, drives setup, creates two companies. |
| `--verify` | Re-checks an existing rehearsal site. Refuses if the site does not exist. |
| `--resume` | Continues against an existing site after a failure. |

**There is no default mode.** Invoking the script without one exits 2 with usage.
Defaulting to `--create` would mean a mistyped flag creates a site, which is the one
outcome worth being pedantic about.

## Guards, as exercised

```
$ scripts/verify_fresh_install.sh freshrelease.local
usage: ... --dry-run|--create|--verify|--resume <new-site-name>
exit=2                                    # no mode -> refuses

$ scripts/verify_fresh_install.sh --dry-run staging.local
REFUSING: staging.local is protected. Use a NEW site name.
exit=3                                    # protected site -> refuses

$ scripts/verify_fresh_install.sh --dry-run freshrelease.local
original default site: staging.local (will restore at end)
== guards passed for freshrelease.local ==
would create site:      freshrelease.local
would install apps:     erpnext my_store_ui
would migrate, then verify setup status
would create companies: Fresh Test Co, Fresh Test Co Two
would restore default:  staging.local
would NOT delete the site afterwards
NOTE: no site was created and no database credential was requested.
result written: /home/zaidh/frappe-bench/logs/fresh_install_result.json
restored default site: staging.local
exit=0
```

Also verified by reading the script:

- `staging.local` and `site1.local` are refused by name
- an existing site is refused for `--create`
- a missing site is refused for `--verify` and `--resume`
- the MariaDB password comes from env or an unechoed prompt, and is never printed
- the original default site is restored through an `EXIT` trap, so it is restored
  even when the run fails
- a failed rehearsal site is **not** deleted, so it can be inspected
- no site is ever dropped automatically; removal is a manual, deliberate command

## Machine-readable result

Written to `$BENCH_DIR/logs/fresh_install_result.json` — outside the app repository,
because a rehearsal is a run artifact and not source.

```json
{
  "site": "freshrelease.local",
  "mode": "dry-run",
  "status": "dry-run-ok",
  "steps_ok": 1,
  "steps_failed": 0,
  "finished_at": "2026-08-04T12:33:36Z"
}
```

The setup-flow code the script drives is separately covered by `test_setup_wizard`,
which creates a company through the standard controller inside a savepoint.

## What `--create` does when a credential is available

1. Create a fresh empty site, install `erpnext` and `my_store_ui`, migrate.
2. `get_setup_status` → confirm `setup_required = true` (no company).
3. `create_company` (standard controller builds CoA, cost centre, warehouses, price
   lists) → first company.
4. `create_company` again → second company, for multi-company separation.
5. `get_setup_status` → confirm setup complete.

## What a real rehearsal still has to prove

The steps above are what the script automates. The following are named in the go-live
requirements and are **not yet covered by it**, so they remain manual runbook steps
rather than automated assertions:

- Customer, Supplier, Product and Item Price creation
- Opening stock
- Sales Order, Purchase Order and Payment
- Printing and PDF output
- User permission checks and disabled-user denial
- Two-company end-to-end separation on the fresh site

They are listed rather than quietly omitted, because a rehearsal reporting COMPLETE
while never having created a sales order is the more dangerous kind of green.

## External requirement

**EXT-03 — MariaDB administrative credential.** Owner: Ops.

Supply `MARIADB_ROOT_PASSWORD` (or run interactively) and execute:

```
scripts/verify_fresh_install.sh --create freshrelease.local
scripts/verify_fresh_install.sh --verify freshrelease.local
```

Then, in a browser on the fresh site, confirm `/retail-erp` redirects to
`/retail-erp/setup`, complete the wizard, add master data and run a sales and a
purchase order.

Until then this page says dry run only. The External Actions tracker carries EXT-03
as `Credential Required` and EXT-04 as `Not Started`.
