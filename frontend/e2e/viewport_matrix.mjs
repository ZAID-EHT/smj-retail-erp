/**
 * Six-viewport browser verification for the Phase 7/8 surfaces.
 *
 * Uses Linux-native Playwright Chromium only, located through Playwright's own
 * chromium.executablePath() -- never a guessed path and never Windows Chrome.
 * The browser is always closed through the Playwright API; no process is ever
 * terminated by name.
 *
 *   BASE_URL   default http://127.0.0.1:8000   (staging.local is the default site)
 *   ERP_USER / ERP_PW  required -- no password is baked in
 *
 *   node e2e/viewport_matrix.mjs
 */

import { createRequire } from "node:module";

// ESM ignores NODE_PATH, and Playwright is not a dependency of this workspace
// (Chromium is already installed in ~/.cache/ms-playwright). Resolve through CJS
// so NODE_PATH or an explicit PLAYWRIGHT_PATH can point at the installed copy.
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const BASE = process.env.BASE_URL || "http://127.0.0.1:8000";
const USER = process.env.ERP_USER;
const PW = process.env.ERP_PW;

if (!USER || !PW) {
  console.error("ERP_USER and ERP_PW are required; this harness refuses to guess a password.");
  process.exit(2);
}

const VIEWPORTS = [
  { name: "desktop-1920", width: 1920, height: 1080, kind: "desktop" },
  { name: "desktop-1440", width: 1440, height: 900, kind: "desktop" },
  { name: "laptop-1024", width: 1024, height: 768, kind: "desktop" },
  { name: "tablet-768", width: 768, height: 1024, kind: "tablet" },
  { name: "mobile-390", width: 390, height: 844, kind: "mobile" },
  { name: "mobile-360", width: 360, height: 800, kind: "mobile" },
];

const ROUTES = [
  { path: "/retail-erp/home", label: "Home" },
  { path: "/retail-erp/smart-sales", label: "Smart Sales" },
  { path: "/retail-erp/inventory/products/new", label: "Product quick-create (18 fields)" },
  { path: "/retail-erp/sales/customers/new", label: "Customer quick-create (14 fields)" },
  { path: "/retail-erp/inventory/products", label: "Product list (SKU)" },
  { path: "/retail-erp/sales/customers", label: "Customer list (business nature)" },
  // Sales team and commission surfaces.
  { path: "/retail-erp/sales/teams", label: "Sales Teams" },
  { path: "/retail-erp/sales/teams?team=new", label: "Sales Team form" },
  { path: "/retail-erp/sales/commissions", label: "Commission Register" },
  { path: "/retail-erp/sales/commission-periods", label: "Commission Periods" },
  { path: "/retail-erp/sales/commissions/historical-review", label: "Historical Commission Review" },
  { path: "/retail-erp/admin/sales/commission-policy", label: "Commission Policy" },
  // Wholesale operations surfaces (sales, delivery, invoicing, payments, purchasing).
  { path: "/retail-erp/sales/transactions", label: "Wholesale transaction register" },
  { path: "/retail-erp/sales/orders", label: "Sales Orders" },
  { path: "/retail-erp/sales/delivery-notes", label: "Delivery Notes" },
  { path: "/retail-erp/sales/invoices", label: "Sales Invoices" },
  { path: "/retail-erp/finance/payments", label: "Payment Entries" },
  { path: "/retail-erp/purchases/orders", label: "Purchase Orders" },
  { path: "/retail-erp/purchases/receipts", label: "Purchase Receipts" },
  { path: "/retail-erp/purchases/invoices", label: "Purchase Invoices" },
  { path: "/retail-erp/purchases/suppliers", label: "Suppliers" },
  { path: "/retail-erp/admin", label: "Administration landing" },
  { path: "/retail-erp/admin/access-control/access", label: "Effective Access" },
  { path: "/retail-erp/admin/access-control/roles", label: "Roles" },
  { path: "/retail-erp/admin/users", label: "Users (generated)" },
  { path: "/retail-erp/admin/companies", label: "Companies" },
  { path: "/retail-erp/setup", label: "Setup wizard" },
  { path: "/retail-erp/admin/printing", label: "Printing & Branding" },
  { path: "/retail-erp/admin/email", label: "Email admin" },
  { path: "/retail-erp/admin/data", label: "Data Management" },
  { path: "/retail-erp/reports/scheduled", label: "Scheduled Reports" },
  { path: "/retail-erp/admin/system", label: "System Operations" },
  { path: "/retail-erp/admin/readiness", label: "Launch Readiness" },
  // Pages built for the ACCOUNT CREATION requirements.
  { path: "/retail-erp/finance/accounts", label: "Accounts workspace" },
  { path: "/retail-erp/reports/henderson-analysis", label: "Henderson Analysis" },
  { path: "/retail-erp/admin/print-formats", label: "Print Format administration" },
  { path: "/retail-erp/finance/payment-reconciliation", label: "Payment Reconciliation" },
  { path: "/retail-erp/finance/bank-reconciliation", label: "Bank Reconciliation" },
  { path: "/retail-erp/inventory/warehouse-stock?warehouse=Stores+-+SMJ", label: "Warehouse stock drill-down" },
  { path: "/retail-erp/sales/teams", label: "Sales Teams" },
  { path: "/retail-erp/sales/teams?team=new", label: "New Sales Team form" },
];

