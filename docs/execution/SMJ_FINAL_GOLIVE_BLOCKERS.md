# SMJ Final Go-Live — External Blockers

Only genuine external requirements belong here. Unfinished development is **not** an
external blocker and is never recorded on this page.

Each entry states the exact requirement, the exact owner action, and what the system
already did so the owner does not repeat local work.

## Status legend

| Status | Meaning |
|---|---|
| Credential Required | Work is complete locally; a secret or access token is missing |
| Awaiting Approval | A human decision is required before anything may be posted |
| Human Action Required | A person must perform or witness the step |
| Infrastructure Required | A server, DNS record or registry must exist first |

## Blockers carried into this mission

These were already recorded before this mission and are re-stated here so the final
handoff is a single page.

| ID | Category | Requirement | Owner action | Status |
|---|---|---|---|---|
| EXT-01 | Accounting | Opening-stock correction of LKR 11,820,700 may not be submitted by any automated process | Accountant reviews the correction package, records a decision with evidence, then authorises posting | Awaiting Approval |
| EXT-02 | Accounting | Commission accounting model (earning trigger, basis, expense account, payable account, payee party type, payout document, withholding, tax, clawback) is not chosen by the software | Accountant selects each value in the decision package and signs it | Awaiting Approval |
| EXT-03 | Database | Fresh-install rehearsal needs MariaDB administrative credentials to create a new site | Owner supplies MariaDB root access, or runs the rehearsal script themselves | Credential Required |
| EXT-04 | Email | Real outbound SMTP credentials are not present | Owner supplies SMTP host, port, user and password for the production domain | Credential Required |
| EXT-05 | Infrastructure | Hetzner server does not exist in this environment | Owner provisions the server and supplies SSH access | Infrastructure Required |
| EXT-06 | Infrastructure | Container registry credentials are absent | Owner supplies registry URL and push credentials | Credential Required |
| EXT-07 | Infrastructure | DNS records are not controlled from here | Owner creates the A/AAAA records for the production hostname | Infrastructure Required |
| EXT-08 | Infrastructure | HTTPS certificate issuance depends on DNS and a live host | Follows EXT-05 and EXT-07 | Infrastructure Required |
| EXT-09 | Operations | Off-server backup destination is not configured | Owner supplies the destination and its credentials | Credential Required |
| EXT-10 | Operations | Restore drill against real infrastructure needs a live target | Follows EXT-05 | Infrastructure Required |
| EXT-11 | UAT | Human client UAT cannot be performed by software | Client testers execute the UAT pack and sign each case | Human Action Required |
| EXT-12 | Approval | Management go-live approval is a human decision | Management signs the cutover authorisation | Human Action Required |
| EXT-13 | Git | Pushing commits and tags needs push credentials | Owner pushes the branch and tags | Credential Required |

## Blockers discovered during this mission

Recorded as they are found, with the evidence that established them.

_(none recorded yet — this mission is in progress)_

## Explicitly not blockers

- Anything that is merely unwritten code.
- Anything that failed because a test was not yet written.
- Anything that could be completed locally but was skipped for time.
