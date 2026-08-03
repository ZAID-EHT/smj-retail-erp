# SMJ Sales Team — Browser Verification Matrix

Linux-native Playwright Chromium, headless, driven against the live site. No
Windows Chrome, and every browser closed through the Playwright API.

```
PLAYWRIGHT_PATH=/home/zaidh/.npm/_npx/e41f203b7505f1fb/node_modules/playwright \
ERP_USER=… ERP_PW=… node e2e/sales_team.mjs
```

Credentials come from `dev_scripts/browser_check_user.create`, which prints a
per-run password to stdout and never writes it to a document or the repository.

## Results

| Harness | Checks | Failures |
|---|---|---|
| `e2e/sales_team.mjs` | **73** | 0 |
| `e2e/viewport_matrix.mjs` (six viewports) | **228** | 0 |
| `e2e/customer_picker.mjs` | **15** | 0 |
| `e2e/button_audit.mjs` | **10** | 0 |

The sales-team harness grew from 52 to 73 checks and the viewport matrix from 210
to 228 in this mission.

## Viewports

| Name | Size | Checks | Failures |
|---|---|---|---|
| desktop-1920 | 1920 × 1080 | 38 | 0 |
| desktop-1440 | 1440 × 900 | 38 | 0 |
| laptop-1024 | 1024 × 768 | 38 | 0 |
| tablet-768 | 768 × 1024 | 38 | 0 |
| mobile-390 | 390 × 844 | 38 | 0 |
| mobile-360 | 360 × 800 | 38 | 0 |

Pages added to the matrix in this mission: Sales Teams list, Sales Team form,
Commission Register. Each is checked at every viewport for horizontal overflow,
clipping, dead routes, HTTP 500s and console errors.

## What the sales-team harness proves

It builds its own data through the API — sales persons, a team, two customers, an
item, stock, an order, a delivery and an invoice — drives the real pages, then
removes what it created.

### Navigation and routing
- Sales Teams appears in the Sales menu, with the Retail ERP base path
- Clicking navigates without a full page reload
- Back and forward return to the page
- A direct URL and a refresh both work

### The team master
- List, search, filters, sort and pagination
- Create with the default 50 / 25 / 25 split
- Shares are preserved on reload, including an uneven 50/25/15/10
- Total allocation reads 100%
- Validation: shares off 100, duplicate people, missing manager

### Smart Sales
- Exactly one customer field
- The idle state shows before a customer is chosen
- Choosing a customer loads the team, manager, both representatives, the split, the
  rate and the 100% total
- A customer with no team shows the empty message rather than the previous
  customer's team
- The dropdown is not hidden behind another card
- **A Sales Manager is offered the override, and an override with no reason is
  refused in the browser as well as on the server**

### The frozen snapshot and commission
- The order freezes the customer's team, with the split totalling 100%
- **The order has a real value to earn on** — asserted explicitly, so a zero-priced
  fixture cannot make the commission checks pass vacuously
- The pool equals base × rate, and equals the expected 4,000
- The manager receives a share of the **pool** (2,000), not of the sale
- Editing the team master afterwards leaves the raised order untouched
- The frozen panel renders on Sales Order and Sales Invoice detail, naming the team
  and listing every member
- Customer detail shows the team card and the past orders with their teams

### Commission register
- The page renders, offers its filters and an export
- It lists the earned lines for the invoice just raised
- **The page does not scroll sideways** — the wide table scrolls inside its own box

### Permissions
- A restricted user does not see the Sales Teams navigation
- Navigating straight to the URL is denied
- The API refuses the same user with HTTP 403 — checked separately, because a
  hidden menu is not a security boundary

### Health
- No console errors
- No failed API requests

## Two harness defects found and fixed

1. **CSRF.** Frappe only starts enforcing CSRF once a page has booted and put a
   token in the session. API calls made after the first navigation were rejected
   with `CSRFTokenError`. The harness now captures `window.frappe.csrf_token` after
   boot and sends it on every later call.
2. **A vacuous pass.** The first version of the commission checks used a customer
   with no price list, so the order priced at zero and "pool equals base × rate"
   was 0 = 0. The fixture now uses the Wholesale Price List, and the harness
   asserts the base is greater than zero before checking any ratio.

## Cleanup

Every created Customer, Sales Team, Sales Person, Item and User is deleted at the
end. Submitted documents cannot be deleted and are left in place on staging by
design; they are disposable test-site data and are excluded from the register only
by their own team, not by any special case.
