/**
 * Commission policy, periods, approval, statements and payout — browser check.
 *
 * Builds its own policy, team, customer, invoice and period through the API, drives
 * the real screens, and asserts the one thing that must never change: no payout can
 * be marked paid, and no accounting is posted.
 */

import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const BASE = process.env.BASE_URL || "http://127.0.0.1:8000";
const USER = process.env.ERP_USER, PW = process.env.ERP_PW;
if (!USER || !PW) { console.error("ERP_USER/ERP_PW required"); process.exit(2); }

const results = [];
function check(name, ok, detail = "") {
  results.push({ name, ok, detail });
  console.log(`  [${ok ? "PASS" : "FAIL"}] ${name}${detail ? ` — ${detail}` : ""}`);
}

const stamp = Date.now().toString(36);
const created = { persons: [], teams: [], customers: [], items: [], policies: [], periods: [] };
let ctx;
// Frappe only enforces CSRF once a page has booted and put a token in the session.
let csrfToken = "";

async function api(method, args = {}, httpMethod = "POST") {
  const res = await ctx.request.fetch(`${BASE}/api/method/${method}`, {
    method: httpMethod,
    headers: {
      "Content-Type": "application/json",
      ...(csrfToken ? { "X-Frappe-CSRF-Token": csrfToken } : {}),
    },
    data: httpMethod === "GET" ? undefined : args,
    params: httpMethod === "GET" ? args : undefined,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok()) throw new Error(`${method} HTTP ${res.status()}: ${JSON.stringify(body).slice(0, 200)}`);
  return body.message;
}

const insert = async (doc) => (await api("frappe.client.insert", { doc })).name;
async function submitDoc(doctype, name) {
  const doc = await api("frappe.client.get", { doctype, name }, "GET");
  return api("frappe.client.submit", { doc });
}

// A fixed timeout is a guess. Wait for the SPA to have actually rendered, and for
// Frappe's boot to have put a CSRF token where the page can see it.
async function ready(page, pattern, timeout = 30000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const text = await page.locator("body").innerText().catch(() => "");
    if (pattern.test(text)) return text;
    await page.waitForTimeout(400);
  }
  return await page.locator("body").innerText().catch(() => "");
}

async function captureCsrf(page, timeout = 20000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const token = await page.evaluate(
      () => window.frappe?.csrf_token || window.csrf_token || "").catch(() => "");
    if (token) return token;
    await page.waitForTimeout(400);
  }
  return "";
}