const results = [];
let failures = 0;

const browser = await chromium.launch({ headless: true });
console.log(`chromium executable: ${chromium.executablePath()}`);

try {
  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      ignoreHTTPSErrors: true,
    });

    // Authenticate once per context through the real login endpoint.
    const login = await context.request.post(`${BASE}/api/method/login`, {
      data: { usr: USER, pwd: PW },
    });
    if (!login.ok()) {
      throw new Error(`login failed at ${viewport.name}: HTTP ${login.status()}`);
    }

    for (const route of ROUTES) {
      const page = await context.newPage();
      const consoleErrors = [];
      page.on("console", (message) => {
        if (message.type() === "error") consoleErrors.push(message.text().slice(0, 200));
      });
      page.on("pageerror", (error) => consoleErrors.push(`pageerror: ${String(error).slice(0, 200)}`));

      let status = 0;
      try {
        const response = await page.goto(`${BASE}${route.path}`, {
          waitUntil: "domcontentloaded",
          timeout: 30000,
        });
        status = response ? response.status() : 0;
        await page.waitForTimeout(1200);

        const probe = await page.evaluate(() => {
          const doc = document.documentElement;
          const text = document.body ? document.body.innerText : "";
          return {
            overflow: doc.scrollWidth - doc.clientWidth,
            notFound: /page not found|route not found/i.test(text),
            denied: /permission denied/i.test(text),
            // Anything that leaks a stored secret into the DOM is a hard failure.
            leak: /password['"\s:=]+[^\s<]{8,}/i.test(text) && !/new password|confirm password|reset password|temporary password/i.test(text),
            headingCount: document.querySelectorAll("h1,h2,h3").length,
            smallTargets: Array.from(document.querySelectorAll("button,a[href],input,select"))
              .filter((el) => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0 && rect.height < 24;
              }).length,
          };
        });

        const problems = [];
        if (status >= 400) problems.push(`http ${status}`);
        if (probe.overflow > 1) problems.push(`h-overflow ${probe.overflow}px`);
        if (probe.notFound) problems.push("dead route");
        if (probe.leak) problems.push("possible secret in DOM");
        if (consoleErrors.length) problems.push(`console(${consoleErrors.length})`);

        if (problems.length) failures += 1;
        results.push({
          viewport: viewport.name,
          kind: viewport.kind,
          route: route.label,
          status,
          overflow: probe.overflow,
          denied: probe.denied,
          headings: probe.headingCount,
          smallTargets: probe.smallTargets,
          problems,
          consoleErrors: consoleErrors.slice(0, 3),
        });
      } catch (error) {
        failures += 1;
        results.push({
          viewport: viewport.name,
          kind: viewport.kind,
          route: route.label,
          status,
          problems: [`exception: ${String(error).slice(0, 160)}`],
          consoleErrors,
        });
      } finally {
        await page.close();
      }
    }
    await context.close();
  }
} finally {
  await browser.close();
}

const byViewport = {};
for (const row of results) {
  byViewport[row.viewport] = byViewport[row.viewport] || { pass: 0, fail: 0 };
  if (row.problems.length) byViewport[row.viewport].fail += 1;
  else byViewport[row.viewport].pass += 1;
}

console.log("\n=== VIEWPORT MATRIX ===");
for (const [name, counts] of Object.entries(byViewport)) {
  console.log(`  ${name.padEnd(14)} pass=${counts.pass} fail=${counts.fail}`);
}
console.log("\n=== PROBLEMS ===");
const problemRows = results.filter((row) => row.problems.length);
if (!problemRows.length) console.log("  none");
for (const row of problemRows) {
  console.log(`  [${row.viewport}] ${row.route}: ${row.problems.join(", ")}`);
  for (const message of row.consoleErrors || []) console.log(`      ${message}`);
}
console.log(`\ntotal checks=${results.length} failures=${failures}`);
process.exit(failures ? 1 : 0);
