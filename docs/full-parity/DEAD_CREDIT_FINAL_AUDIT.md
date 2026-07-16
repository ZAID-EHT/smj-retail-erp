# Dead-Credit Audit — Required-222 Mission

Per mission Section 5: before writing new code, check whether any of the
222 items already had a real working implementation the audit was failing
to credit, or a real bug preventing an intended credit from taking effect.

## Method

For every `document_action` entry in the 163-item list remaining after
Batch 1, the parent doctype's real, live `frappe.get_meta(doctype).
get_dashboard_data()` was loaded (the exact same source Desk's own
Connections sidebar and `frappe.desk.notifications.get_open_count` read)
and the scanner-detected action key was checked against every linked
doctype name in that config's `transactions` groups and `internal_links`
keys (both `frappe.scrub()`-normalised to match the scanner's own key
format). This is a precise, code-driven check, not a guess from button
labels — 20 of 159 remaining document-actions matched.

```
connection_matches_count: 20
connection_matches: [
  ("Blanket Order", "sales_order"), ("Lead", "prospect"),
  ("Material Request", "sales_order"), ("Material Request", "work_order"),
  ("Payment Order", "payment_entry"), ("Purchase Invoice", "payment_request"),
  ("Purchase Invoice", "purchase_order"), ("Purchase Invoice", "purchase_receipt"),
  ("Purchase Order", "material_request"), ("Purchase Order", "payment_request"),
  ("Purchase Order", "subcontracting_order"), ("Purchase Order", "supplier_quotation"),
  ("Purchase Receipt", "asset"), ("Purchase Receipt", "purchase_invoice"),
  ("Purchase Receipt", "purchase_order"), ("Quotation", "sales_order"),
  ("Supplier Quotation", "material_request"), ("Supplier Quotation", "request_for_quotation"),
  ("Supplier", "bank_account"), ("Supplier", "pricing_rule"),
]
non_matches_count: 139
```

## Outcome

**19 of 20 credited.** Each was added to `DOCTYPE_SPECIFIC_ACTIONS` in
`my_store_ui/audit/parity_registry.py` with a comment naming the exact
source `*_dashboard.py` file it came from, backed by the new generic
`get_dashboard_connections()` adapter (`my_store_ui/universal/api.py`),
verified against real site1 data. See commit `7f2aae1`.

**1 stayed pending**: `("Blanket Order", "sales_order")`. The credit rule
requires `parent in routed_doctypes` (the parent doctype must already have
a real Retail ERP route) — Blanket Order does not yet have one. The
`DOCTYPE_SPECIFIC_ACTIONS["Blanket Order"]` entry was still added (harmless
forward-looking addition, matching this codebase's existing convention of
pre-registering actions for not-yet-routed doctypes elsewhere), so this
will auto-credit the moment Blanket Order itself is routed — no registry
change will be needed at that point.

## Real bug found and fixed (not a scanner-mismatch, an actual code bug)

`DOCTYPE_SPECIFIC_ACTIONS` (a Python dict literal) contained two entries
keyed `"Supplier"`:

```python
"Supplier": {"hold", "resume"},                       # line 230 (original)
...
"Supplier": {"accounting_ledger", "accounts_payable"}, # line 292 (original)
```

Python dict literals silently let the later key win — the first entry was
completely discarded at import time. This means `Supplier.hold` and
`Supplier.resume` (real, working actions — `run_document_action` already
handles them at `universal/api.py:879`) were **never actually being
credited or served through the registry's `served` check**, even though
the code intent was clearly to include them. This was not caught by any
prior dead-credit pass because both entries individually looked correct in
isolation; only reading the whole dict at once revealed the collision.

**Fix**: merged into a single entry:
`"Supplier": {"hold", "resume", "accounting_ledger", "accounts_payable", "bank_account", "pricing_rule"}`.

**Impact**: `Supplier.hold`/`Supplier.resume` were not in the 222 or 163
required-missing lists (they must have been resolved through some other
path, or the scanner never flagged them as missing despite the dead code —
worth a follow-up check), so this fix did not move the headline count. It
is still a genuine correctness fix: the registry's evidence trail for
Supplier hold/resume was silently wrong before this commit, and is now
accurate. Recorded here per the mission's explicit instruction to document
every dead-credit finding, not only the ones that move the number.

## What was NOT found

No other duplicate-key bugs were found elsewhere in `DOCTYPE_SPECIFIC_
ACTIONS`, `MAPPED_ACTIONS`, `BUILT_ADAPTER_DOCTYPE_NAMES`,
`BUILT_ADAPTER_ACTIONS_BY_PARENT`, `WORKSPACE_OVERRIDES`, or
`PAGE_OVERRIDES` this session — each was read in full at least once while
tracing the classification logic, but a full line-by-line collision audit
(as opposed to the targeted checks above) was not run. Recommended as a
cheap first step for whoever continues this mission next, given how much
value the single Supplier collision above turned up.

The remaining 139 non-matched document-actions from the connections check
were not individually re-investigated for other kinds of dead credit
(e.g. an already-implemented `MAPPED_ACTIONS` entry whose internal key
just doesn't match the scanner's key, the exact pattern several entries in
`DOCTYPE_SPECIFIC_ACTIONS`'s existing comments describe having fixed in
prior sessions). That remains real, valuable, likely-productive work for
the next session before writing any new adapters — see
[REQUIRED_222_BATCH_LOG.md](REQUIRED_222_BATCH_LOG.md).