const browser = await chromium.launch({ headless: true });
try {
  ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const login = await ctx.request.post(`${BASE}/api/method/login`, { data: { usr: USER, pwd: PW } });
  if (!login.ok()) throw new Error(`login HTTP ${login.status()}`);

  const page = await ctx.newPage();
  const consoleErrors = [];
  const failedRequests = [];
  page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text().slice(0, 160)); });
  page.on("pageerror", (e) => consoleErrors.push(String(e).slice(0, 160)));
  page.on("response", (r) => {
    if (r.status() >= 400 && r.url().includes("/api/")) {
      failedRequests.push(`${r.status()} ${r.url().split("/api/method/")[1] || r.url()}`);
    }
  });

  // ---- 1. the policy screen ---------------------------------------------
  await page.goto(`${BASE}/retail-erp/admin/sales/commission-policy`, { waitUntil: "domcontentloaded" });
  const policyBody = await ready(page, /commission policy/i);
  csrfToken = await captureCsrf(page);
  check("Commission Policy page renders", /commission policy/i.test(policyBody),
    policyBody.slice(0, 80).replace(/\n/g, " "));
  check("a CSRF token is available after boot", Boolean(csrfToken));
  // The button appears once the list request returns, which is after the banner.
  const newPolicy = page.locator('[data-test="policy-new"]');
  await newPolicy.waitFor({ state: "visible", timeout: 20000 }).catch(() => {});
  check("a policy can be created from the page", (await newPolicy.count()) > 0);

  await newPolicy.click();
  await page.waitForTimeout(2000);
  const trigger = page.locator('[data-test="policy-trigger"]');
  check("the earning trigger has no default",
    (await trigger.inputValue()) === "", await trigger.inputValue());
  const missingText = await page.locator('[data-test="policy-missing"]').innerText().catch(() => "");
  check("the page names every unanswered decision",
    /Commission Is Earned On/i.test(missingText) && /Withholding/i.test(missingText),
    missingText.slice(0, 90));

  // ---- 2. build a real closing through the API ---------------------------
  const company = (await api("frappe.client.get_list",
    { doctype: "Company", limit_page_length: 1 }, "GET"))[0].name;
  const policy = await api("my_store_ui.commission_policy.save_commission_policy", {
    payload: {
      policy_name: `E2E Policy ${stamp}`, company, effective_from: new Date().toISOString().slice(0, 10),
      enabled: 1, earning_trigger: "Sales Invoice Submission",
      commission_basis: "Net Total After Discount", rate_source: "Sales Team Rate",
      payout_cycle: "Monthly", withholding_mode: "No Withholding",
      returns_rule: "Reverse Before Payout",
    },
  });
  created.policies.push(policy.name);
  check("a complete policy is Ready for Review, not Active",
    policy.policy.status === "Ready for Review", policy.policy.status);
  check("a complete policy still cannot post", policy.policy.may_post === false);

  const approved = await api("my_store_ui.commission_policy.approve_commission_policy",
    { name: policy.name });
  check("an approved, enabled policy becomes Active",
    approved.policy.status === "Active", approved.policy.status);
  check("an Active policy still cannot post", approved.policy.may_post === false,
    `missing: ${(approved.policy.missing_for_posting || []).join(", ").slice(0, 70)}`);

  for (let i = 0; i < 3; i += 1) {
    created.persons.push(await insert({
      doctype: "Sales Person", sales_person_name: `E2E CP ${stamp}-${i}`, is_group: 0,
    }));
  }
  const team = await api("my_store_ui.sales_team.save_sales_team", {
    payload: {
      team_name: `E2E CP Team ${stamp}`, commission_rate: 2,
      effective_from: new Date().toISOString().slice(0, 10), is_active: true,
      members: [
        { sales_person: created.persons[0], team_role: "Sales Manager", share_percentage: 50, is_active: true },
        { sales_person: created.persons[1], team_role: "Sales Representative", share_percentage: 25, is_active: true },
        { sales_person: created.persons[2], team_role: "Sales Representative", share_percentage: 25, is_active: true },
      ],
    },
  });
  created.teams.push(team.name);

  const groups = await api("frappe.client.get_list",
    { doctype: "Customer Group", filters: JSON.stringify([["is_group", "=", 0]]), limit_page_length: 1 }, "GET");
  const territories = await api("frappe.client.get_list",
    { doctype: "Territory", filters: JSON.stringify([["is_group", "=", 0]]), limit_page_length: 1 }, "GET");
  const customer = await insert({
    doctype: "Customer", customer_name: `E2E CPCust ${stamp}`,
    customer_group: groups[0].name, territory: territories[0].name,
    default_price_list: "Wholesale Price List",
  });
  created.customers.push(customer);
  await api("my_store_ui.sales_team.assign_customer_sales_team", { customer, team: team.name });

  const itemGroups = await api("frappe.client.get_list",
    { doctype: "Item Group", filters: JSON.stringify([["is_group", "=", 0]]), limit_page_length: 1 }, "GET");
  const warehouses = await api("frappe.client.get_list",
    { doctype: "Warehouse", filters: JSON.stringify([["is_group", "=", 0], ["disabled", "=", 0]]), limit_page_length: 1 }, "GET");
  const warehouse = warehouses[0].name;
  const product = await api("my_store_ui.quick_entry.product.create_product", {
    values: {
      product_name: `E2E CPItem ${stamp}`, category: itemGroups[0].name,
      stock_location_1: warehouse, cost_price: 500, wholesale_price: 1000, retail_price: 1200,
    },
  });
  created.items.push(product.name);
  const receipt = await api("frappe.client.insert", {
    doc: {
      doctype: "Stock Entry", stock_entry_type: "Material Receipt",
      items: [{ item_code: product.name, qty: 300, t_warehouse: warehouse, basic_rate: 500 }],
    },
  });
  await submitDoc("Stock Entry", receipt.name);
  const order = await api("my_store_ui.api.create_draft_sales_order", {
    payload: {
      request_id: `e2e-cp-${stamp}`, customer, warehouse,
      items: [{ item_code: product.name, qty: 100 }],
    },
  });
  await submitDoc("Sales Order", order.name);
  const note = await api("my_store_ui.wholesale.delivery.create_delivery_note",
    { sales_order: order.name, override_reason: "E2E commission closing", submit: 1 });
  await api("my_store_ui.wholesale.invoicing.create_sales_invoice",
    { delivery_note: note.name, submit: 1 });

  const period = await api("my_store_ui.commission_period.create_commission_period", {
    company, policy: policy.name,
    from_date: new Date(Date.now() - 30 * 864e5).toISOString().slice(0, 10),
    to_date: new Date(Date.now() + 864e5).toISOString().slice(0, 10),
  });
  created.periods.push(period.name);
  check("the period gets a dated identifier", /^COM-PER-\d{4}-\d{6}$/.test(period.name), period.name);

  // ---- 3. the periods screen --------------------------------------------
  await page.goto(`${BASE}/retail-erp/sales/commission-periods`, { waitUntil: "domcontentloaded" });
  const periodsBody = await ready(page, /commission periods/i);
  check("Commission Periods page renders", /commission periods/i.test(periodsBody));
  check("the period list shows the new period",
    (await page.locator('[data-test="period-table"]').innerText().catch(() => "")).includes(period.name));

  await page.goto(`${BASE}/retail-erp/sales/commission-periods?period=${encodeURIComponent(period.name)}`,
    { waitUntil: "domcontentloaded" });
  await ready(page, /Net payable|Status/i);
  check("the period detail opens", (await page.locator('[data-test="period-totals"]').count()) > 0);

  await page.locator('[data-test="period-prepare"]').click();
  await page.waitForTimeout(4000);
  const rowCount = await page.locator('[data-test="period-rows"] tbody tr').count();
  check("preparing fills the period from the frozen snapshots", rowCount >= 3, `${rowCount} rows`);
  check("the period shows a net payable",
    /[1-9]/.test(await page.locator('[data-test="period-net"]').innerText().catch(() => "0")));

  await page.locator('[data-test="period-checks"]').click();
  await page.waitForTimeout(2500);
  const checkText = await page.locator('[data-test="period-check-list"]').innerText().catch(() => "");
  check("approval checks are shown before approving", /PASS|FAIL/.test(checkText));

  // ---- 4. approval through the API, then payout on screen ---------------
  await api("my_store_ui.commission_period.submit_period_for_review", { name: period.name });
  await api("my_store_ui.commission_period.review_commission_period",
    { name: period.name, comment: "E2E" });
  await api("my_store_ui.commission_period.approve_commission_period",
    { name: period.name, comment: "E2E" });

  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(3500);
  await page.getByRole("button", { name: /^Statements$/ }).click();
  await page.waitForTimeout(3000);
  check("statements render for the approved period",
    (await page.locator('[data-test="statement"]').count()) >= 3,
    String(await page.locator('[data-test="statement"]').count()));

  await page.getByRole("button", { name: /^Payout$/ }).click();
  await page.waitForTimeout(1500);
  await page.locator('[data-test="payout-prepare"]').click();
  // Preparing a payout is three round trips (prepare, validate, reload). Wait for
  // the result rather than guessing how long they take.
  await page.locator('[data-test="payout-lines"]')
    .waitFor({ state: "visible", timeout: 60000 }).catch(() => {});

  // The app renders no <main>, so read the body -- a diagnostic that silently
  // returns "" is worse than none at all.
  console.log("    [diag] payout tab body:",
    (await page.locator("body").innerText().catch(() => "")).replace(/\n+/g, " | ").slice(-400));
  const blocked = await page.locator('[data-test="payout-blocked"]').innerText().catch(() => "");
  check("the payout states plainly why posting is blocked",
    /not enabled|incomplete/i.test(blocked), blocked.slice(0, 90));
  check("payout lines are listed",
    (await page.locator('[data-test="payout-lines"] tbody tr').count()) >= 3);
  const preview = await page.locator('[data-test="accounting-preview"]').innerText().catch(() => "");
  check("the accounting preview says it would not post", /would post\s*no/i.test(preview),
    preview.replace(/\n/g, " ").slice(0, 90));

  const body = await page.locator("body").innerText();
  check("no fake Paid status appears anywhere on the page",
    !/\bPaid\b(?!\s*0)/.test(body.replace(/Part Paid|Unpaid/g, "")) || /Paid\s*0/.test(body),
    "");

  const postAttempt = await ctx.request.fetch(
    `${BASE}/api/method/my_store_ui.commission_payout.post_commission_payout`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrfToken },
      data: { name: (await api("my_store_ui.commission_payout.list_commission_payouts",
        { period: period.name }, "GET")).rows[0].name, confirmation: "yes" },
    });
  check("the posting endpoint refuses even when called directly",
    postAttempt.status() >= 400, `HTTP ${postAttempt.status()}`);

  const gl = await api("frappe.client.get_count",
    { doctype: "GL Entry", filters: JSON.stringify([["voucher_no", "=", period.name]]) }, "GET");
  check("no GL entry exists for the period", Number(gl) === 0, String(gl));

  // ---- 5. historical review ---------------------------------------------
  await page.goto(`${BASE}/retail-erp/sales/commissions/historical-review`, { waitUntil: "domcontentloaded" });
  const reviewBody = await ready(page, /historical commission review/i);
  check("Historical Commission Review renders", /historical commission review/i.test(reviewBody));
  check("the page states that a current team is not evidence",
    /not evidence/i.test(await page.locator('[data-test="historical-note"]').innerText().catch(() => reviewBody)));

  check("no page scrolls sideways",
    await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1));

  // ---- 6. the closing screens at all six viewports ------------------------
  // The period detail, exceptions, adjustments, statements, payout and accounting
  // preview are tabs on one route, so no static URL sweep can reach them. Drive them
  // here instead, while this run's own period still exists.
  const VIEWPORTS = [
    { name: "desktop-1920", width: 1920, height: 1080 },
    { name: "desktop-1440", width: 1440, height: 900 },
    { name: "laptop-1024", width: 1024, height: 768 },
    { name: "tablet-768", width: 768, height: 1024 },
    { name: "mobile-390", width: 390, height: 844 },
    { name: "mobile-360", width: 360, height: 800 },
  ];
  const TABS = [/^Rows/, /^Exceptions/, /^Adjustments/, /^Statements$/, /^Payout$/];

  for (const vp of VIEWPORTS) {
    const vctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    try {
      const vLogin = await vctx.request.post(`${BASE}/api/method/login`, { data: { usr: USER, pwd: PW } });
      if (!vLogin.ok()) throw new Error(`login HTTP ${vLogin.status()}`);
      const vpage = await vctx.newPage();
      const vErrors = [];
      vpage.on("console", (m) => { if (m.type() === "error") vErrors.push(m.text().slice(0, 160)); });
      vpage.on("pageerror", (e) => vErrors.push(String(e).slice(0, 160)));

      await vpage.goto(
        `${BASE}/retail-erp/sales/commission-periods?period=${encodeURIComponent(period.name)}`,
        { waitUntil: "domcontentloaded" });
      await ready(vpage, /Net payable|Status/i);

      let widest = 0;
      let clipped = "";
      for (const label of TABS) {
        await vpage.getByRole("button", { name: label }).first().click().catch(() => {});
        await vpage.waitForTimeout(1500);
        const probe = await vpage.evaluate(() => ({
          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
          // A table wider than its own scroll container is clipped, not scrollable.
          clipped: Array.from(document.querySelectorAll("table"))
            .filter((t) => {
              const box = t.closest(".smj-table-scroll");
              return t.scrollWidth > t.clientWidth + 1 && !box;
            }).length,
        }));
        widest = Math.max(widest, probe.overflow);
        if (probe.clipped) clipped = `${probe.clipped} table(s)`;
      }

      check(`${vp.name}: the closing tabs never scroll the page sideways`, widest <= 1, `${widest}px`);
      check(`${vp.name}: no table is clipped outside a scroll container`, !clipped, clipped);
      check(`${vp.name}: no console errors across the closing tabs`, vErrors.length === 0, vErrors[0] || "");
      const vBody = await vpage.locator("body").innerText();
      check(`${vp.name}: still no fake Paid status`,
        !/\bPaid\b(?!\s*0)/.test(vBody.replace(/Part Paid|Unpaid|Partly Paid/g, "")) || /Paid\s*0/.test(vBody));
      await vpage.close();
    } finally {
      await vctx.close();
    }
  }

  // ---- 7. health ---------------------------------------------------------
  check("no console errors", consoleErrors.length === 0, consoleErrors[0] || "");
  const realFailures = failedRequests.filter((f) => !f.startsWith("417") && !f.includes("post_commission_payout"));
  check("no unexpected failed API requests", realFailures.length === 0, realFailures[0] || "");

  await page.close();
} finally {
  // Cleanup that swallows every error leaves residue and reports success. Say what
  // could not be removed instead.
  const undeleted = [];
  const del = async (doctype, name) => {
    try {
      await api("frappe.client.delete", { doctype, name });
    } catch (caught) {
      undeleted.push(`${doctype} ${name}: ${String(caught.message || caught).slice(0, 80)}`);
    }
  };
  try {
    for (const p of created.periods) {
      // A payout is named for itself, not for its period. Deleting by the period
      // name silently fails, and then the period cannot go either because the
      // payout still links to it.
      const payouts = await api("frappe.client.get_list", {
        doctype: "Retail Commission Payout",
        filters: JSON.stringify([["period", "=", p]]), limit_page_length: 50,
      }, "GET").catch(() => []);
      for (const row of payouts) await del("Retail Commission Payout", row.name);
      await del("Retail Commission Period", p);
    }
    for (const p of created.policies) await del("Retail Commission Policy", p);
    // The order, delivery, invoice and stock entry this run submitted are accounting
    // documents and are deliberately left alone, so the customer, team, item and
    // sales people they link to cannot go either. That is correct, not a leak.
    for (const c of created.customers) await del("Customer", c);
    for (const t of created.teams) await del("Retail Sales Team", t);
    for (const i of created.items) await del("Item", i);
    for (const p of created.persons) await del("Sales Person", p);
  } catch (caught) {
    undeleted.push(`cleanup aborted: ${String(caught.message || caught).slice(0, 120)}`);
  }
  if (undeleted.length) {
    console.log("\n=== NOT DELETED (expected for anything a submitted document links to) ===");
    for (const line of undeleted) console.log(`  ${line}`);
  }
  await browser.close();
}

const failed = results.filter((r) => !r.ok).length;
console.log(`\ntotal=${results.length} failures=${failed}`);
process.exit(failed ? 1 : 0);
