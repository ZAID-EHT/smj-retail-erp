# SMJ Retail ERP — Home Workspace: Deep Browser Evidence

**Date:** 2026-07-18 · **Method:** real Linux-native Playwright Chromium,
authenticated as Administrator via the actual login form. Evidence:
`docs/ui/evidence/runtime/interactions-2026-07-17T22-21-01-510Z/`.

Home is audited in the most depth of the 18 workspaces because it is the
landing page every user sees first and hosts the widest variety of
component types (KPI cards, charts, donut legends, quick actions,
navigation, search) in one screen.

## Surface sweep (all 6 viewports)

Part of the 108-point sweep in `SMJ_BROWSER_VERIFICATION.md`: 0 overflow,
0 console errors, 0 failed requests at every viewport. 15 buttons, 41
links, 1 table detected at 1440×900.

## Interactive elements — real click-through, not just "the button exists"

| Element | interaction → result |
|---|---|
| Module nav dropdown/chevron | Clicked → a real teleported dropdown menu became visible (`dropdownVisible: true`) |
| Global search | Typed "customer" → a real results dropdown became visible (`resultsVisible: true`) |
| User menu (avatar/profile button) | Clicked → a real menu became visible (`menuVisible: true`) |
| KPI card | Clicked → real navigation occurred, `/home` → `/sales/invoices` (`navigated: true`) — confirms KPI cards are genuinely wired to their target workspace, not decorative |
| Keyboard Tab (×3 presses) | Focus landed on a real `<a>` element with a visible focus ring (`box-shadow: rgba(139, 184, 255, 0.55) 0px 0px 0px 3px`) — accessible focus state confirmed present, not `outline: none` with no replacement |

## The two previously-uncertain mobile CSS issues (resolved here)

At 390×844, using real `getComputedStyle()`/`getBoundingClientRect()`
queries against the live rendered page (not a screenshot diff):

- **"View Report" link** (Sales Trend chart card): right edge at 123px,
  viewport 390px wide. Not clipped.
- **Payment Collection donut legend** (3 items: Collected 64% / Pending
  0% / a third entry): all three items' right edges at 349px (within the
  390px viewport), and each item's amount value (`<b>` element) also
  fully visible (rightmost at 319px). Not clipped.

Both are genuinely fixed — see `SMJ_RESPONSIVE_RESULTS.md` for the full
comparison against the 2026-07-16 session's uncertainty.

## Error and permission behavior

- Navigating to a non-existent Sales Order
  (`/sales/orders/SAL-ORD-9999-99999`) serves a real page with intact
  navigation (header, module links, breadcrumb showing "Sales Order")
  rather than a blank screen or a raw stack trace — confirmed via
  `invalid_record_error.png` and the captured body text.
- A second, real restricted account (`Sales User` role only, no
  Administrator/System Manager) was created, logged in through the real
  UI, and used to load `/admin`. Result: the navigation menu correctly
  omits Purchases/Operations/Admin (role-filtered server-side), and the
  page itself renders a genuine "Permission Denied — You do not have
  permission to use this Retail ERP feature" message rather than
  crashing, leaking data, or silently rendering the admin page anyway.
  This is the first time in this project's history this specific
  check (permission-denied *behavior*, not just backend permission
  *config*) has been verified in a real browser — the 2026-07-16 session
  explicitly flagged this as untested ("only Administrator... was
  available to test with").

## Truthful status

All items above: **browser_verified**. Nothing in this document is
inferred from source code or HTTP responses alone.
