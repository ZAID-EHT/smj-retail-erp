# SMJ Core Wholesale Workflow — Mission State

**Resumable state.** Machine-readable companion: `SMJ_CORE_WORKFLOW_MISSION_STATE.json`.
Do not rely only on conversation history — update this after every logical batch.

## Repository
- Starting branch: `full-feature-parity`
- Mission start commit: `e15c37e`
- **Recovery mission (2026-07-26) started from:** `e9e71e2`
- Recovery tag: `pre-smj-phase78-recovery-20260726-1740`
- Earlier recovery tag: `pre-smj-core-workflow-20260724-1140`
- Test site (all writes): `staging.local`
- Dev site (untouched): `site1.local`
- Backup taken before this session's write testing:
  `sites/staging.local/private/backups/20260726_174038-staging_local-*`
  (database.sql.gz 1.3 MiB, files.tar, private-files.tar, site_config json)

## Recovery status (2026-07-26)

The previous session ended with **valid-looking but entirely unverified** code in
the working tree. All of it has now been verified, corrected and committed. Nothing
was discarded, reset or rewritten from scratch.

### Worktree inventory found at recovery

| File | State on arrival | Outcome |
|------|------------------|---------|
| `my_store_ui/form_api.py` | modified, unverified | verified, **2 defects fixed**, committed `ba2e1dc` |
| `my_store_ui/tests/test_item_price_sync.py` | untracked | 7 → **14 tests**, committed `ba2e1dc` |
| `my_store_ui/access_management.py` | untracked | verified, **3 defects fixed**, committed `0667a5d` |
| `my_store_ui/tests/test_access_management.py` | untracked | 19 → **28 tests**, committed `eec512b` |
| `docs/ui/SMJ_SIMPLIFIED_ENTRY_FORMS.md` | modified | corrected + extended, committed `ba2e1dc` |
| `docs/execution/SMJ_CORE_WORKFLOW_BLOCKERS.md` | modified | corrected + extended, committed `ba2e1dc` |
| `my_store_ui/dev_scripts/_tmp_probe.py` | untracked scratch | removed (superseded by committed probes) |

No unrelated pre-existing files were touched.

## Scope map (prompt phases → this repo)
| Phase | Requirement | Primary code |
|-------|-------------|--------------|
| 1 | Customer-first Smart Sales | `frontend/src/pages/priority/SmartSalesPage.vue`, `my_store_ui/api.py` |
| 2 | Customer-specific pricing | `my_store_ui/api.py`, ERPNext pricing engine |
| 3 | Actual/Reserved/Available + concurrency | `my_store_ui/api.py`, `my_store_ui/wholesale/reservation.py` |
| 4 | FIFO valuation | Stock Settings + controlled staging test items |
| 5 | Purchase Order data + workflow | universal form engine + PO metadata |
| 6 | `+ Create` header menu | `frontend/src/components/shell/*`, route registry |
| 7 | Simplified entry forms **+ Item Price sync** | `form_api.py` |
| 8 | User/role/access management | `access_management.py`, `frontend/src/pages/priority/AccessControlPage.vue` |

## Defects found and fixed during recovery

1. **Item Price sync broke product creation for `Item Manager`.** `Item Price` is
   master data in stock ERPNext v15 (Sales/Purchase Master Manager only). The suite
   runs as Administrator, which bypasses permission checks, so it could not catch
   this. Now plans changes, gates on the exact permissions needed, fails atomically.
2. **`Wholesale Price List` was still `buying=1`.** ERPNext stamps list flags onto
   each `Item Price`, so the marked-up wholesale rate was selectable as a purchase
   cost. Now selling-only, after re-verifying zero references.
3. **Email status queried a non-existent column.** `Email Account` has no `disabled`
   field — every call raised `OperationalError (1054)` and took 4 tests with it.
4. **Self-lockout was possible.** Frappe protects only Administrator/Guest, so a
   System Manager could disable their own account or drop their own System Manager
   role and leave nobody able to undo it.
5. **Access Control was a dead route.** Not registered in the server-side
   `ROUTE_REGISTRY`, so the SPA's own guard resolved a working page to "not found".
6. **Optional route groups returned HTTP 500.** `unquote(None)` raises; a valid URL
   omitting an optional segment crashed. Latent for any future optional group.

Defects 1, 5 and 6 were found only by probing or real-browser verification — never
by the existing test suites.

## Upstream behaviour recorded (not a defect in this app)

`User.validate` calls `populate_role_profile_roles()` on **every** save, which clears
`roles` before re-applying the profile's. A direct role therefore cannot coexist with
an assigned Role Profile. Asserted in both directions by the acceptance suite and
stated inline on the Access Control screen.

## Safety invariants held this mission
- Writes only to `staging.local`; `site1.local` business data untouched.
- No `ignore_permissions=True` in any endpoint; standard ERPNext controllers only.
- No direct GL/SLE/Bin/outstanding writes; no Vue-side valuation.
- No sudo / killall / pkill / taskkill / Windows Chrome. The browser is closed
  through the Playwright API only.
- Every staging configuration change was re-verified as unreferenced first, and is
  applied by a script that refuses to act if that is no longer true.
- Test credentials are generated per run and never written to a document or a doc.
- All test fixtures removed afterwards; staging verified clean (0 `Item Price` rows,
  no residual test users).
