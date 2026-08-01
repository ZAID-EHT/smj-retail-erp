/**
 * Smart Sales customer field: one input, type-ahead suggestions, selection.
 *
 * Asserts the requirement from ACCOUNT CREATION.docx -- there is a single customer
 * field (no separate "Choose customer" select), typing shows the most relevant
 * matches, and picking one selects that customer.
 */

import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const BASE = process.env.BASE_URL || "http://127.0.0.1:8000";
const USER = process.env.ERP_USER, PW = process.env.ERP_PW;
let TERM = process.env.CUSTOMER_TERM || "";
if (!USER || !PW) { console.error("ERP_USER/ERP_PW required"); process.exit(2); }

const results = [];
function check(name, ok, detail = "") {
  results.push({ name, ok, detail });
  console.log(`  [${ok ? "PASS" : "FAIL"}] ${name}${detail ? ` — ${detail}` : ""}`);
}

const browser = await chromium.launch({ headless: true });
try {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const login = await ctx.request.post(`${BASE}/api/method/login`, { data: { usr: USER, pwd: PW } });
  if (!login.ok()) throw new Error(`login HTTP ${login.status()}`);
  // Derive a search term from a real customer so the harness needs no hardcoded name.
  if (!TERM) {
    const res = await ctx.request.get(
      `${BASE}/api/method/frappe.client.get_list`
      + `?doctype=Customer&filters=${encodeURIComponent('[["disabled","=",0]]')}`
      + `&fields=${encodeURIComponent('["customer_name"]')}&limit_page_length=1`,
    );
    const body = await res.json().catch(() => ({}));
    const name = body?.message?.[0]?.customer_name || "";
    TERM = name ? name.slice(0, 3) : "a";
  }

  const page = await ctx.newPage();
  const consoleErrors = [];
  page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text().slice(0, 160)); });
  page.on("pageerror", (e) => consoleErrors.push(String(e).slice(0, 160)));

  await page.goto(`${BASE}/retail-erp/smart-sales`, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForTimeout(3000);

  // 1. The old second field must be gone.
  const selects = await page.locator("select").allTextContents();
  check("no 'Choose customer' select remains", !selects.some((t) => /choose customer/i.test(t)));

  // 2. Exactly one customer field, and it is a combobox.
  // Scope to the customer field: the global header search is also a combobox.
  const combo = page.locator('input[aria-controls="smj-customer-options"]');
  check("single customer combobox exists", (await combo.count()) === 1, `found ${await combo.count()}`);
  check("only one customer input in Sale setup", (await page.locator(".smj-customer-picker input").count()) === 1);

  // 3. Typing shows suggestions.
  await combo.click();
  await combo.type(TERM, { delay: 60 });
  await page.waitForTimeout(1400);
  const listbox = page.locator('#smj-customer-options[role="listbox"]');
  const open = await listbox.count();
  check("suggestion list opens while typing", open === 1);

  const options = page.locator('#smj-customer-options li[role="option"]');
  const optionCount = await options.count();
  check("matching customers are suggested", optionCount > 0, `${optionCount} suggestions`);

  // 4. Picking one selects the customer.
  if (optionCount > 0) {
    const label = (await options.first().locator("strong").innerText()).trim();
    await options.first().click();
    await page.waitForTimeout(2500);
    const value = await combo.inputValue();
    check("selecting fills the field", value.length > 0, `"${value}"`);
    check("selected value matches the chosen customer", value === label, `"${value}" vs "${label}"`);

    const banner = await page.locator(".smj-sales-customer-required").count();
    check("red customer-required banner disappears", banner === 0);

    const badge = await page.locator(".rug-value-badge").first().innerText().catch(() => "");
    check("selected customer is shown on the card", badge.trim().length > 0, badge.trim());
  }

  // 5. Keyboard navigation works.
  await combo.click();
  await combo.fill("");
  await combo.type(TERM, { delay: 60 });
  await page.waitForTimeout(1400);
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Enter");
  await page.waitForTimeout(1500);
  check("keyboard selection works", (await combo.inputValue()).length > 0);

  // 6. Visual consistency: the customer input must match the Warehouse select.
  const metrics = await page.evaluate(() => {
    const input = document.querySelector('.smj-customer-picker__control input');
    const select = document.querySelector('.priority-sales-controls select');
    if (!input || !select) return null;
    const a = input.getBoundingClientRect(), b = select.getBoundingClientRect();
    const ca = getComputedStyle(input), cb = getComputedStyle(select);
    return {
      inH: Math.round(a.height), selH: Math.round(b.height),
      inFont: ca.fontSize, selFont: cb.fontSize,
      inRadius: ca.borderRadius, selRadius: cb.borderRadius,
    };
  });
  if (metrics) {
    check("customer input height matches the select", metrics.inH === metrics.selH,
      `${metrics.inH}px vs ${metrics.selH}px`);
    check("font size matches", metrics.inFont === metrics.selFont,
      `${metrics.inFont} vs ${metrics.selFont}`);
    check("corner radius matches", metrics.inRadius === metrics.selRadius,
      `${metrics.inRadius} vs ${metrics.selRadius}`);
  } else {
    check("control metrics readable", false, "input or select not found");
  }

  // 7. The suggestion list must paint in FRONT of the card below it.
  await combo.click();
  await combo.fill("");
  await combo.type(TERM, { delay: 60 });
  await page.waitForTimeout(1400);
  const front = await page.evaluate(() => {
    const list = document.querySelector('#smj-customer-options');
    if (!list) return { ok: false, why: "list not rendered" };
    const r = list.getBoundingClientRect();
    if (r.height < 5) return { ok: false, why: "list has no height" };
    const x = r.left + r.width / 2;
    const y = r.top + Math.min(r.height - 4, 30);
    const top = document.elementFromPoint(x, y);
    return { ok: !!top && list.contains(top), why: top ? (top.className || top.tagName) : "nothing" };
  });
  check("suggestion list paints in front of the next card", front.ok, String(front.why));

  check("no console errors", consoleErrors.length === 0, consoleErrors[0] || "");
  await page.close();
  await ctx.close();
} finally {
  await browser.close();
}

const failed = results.filter((r) => !r.ok).length;
console.log(`\ntotal=${results.length} failures=${failed}`);
process.exit(failed ? 1 : 0);
