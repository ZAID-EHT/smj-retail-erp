# Accountant Decision — Permission and Segregation Matrix

How the Accountant Decision Centre decides who may do what, and why the boundaries fall
where they do. The authoritative source is `CAPABILITIES` in
`my_store_ui/finance/accountant_decisions.py`; this page explains it.

## Why capabilities rather than page permissions

Permissions are expressed per *action*, not per *page*. One person may legitimately hold
several roles, and the interesting question is never "can they open the screen" but "can
they be the one who approves this". A capability map answers the second question, and
every write re-checks it server-side. The page is not the boundary.

## The two app-created roles

| Role | Why it exists |
|---|---|
| `Retail Accountant` | Makes "the accountant" a grantable identity. Without it, the only way to express accountant approval is to let a System Manager assert it — which is the exact failure being designed out. |
| `Retail Finance Verifier` | Lets post-posting verification be someone other than whoever implemented the change. |

Both are created by `my_store_ui.patches.create_finance_decision_roles`, which runs in
`pre_model_sync` because the DocType's permission rows link to them. Both have
`desk_access = 0`; they are permission identities for the Retail ERP frontend, not a
second admin interface.

## Capability matrix

| Capability | System Manager | Accounts Manager | Accounts User | Retail Accountant | Retail Finance Verifier |
|---|---|---|---|---|---|
| View finance decisions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Prepare finance proposal | ✅ | ✅ | — | — | — |
| **Record accountant decision** | **❌** | **❌** | — | ✅ | — |
| Approve implementation | — | ✅ | — | ✅ | — |
| Prepare accounting draft | ✅ | ✅ | — | — | — |
| **Submit accounting correction** | **❌** | **❌** | **❌** | **❌** | **❌** |
| Verify after posting | — | ✅ | — | ✅ | ✅ |

### The two deliberate holes

**System Manager cannot record an accountant decision.** This is the point of the whole
design. An administrator can do almost anything else in this system; being able to also
record that an accountant approved something would make every approval unfalsifiable.
`CAPABILITIES[CAP_RECORD]` is `("Retail Accountant",)` and a test asserts System Manager
is absent from it.

**Nobody can submit an accounting correction.** `CAPABILITIES[CAP_SUBMIT_CORRECTION]` is
the empty tuple. `has_capability` returns `False` for an empty allowlist regardless of
who is asking, so this cannot be satisfied by granting roles. Submitting the correction
is a deliberate act performed with the accountant's authority through the guarded
`apply()` path, not something a browser session can reach.

## Segregation rules enforced in code

| Rule | Where enforced | Failure mode it prevents |
|---|---|---|
| The preparer of a proposal cannot record the decision on it | `RetailAccountantDecision._require_segregation` | Someone proposing a treatment and then approving their own proposal |
| Approval requires evidence (attachment or reference) | `_require_evidence_for_approval` | An "approved" record nobody actually signed |
| Approval requires a named accountant | `_require_evidence_for_approval` | Approval attributed to nobody |
| Rejection requires a reason | `_require_reason_for_rejection` | A silent rejection that cannot be answered |
| A decided record cannot be edited | `_guard_frozen_fields` | Rewriting history so a past approval reads differently |
| A decided record cannot be re-decided | `record_decision` | Overwriting an answer instead of superseding it |
| Implementation requires an approved decision | `mark_implemented` | Implementing something that was rejected or never reviewed |
| Verification requires implementation first | `mark_verified` | Verifying a change that was never made |

The segregation check compares `prepared_by` against `recorded_by` on the record itself,
so it holds even when one person genuinely holds both roles. Holding both roles lets you
act in either capacity — on *different* records.

## Lifecycle

```
Not Reviewed ──> Under Accountant Review ──> Approved ──────> Implemented ──> Verified
      │                    │                 Approved w/ Changes
      │                    v
      └──────────> Information Required
                           │
                           v
                       Rejected
```

`Approved`, `Approved with Changes`, `Implemented` and `Verified` are the statuses that
authorise downstream work. `Rejected` and every pre-decision status authorise nothing —
`approved_decision()` returns `None` for them, and so does a superseded record.

## Changing an answer

A decided record is never edited. `supersede_decision()` creates a new version at
`version_no + 1`, points the old record's `superseded_by` at it, and leaves the old
record's answer, accountant name and date exactly as they were. Queries for the live
answer filter on `superseded_by is not set`, so the moment a record is superseded it
stops authorising anything — including work that was already permitted under it.

`decision_history()` returns every version including superseded ones, in creation order.

## What the Centre does not do

- It does not post, submit, pay or cancel any accounting document.
- It does not enable commission posting. `posting_blockers()` still returns a non-empty
  list and `post_commission_payout()` still refuses, regardless of what is recorded here.
- It does not grant itself authority. Recording "approved" against the opening-stock
  correction does not make `apply()` run; that path has its own site allowlist, amount
  re-measurement, duplicate check and exact confirmation string.

## Test coverage

`my_store_ui/tests/test_accountant_decisions.py` — 45 tests. The majority assert
refusals: approval without evidence, rejection without reason, self-approval, System
Manager recording a decision, editing a decided record, re-deciding, implementing an
unapproved decision, verifying an unimplemented one, and an outsider reaching the Centre
at all.
