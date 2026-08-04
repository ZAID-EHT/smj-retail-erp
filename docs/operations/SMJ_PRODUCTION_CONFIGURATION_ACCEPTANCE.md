# Production Configuration — Acceptance

Route: `/retail-erp/admin/readiness/configuration` (System Manager only)
Module: `my_store_ui/production_configuration.py`
Tests: `my_store_ui/tests/test_production_configuration.py` — 17, all passing

## What it is

Thirty-two fixed-purpose checks across six groups, answering one question: is this
site configured to be production, and what is honestly unknown.

## What it deliberately is not

There is **no endpoint that accepts a command**. The check list is a tuple of named
zero-argument functions, and a test asserts none of them takes caller-supplied input.
A configuration checker that runs what the browser asks it to run is a remote shell
with a reassuring name.

## Statuses

| Status | Meaning |
|---|---|
| Pass | Verified here, now |
| Warning | Works, but not how production should look |
| Fail | Wrong; go-live should not proceed |
| External | Depends on somebody outside this system — **never Pass** |
| Not Applicable | Genuinely does not apply |

`External` is the load-bearing one. Without it, "restore drill" has to be either Pass
(a lie) or Fail (implying we broke it). With it the page says the true thing: nobody
here can answer.

Four items are permanently External and asserted as such by test: off-server backup
destination, restore drill, monitoring, and background-worker health.

## Groups and checks

| Group | Checks |
|---|---|
| Application | developer_mode off · allow_tests off · migrations complete · frontend assets built · required apps installed |
| Services | database reachable · Redis cache · Redis queue · scheduler enabled · background workers (External) |
| Business setup | company · active fiscal year · chart of accounts · cost centre · warehouses · selling price lists · buying price list · user accounts |
| Security | HTTPS hostname · no enabled test users · no enabled test warehouses · encryption key configured (presence only) |
| Operations | recent backup · off-server destination (External) · restore drill (External) · monitoring (External) · 24h error trend |
| Finance and approvals | opening-stock decisions · opening-stock correction posted · commission decisions · commission posting (N/A) · external go-live actions |

## Secret handling

The encryption-key check reports `configured` or `not configured` and never the value.
A test compares every check's detail text against the site's actual configured secrets
and fails if any appears.

## Measured result on staging.local, 2026-08-04

```
32 checks: 17 Pass · 3 Warning · 2 Fail · 9 External · 1 Not Applicable
production_ready: false
failing: Test mode disabled, Scheduler enabled
```

Both failures are correct and expected: `staging.local` runs with `allow_tests` on and
the scheduler disabled, because it is a test site. The checker is reporting accurately
that **staging is not production**, which is the behaviour wanted — a checker that
passed everything on a test site would be useless on a real one.

`production_ready` is false and will stay false while any External item remains, which
is by design. The nine External items map to entries in the External Actions tracker.

## Acceptance

- [x] Six groups all produce checks
- [x] Every check carries a valid status
- [x] Only `Fail` is treated as blocking
- [x] Externally-owned items never report Pass
- [x] Commission posting reports Not Applicable with the build-level reason
- [x] No secret value appears in any check detail
- [x] No endpoint accepts a command or shell string
- [x] Non-System-Manager access is refused
- [x] A failing check reports itself rather than taking the page down
- [x] The site does not claim to be production-ready
