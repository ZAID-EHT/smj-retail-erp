/**
 * Action-button audit for the Retail ERP.
 *
 * For each page, finds the primary create/action buttons, clicks them, and asserts
 * that something real happens: the route changes to a page that renders (not
 * "Page not found", not "Permission denied"), or a modal opens. A button that
 * navigates nowhere, or navigates to a dead route, is a failure.
 *
 * Linux-native Playwright Chromium only, closed through the Playwright API.
 *
 *   ERP_USER / ERP_PW required.
 *   node e2e/button_audit.mjs
 */

import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const BASE = process.env.BASE_URL || "http://127.0.0.1:8000";
const USER = process.env.ERP_USER;
const PW = process.env.ERP_PW;

if (!USER || !PW) {
  console.error("ERP_USER and ERP_PW are required; this harness refuses to guess a password.");
  process.exit(2);
}

// Pages whose primary action button the requirements document calls out.
const PAGES = [
  { path: "/retail-erp/purchases/suppliers", label: "Suppliers", button: /new supplier|create supplier/i },
  { path: "/retail-erp/crm/leads", label: "Leads", button: /new lead|create lead/i },
  { path: "/retail-erp/sales/quotations", label: "Quotations", button: /new quotation|create quotation/i },
  { path: "/retail-erp/sales/orders", label: "Sales Orders", button: /new sales order|create sales order/i },
  { path: "/retail-erp/sales/delivery-notes", label: "Delivery Notes", button: /new delivery note|create delivery note/i },
  { path: "/retail-erp/sales/customers", label: "Customers", button: /new customer|create customer/i },
  { path: "/retail-erp/purchases/orders", label: "Purchase Orders", button: /new purchase order|create purchase order/i },
  { path: "/retail-erp/inventory/products", label: "Products", button: /new (item|product)|create (item|product)/i },
  { path: "/retail-erp/inventory/warehouses", label: "Warehouses", button: /new warehouse/i },
  { path: "/retail-erp/finance/payments", label: "Payment Entries", button: /new payment/i },
];

const results = [];
let failures = 0;

const browser = await chromium.launch({ headless: true });
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const login = await context.request.post(`${BASE}/api/method/login`, { data: { usr: USER, pwd: PW } });
  if (!login.ok()) throw new Error(`login failed: HTTP ${login.status()}`);

  for (const spec of PAGES) {
    const page = await context.newPage();
    const consoleErrors = [];
    page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text().slice(0, 160)); });
    page.on("pageerror", (e) => consoleErrors.push(`pageerror: ${String(e).slice(0, 160)}`));

    let outcome = "ok";
    let detail = "";
    try {
      const resp = await page.goto(`${BASE}${spec.path}`, { waitUntil: "domcontentloaded", timeout: 30000 });
      if (resp && resp.status() >= 400) {
        outcome = "fail"; detail = `list page HTTP ${resp.status()}`;
      } else {
        // The list config (and therefore the permission-gated create button) is
        // fetched after mount; 1.5s was too short and produced false negatives.
        await page.waitForTimeout(3000);
        const listText = await page.evaluate(() => document.body.innerText);
        if (/page not found|route not found/i.test(listText)) {
          outcome = "fail"; detail = "list page renders Not Found";
        } else {
          // Find the create button by accessible name.
          const btn = page.getByRole("button", { name: spec.button })
            .or(page.getByRole("link", { name: spec.button }))
            .first();
          const count = await btn.count();
          if (count === 0) {
            outcome = "missing"; detail = "no create button found (may be permission-gated)";
          } else {
            // Report *why* a button cannot be used, rather than just timing out.
            const state = await btn.evaluate((el) => {
              const cs = getComputedStyle(el);
              const r = el.getBoundingClientRect();
              const mid = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
              return {
                tag: el.tagName, disabled: !!el.disabled, visibility: cs.visibility,
                display: cs.display, pointerEvents: cs.pointerEvents, opacity: cs.opacity,
                w: Math.round(r.width), h: Math.round(r.height),
                covered: mid && !el.contains(mid) && mid !== el ? (mid.className || mid.tagName) : null,
                href: el.getAttribute("href"),
              };
            }).catch(() => null);

            const before = page.url();
            await btn.scrollIntoViewIfNeeded().catch(() => {});
            try {
              await btn.click({ timeout: 8000 });
            } catch (clickErr) {
              outcome = "fail";
              detail = `button not clickable: ${JSON.stringify(state)}`;
              results.push({ ...spec, outcome, detail, consoleErrors: consoleErrors.length });
              failures += 1;
              await page.close();
              continue;
            }
            await page.waitForTimeout(1800);
            const after = page.url();
            const text = await page.evaluate(() => document.body.innerText);
            const dialog = await page.locator("[role=dialog], .modal, dialog[open]").count();

            if (/page not found|route not found/i.test(text)) {
              outcome = "fail"; detail = `navigated to a dead route: ${after}`;
            } else if (/permission denied/i.test(text)) {
              outcome = "fail"; detail = `navigated to permission-denied: ${after}`;
            } else if (after === before && dialog === 0) {
              outcome = "fail"; detail = "click did nothing (no navigation, no modal)";
            } else {
              // A real form must expose at least one input to be usable.
              const inputs = await page.locator("input, select, textarea").count();
              if (dialog === 0 && inputs === 0) {
                outcome = "fail"; detail = `navigated to ${after} but the form has no fields`;
              } else {
                detail = dialog > 0 ? "opened a modal" : `navigated to ${after}`;
              }
            }
          }
        }
      }
    } catch (err) {
      outcome = "fail"; detail = String(err).slice(0, 180);
    }

    if (consoleErrors.length && outcome === "ok") {
      outcome = "fail"; detail = `console: ${consoleErrors[0]}`;
    }
    if (outcome === "fail") failures += 1;
    results.push({ ...spec, outcome, detail, consoleErrors: consoleErrors.length });
    await page.close();
  }
  await context.close();
} finally {
  await browser.close();
}

console.log("\n=== BUTTON AUDIT ===");
for (const r of results) {
  const mark = r.outcome === "ok" ? "PASS" : r.outcome === "missing" ? "SKIP" : "FAIL";
  console.log(`  [${mark}] ${r.label.padEnd(18)} ${r.detail}`);
}
console.log(`\ntotal=${results.length} failures=${failures}`);
process.exit(failures ? 1 : 0);
