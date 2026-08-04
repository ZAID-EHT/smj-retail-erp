# Opening Stock Correction — Final Accountant Review Package

**Status: awaiting accountant decision. Nothing has been posted.**
**Measured on staging.local, 2026-08-04. Company: SMJ Retail ERP.**

This package exists so an accountant can decide without reading the codebase. Every
figure below was re-measured from the ledger for this package rather than copied from
an earlier document — and that re-measurement changed one of the headline numbers.

---

## Read this first: a previously published figure is out of date

Earlier finance documents state that profit after correction will be **4,048,006**.
That figure was correct when it was written on 2026-07-27, and it is **wrong now**.

| | Then (2026-07-27 docs) | Now (measured 2026-08-04) |
|---|---|---|
| Profit before correction | 15,868,706 | **17,418,706** |
| Correction amount | 11,820,700 | **11,820,700** (unchanged) |
| Profit after correction | 4,048,006 | **5,598,006** |

The correction amount has not moved. The *starting* profit has, because staging took on
further trading activity between 2026-07-27 and 2026-08-04 (a difference of 1,550,000 in
profit before). The arithmetic in the old document was sound; its inputs simply aged.

**Do not approve against 4,048,006.** The figure to reconcile to after posting on this
data set is **5,598,006**. Documents still carrying the old number are listed at the end
of this package.

This is also the reason the correction tool re-measures the ledger every time it runs
and refuses to proceed when the ledger disagrees with it, rather than trusting a
constant.

---

## 1. Root cause

Three Material Receipt Stock Entries credited the value of opening inventory to the
**expense** account `Stock Adjustment - SMJ` instead of an equity account.

The effect: opening inventory was brought in as a *negative expense*, which understates
cost of sales and therefore overstates profit by the full opening value. Total expense
currently measures **−7,745,496** — a negative total expense is not a plausible trading
result and is the visible symptom.

| Voucher | Type |
|---|---|
| `MAT-STE-2026-00001` | Stock Entry (Material Receipt) |
| `MAT-STE-2026-00002` | Stock Entry (Material Receipt) |
| `MAT-STE-2026-00003` | Stock Entry (Material Receipt) |

All three post on or before the opening date `2025-07-01`.

---

## 2. The proposed correction

A single reclassification Journal Entry:

```
Dr  Stock Adjustment - SMJ          11,820,700.00     (removes the P&L artifact)
Cr  Opening Balance Equity - SMJ    11,820,700.00     (records it as opening equity)
```

- **Proposed posting date:** `2025-07-01` (the opening date)
- **Amount:** `11,820,700.00`, measured from the GL, not typed in
- **Document:** one Journal Entry through the standard ERPNext controller

No stock document is cancelled. No Stock Ledger Entry is written, amended or re-posted.

---

## 3. Measured position — before

Source: `opening_stock_correction.inspect()` against staging.local on 2026-08-04.

| Measure | Value |
|---|---|
| Income | 9,673,210.00 |
| Expense | −7,745,496.00 |
| **Profit** | **17,418,706.00** |
| Trial balance — debit | 70,743,914.30 |
| Trial balance — credit | 70,743,914.30 |
| Trial balance balanced | Yes |
| Overstatement measured on `Stock Adjustment - SMJ` | 11,820,700.00 |
| Correction already submitted | None |
| Correction draft already existing | None |

---

## 4. Expected position — after

Source: `opening_stock_correction.dry_run()`, which builds and submits the entry inside
a savepoint and then rolls it back. Nothing persisted; `persisted: false`.

| Measure | Before | After | Change |
|---|---|---|---|
| Income | 9,673,210.00 | 9,673,210.00 | none |
| Expense | −7,745,496.00 | 4,075,204.00 | +11,820,700.00 |
| **Profit** | **17,418,706.00** | **5,598,006.00** | **−11,820,700.00** |
| Trial debit | 70,743,914.30 | 82,564,614.30 | +11,820,700.00 |
| Trial credit | 70,743,914.30 | 82,564,614.30 | +11,820,700.00 |
| Balanced | Yes | Yes | stays balanced |

Profit falls by exactly the correction amount, and by nothing else. Expense becomes
positive, which is the point of the exercise.

---

## 5. Proof there is no stock impact

| Measure | Value at measurement | Effect of the correction |
|---|---|---|
| Stock Ledger Entries (active) | 573 | unchanged — a Journal Entry creates none |
| Total stock value | 20,382,196.00 | unchanged |
| Total bin quantity | 4,729.000 | unchanged |

The correction moves an amount between two GL accounts. It does not touch a stock
document, so there is no valuation change and no reposting cascade. This is the reason
a reclassification was chosen over cancelling and re-entering the three receipts.

