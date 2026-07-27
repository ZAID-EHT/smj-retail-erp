# SMJ Notification Acceptance

`get_notification_coverage()` reports, for each core wholesale event (Sales Order,
Sales Invoice, Payment Entry, Delivery Note, Purchase Order, Material Request),
whether an **enabled** standard Frappe Notification exists.

| Aspect | Status |
|--------|--------|
| Coverage report | implemented + tested (`test_email_admin`) |
| Template listing | implemented (name + subject) |
| Notification listing | implemented (with wholesale-relevance flag) |
| Actually sending a notification | **requires configured SMTP** (external) |

Sending real notifications depends on a configured outgoing Email Account (external).
The coverage and template review are available now so an administrator can prepare the
content before SMTP is connected.
