# SMJ Print Format Security

| Control | Enforcement |
|---------|-------------|
| Overview/preview manager-gated | `_require_user_manager` |
| Preview needs document permission | `has_permission(dt, "print"/"read", doc=name)` |
| Cost fields hidden from unauthorised users | Frappe `get_print` honours field-level permissions |
| Only printable business DocTypes | allowlist `PRINTABLE_DOCTYPES`; others rejected |
| No arbitrary template execution here | HTML/Jinja authoring stays in gated Print Format CRUD |
| Format must match the DocType | preview validates `print_format.doc_type == doctype` |

**Purchase-price confidentiality:** a Sales-only user cannot see purchase/cost fields
in a printed Sales document because those fields are permission-restricted and
`get_print` omits them. This is standard ERPNext behaviour, relied on rather than
re-implemented.
