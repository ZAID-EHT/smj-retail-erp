# SMJ Data Management Security

| Control | Enforcement |
|---------|-------------|
| Allowlisted DocTypes only | `ALLOWED_DOCTYPES`; arbitrary DocType raises ValidationError (tested) |
| Per-DocType permission | `frappe.has_permission` on every call |
| User Permissions / company scope on export | `frappe.get_list` (tested: permission-filtered) |
| No credential/secret in template or export | `FORBIDDEN_EXPORT_FIELDS` + Password fieldtype excluded (tested) |
| Row-count cap | 5,000 max (tested) |
| Import validation | standard Frappe Data Import (row-level) |
| Opening stock / balances | standard ERPNext mechanisms, no direct ledger write |
