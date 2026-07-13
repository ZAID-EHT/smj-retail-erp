# Universal generated UX verification

Date: 2026-07-13  
Site: `site1.local`  
Scope: the existing 20 `generated_provisional` DocTypes only

## Shared implementation

- Server presentation configuration controls plural titles, descriptions,
  primary fields, default columns, up to five main filters and module accent.
- Metadata inference and safe universal defaults apply when presentation
  configuration is absent.
- List columns, filters and sort fields are independently allowlisted by the
  server. The browser may request no more than 12 visible columns.
- Forms preserve every readable required field, group metadata sections and
  place uncommon optional sections under Advanced.
- Details expose only permission-filtered fields and related records. All
  actions originate from the server registry.
- Collaboration adapters recheck parent document permissions before comments,
  files, assignments, sharing, tags, email or version-history reads.
- Print selection uses Frappe Print Formats, Letter Heads, print view and the
  protected standard PDF endpoint.

## Feature graduation result

| Feature | Administrator list/config | Existing non-Administrator | Graduation |
|---|---|---|---|
| Supplier | Pass | Pass | Provisional |
| Warehouse | Pass | Pass | Provisional |
| Lead | Pass | Pass | Provisional |
| Opportunity | Pass | Pass | Provisional |
| Project | Pass | Permission denied | Provisional |
| Asset | Pass | Pass | Provisional |
| Address | Pass | Pass | Provisional |
| Contact | Pass | Pass | Provisional |
| Territory | Pass | Pass | Provisional |
| Customer Group | Pass | Pass | Provisional |
| Supplier Group | Pass | Pass | Provisional |
| Item Group | Pass | Pass | Provisional |
| Brand | Pass | Pass | Provisional |
| UOM | Pass | Permission denied | Provisional |
| Sales Person | Pass | Pass | Provisional |
| Price List | Pass | Pass | Provisional |
| Mode of Payment | Pass | Pass | Provisional |
| Cost Center | Pass | Pass | Provisional |
| Department | Pass | Permission denied | Provisional |
| Designation | Pass | Pass | Provisional |

No permission was changed and no user was created. Guest API access was
rejected. A denial in this table is a correct permission result, not a defect.

No feature was graduated. Per-feature interactive create/edit/delete,
collaboration writes, complete action applicability, and browser checks at
1920/1440/1366/1280/1024/768/390/375/320 remain required. Static responsive
rules cover 1024, 768 and 390 breakpoints, with mobile cards below 768, but this
is not claimed as visual browser verification.

## PDF environment

`wkhtmltopdf` is not on the executable path. Frappe PDF rendering fails with:

```text
OSError: No wkhtmltopdf executable found: "b''"
```

The generated print dialog disables PDF download with a readable explanation.
Print Preview and browser print use standard Frappe routes. Installing a
supported wkhtmltopdf package requires separate machine-change approval.

## Remaining manual verification

- Run list, new, detail and edit routes at every requested desktop/mobile width.
- Verify keyboard and touch operation of filters, column chooser, child rows,
  print dialog and collaboration panels.
- Exercise file upload/removal, comment, assignment, share, tags and email on a
  disposable permitted record with transaction cleanup.
- Re-run PDF selection/download after wkhtmltopdf is approved and installed.
- Validate feature-specific Client Script behavior or register a special/custom
  adapter before graduating that feature.