---

## 6. Risk and rollback

| Risk | Assessment |
|---|---|
| Wrong amount posted | The tool re-measures the ledger and refuses if it disagrees with 11,820,700 |
| Posted twice | Refuses when a correction Journal Entry already exists |
| Posted to the wrong site | Refuses on `site1.local`; refuses on any site not explicitly allowlisted |
| Posted to the wrong company | Company is resolved from the ledger, and the accounts are validated against it |
| Stock disturbed | Not possible — no stock document is involved |
| Trial balance broken | Dry run confirms balanced before and after |

**Rollback:** the correction is a single Journal Entry. If it is posted and later judged
wrong, cancel it through the standard ERPNext cancellation path. There is no cascade to
unwind because nothing downstream depends on it.

**Backup:** a full staging backup with files was taken before this mission
(`20260804_165748`, SHA256 recorded in `docs/execution/SMJ_FINAL_GOLIVE_STATE.md`).

---

## 7. What the software will and will not do

| Action | Available | Notes |
|---|---|---|
| `inspect` — read the current position | Yes | read-only |
| `dry_run` — prove the result in a rolled-back savepoint | Yes | nothing persists |
| `prepare_draft` — create a **draft** Journal Entry for review | Yes | `docstatus 0`, not submitted |
| `verify_after` — reconcile once a correction has been posted | Yes | read-only |
| `apply` — submit the correction | **Guarded** | requires the exact confirmation string `11820700.0:APPROVED`, an allowlisted site, and a recorded accountant approval |

No scheduled job, no migration, no test and no API reachable from the browser submits
this entry. Submission is a deliberate act performed with the accountant's authority.

---

## 8. Accountant decision

Four questions are recorded in the Accountant Decision Centre at
`/retail-erp/admin/finance/decisions`. Each is a separate record so that a change to one
does not silently re-open the others.

| # | Question | System proposal | Decision |
|---|---|---|---|
| 1 | Which accounts carry the reclassification? | Dr `Stock Adjustment - SMJ` / Cr `Opening Balance Equity - SMJ` | ☐ Approved ☐ Approved with changes ☐ Rejected |
| 2 | Is 11,820,700.00 the amount to correct? | Yes — measured from GL | ☐ Approved ☐ Approved with changes ☐ Rejected |
| 3 | On what date is it posted? | 2025-07-01 | ☐ Approved ☐ Approved with changes ☐ Rejected |
| 4 | Is submission authorised? | Not proposed — this is the accountant's call | ☐ Approved ☐ Rejected |

**Approval requires evidence.** The Centre refuses an approval with no attachment or
reference, refuses a rejection with no reason, and refuses to let whoever prepared the
proposal record the decision on it.

Accountant name: ............................................................

Signature / reference: ......................................................

Date: ...................  Effective date: ...................

---

## 9. Verification checklist — after posting

Run `verify_after()` and confirm each line.

- [ ] Exactly one submitted correction Journal Entry exists
- [ ] Its amount is 11,820,700.00
- [ ] Profit now reads **5,598,006.00** (re-measure; do not assume if further trading has been posted since)
- [ ] Total expense is positive
- [ ] Trial balance debit equals credit
- [ ] Balance Sheet balances
- [ ] Stock Ledger Entry count unchanged at 573
- [ ] Total stock value unchanged at 20,382,196.00
- [ ] Total bin quantity unchanged at 4,729.000
- [ ] The four decision records move to Implemented, then Verified

---

## 10. Documents still carrying the superseded 4,048,006 figure

These were accurate when written and are now stale on this data set. They are listed
rather than silently rewritten, because several are historical mission records whose
value is that they say what was true at the time.

- `docs/finance/SMJ_FINANCE_NUMBER_REVERIFICATION.md`
- `docs/finance/SMJ_STAGING_CORRECTION_RUNBOOK.md`
- `docs/execution/SMJ_PRODUCTION_READINESS_SCORECARD.md`
- `docs/execution/SMJ_FINANCE_DEPLOYMENT_FINAL_REPORT.md`
- `docs/execution/SMJ_FINANCE_DEPLOYMENT_MISSION_STATE.md` / `.json`
- `docs/execution/SMJ_FINAL_PRODUCTION_READINESS_REPORT.md`
- `docs/execution/SMJ_REMAINING_EXTERNAL_ACTIONS.md`
- `docs/full-parity/VERIFICATION_MATRIX.md`, `PROGRESS.md`, `DECISIONS.md`, `BLOCKERS.md`

**This package is the authoritative figure of record.** Where it disagrees with any of
the above, this package wins, and the correct action before posting is to re-measure
again rather than to trust either document.
