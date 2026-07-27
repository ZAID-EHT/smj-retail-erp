# SMJ Data Import & Export

Route: `/retail-erp/admin/data` (System Manager gated). Backend:
`my_store_ui/data_management.py`. Tests: `test_data_management` (7, green).

## Allowlisted types

Customer, Supplier, Item, Item Price, Warehouse, Contact, Address. An arbitrary
DocType (User, GL Entry, Stock Ledger Entry, DocType, …) is **rejected server-side**.

## Workflow

1. Choose a data type (only allowlisted, permission-filtered types are shown).
2. Download a CSV template (safe importable fields only — no credential fields).
3. Fill it and import via standard **Frappe Data Import** (row-level validation and
   errors before commit).
4. Export current records to CSV (permission-filtered).
5. Review import history.

## Security

- Every call re-checks the caller's DocType permission.
- Export uses `frappe.get_list`, so role permissions, **User Permissions and company
  filters** all apply — a restricted user only exports what they may see.
- Credential/key/session fields are excluded from templates and exports.
- Export row count is capped (5,000).
- Opening stock uses standard ERPNext stock mechanisms; opening balances use standard
  accounting setup — never a direct GL write.
