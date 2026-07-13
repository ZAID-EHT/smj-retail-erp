# Priority report adapter

The Retail ERP report hub and viewer use a server-owned allowlist from
`my_store_ui.services.priority_registry.REPORT_GROUPS`. Vue can submit only the
filter names in `REPORT_FILTERS`; Link filter values are checked with normal
DocType and record permissions before the standard
`frappe.desk.query_report.run` adapter is called.

Returned Link and Dynamic Link cells are resolved in bounded batches. A custom
record URL is returned only when the current user can read the target record.
The response never supplies a Desk route to ordinary Retail ERP navigation.

The shared viewer supports required/default filters, formatted table rows,
tree indentation, report summaries, returned chart data, CSV export when the
reference DocType permits export, and browser Print Preview when print is
permitted. Prepared-report capability is displayed rather than bypassed.

PDF status is environment-derived. On `site1.local`, `wkhtmltopdf` is not on
`PATH`; no package was installed in this sprint. ERPNext PDF generation needs a
separately approved system-package installation before visual PDF verification.

