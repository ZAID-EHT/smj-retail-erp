# SMJ Finance Number Re-verification

Re-derived from authoritative ledger data on `staging.local`, 2026-07-27, via
`dev_scripts/reverify_finance_numbers.py` (read-only). Company `SMJ Retail ERP`,
currency LKR, fiscal year 2026-2027.

## The reported "impossible" figure does not exist in the repo

The mission brief flagged a reported corrected profit of **LKR 4,048,825,204**, which
is arithmetically impossible. A full search of the committed documentation
(`grep` across `docs/`, `AGENT_HANDOFF.md`) found **that figure nowhere** — every
finance document already uses the correct **4,048,006** (or "4.05M" in the release
notes). The impossible number is a **concatenation artifact** of two correct values:
corrected profit `4,048,`**006** and corrected expense `4,`**825,204** →
"4,048,825,204". No documentation change was required to remove it; it was never in
the repository.

## Authoritative figures (from GL, not documentation)

| Measure | Value | Source |
|---------|------:|--------|
| Income | 8,873,210 | `SUM(credit−debit)` over Income accounts |
| Expense (net) | **−6,995,496** | `SUM(debit−credit)` over Expense accounts (negative = the artifact) |
| **Profit before correction** | **15,868,706** | income − expense |
| Opening-stock credit on Stock Adjustment | **11,820,700** | GL, Stock Entry, ≤ 2025-07-01 |
| **Expected profit after correction** | **4,048,006** | 15,868,706 − 11,820,700 (arithmetic check ✓) |
| Expected expense after correction | **4,825,204** | −6,995,496 + 11,820,700 |
| Trial Balance debit | 68,293,914.30 | GL |
| Trial Balance credit | 68,293,914.30 | GL |
| Trial Balance balanced | **yes** | debit = credit |

`arithmetic_check`: `15868706.0 − 11820700.0 = 4048006.0` ✓

## Reliability / method

- Figures are computed **directly from `tabGL Entry`** (`is_cancelled=0`) grouped by
  account `root_type` — the ledger itself, the most authoritative source.
- The official Profit and Loss Statement report API was also invoked; its structured
  "Profit for the year" row is laid out differently across periods and the automated
  row-matcher returned `null`, so the **GL-derived figures above are used as
  authoritative** (they are the underlying ledger the report renders). The Trial
  Balance identity (debit = credit) independently confirms ledger integrity.

## Conclusion

All finance figures in the repository are **correct and internally consistent**. No
documentation arithmetic error exists to fix. The correction (moving 11,820,700 from
the Expense `Stock Adjustment` to Equity) reduces profit to the credible **4,048,006**
— see `SMJ_OPENING_STOCK_CONFIRMED_ROOT_CAUSE.md` and the correction package.
