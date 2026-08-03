/**
 * Sales Team and Commission — real browser verification.
 *
 * Builds its own test data through the API (sales persons, a team, a customer),
 * drives the live Retail ERP pages, then removes what it created. Nothing is
 * hardcoded to an existing record.
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
const created = { persons: [], teams: [], customers: [], users: [] };
let ctx;

async function api(method, args = {}, httpMethod = "POST") {
  const res = await ctx.request.fetch(`${BASE}/api/method/${method}`, {
    method: httpMethod,
    headers: { "Content-Type": "application/json" },
    data: httpMethod === "GET" ? undefined : args,
    params: httpMethod === "GET" ? args : undefined,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok()) throw new Error(`${method} HTTP ${res.status()}: ${JSON.stringify(body).slice(0, 200)}`);
  return body.message;
}

async function purgeStale() {
  for (const [doctype, field] of [["Customer", "customer_name"],
                                  ["Retail Sales Team", "team_name"],
                                  ["Sales Person", "sales_person_name"]]) {
    const rows = await api("frappe.client.get_list", {
      doctype, filters: JSON.stringify([[field, "like", "E2E %"]]), limit_page_length: 100,
    }, "GET").catch(() => []);
    for (const row of rows || []) {
      await api("frappe.client.delete", { doctype, name: row.name }).catch(() => {});
    }
  }
}

async function insert(doc) {
  const out = await api("frappe.client.insert", { doc });
  return out.name;
}

const browser = await chromium.launch({ headless: true });
try {
  ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const login = await ctx.request.post(`${BASE}/api/method/login`, { data: { usr: USER, pwd: PW } });
  if (!login.ok()) throw new Error(`login HTTP ${login.status()}`);

  // Any earlier run that was interrupted may have left records behind; a stale
  // "E2E Cust A ..." would otherwise be matched by the autocomplete.
  await purgeStale();

  // ---- test data -------------------------------------------------------
  for (let i = 0; i < 3; i += 1) {
    created.persons.push(await insert({
      doctype: "Sales Person", sales_person_name: `E2E SP ${stamp}-${i}`, is_group: 0,
    }));
  }
  const teamName = `E2E Team ${stamp}`;
  const saved = await api("my_store_ui.sales_team.save_sales_team", {
    payload: {
      team_name: teamName, commission_rate: 4,
      effective_from: new Date().toISOString().slice(0, 10), is_active: true,
      members: [
        { sales_person: created.persons[0], team_role: "Sales Manager", share_percentage: 50, is_active: true },
        { sales_person: created.persons[1], team_role: "Sales Representative", share_percentage: 25, is_active: true },
        { sales_person: created.persons[2], team_role: "Sales Representative", share_percentage: 25, is_active: true },
      ],
    },
  });
  created.teams.push(saved.name);

  const groups = await api("frappe.client.get_list",
    { doctype: "Customer Group", filters: JSON.stringify([["is_group", "=", 0]]), limit_page_length: 1 }, "GET");
  const territories = await api("frappe.client.get_list",
    { doctype: "Territory", filters: JSON.stringify([["is_group", "=", 0]]), limit_page_length: 1 }, "GET");
  const withTeam = await insert({
    doctype: "Customer", customer_name: `E2E Cust A ${stamp}`,
    customer_group: groups[0].name, territory: territories[0].name,
  });
  const withoutTeam = await insert({
    doctype: "Customer", customer_name: `E2E Cust B ${stamp}`,
    customer_group: groups[0].name, territory: territories[0].name,
  });
  created.customers.push(withTeam, withoutTeam);
  await api("my_store_ui.sales_team.assign_customer_sales_team", { customer: withTeam, team: saved.name });

  // Restricted user for the unauthorised checks, created before any page opens.
  const restrictedEmail = `e2e-nosales-${stamp}@example.invalid`;
  const restrictedPw = `E2e!${stamp}Aa1`;
  await api("frappe.client.insert", {
    doc: {
      doctype: "User", email: restrictedEmail, first_name: "E2E NoSales",
      send_welcome_email: 0, new_password: restrictedPw,
      roles: [{ role: "Stock User" }],
    },
  });
  created.users = [restrictedEmail];

  // Fourth person, created up front for the "add a representative" case below.
  const extra = await insert({
    doctype: "Sales Person", sales_person_name: `E2E SP ${stamp}-x`, is_group: 0,
  });
  created.persons.push(extra);

  const page = await ctx.newPage();
  const consoleErrors = [];
  const failedRequests = [];
  page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text().slice(0, 160)); });
  page.on("pageerror", (e) => consoleErrors.push(String(e).slice(0, 160)));
  const teamRequests = [];
  page.on("request", (r) => {
    if (r.url().includes("get_sales_team")) teamRequests.push(r.url());
  });
  page.on("response", (r) => {
    if (r.status() >= 400 && r.url().includes("/api/")) failedRequests.push(`${r.status()} ${r.url().split("/api/method/")[1] || r.url()}`);
  });

  // ---- 1. navigation ---------------------------------------------------
  await page.goto(`${BASE}/retail-erp/home`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2500);
  await page.getByRole("button", { name: /^Sales submenu$/i }).click().catch(() => {});
  await page.waitForTimeout(800);
  // The module menu shows the first 7 links and hides the rest behind "Show all
  // links" (existing behaviour), so expand it the way a user would.
  await page.getByRole("button", { name: /show all \d+ links/i }).click().catch(() => {});
  const navLink = page.locator('a[href*="/sales/teams"]');
  await navLink.first().waitFor({ state: "attached", timeout: 8000 }).catch(() => {});
  const navLinks = await navLink.count();
  check("Sales Teams appears in the Sales navigation", navLinks > 0, `${navLinks} link(s)`);
  const href = await navLink.first().getAttribute("href");
  check("navigation href uses the Retail ERP base path",
    href === "/retail-erp/sales/teams", String(href));
  await page.evaluate(() => { window.__spa = true; });
  await navLink.first().click();
  await page.waitForTimeout(3000);
  check("clicking navigates without a full page reload",
    await page.evaluate(() => window.__spa === true));
  check("click lands on the Sales Teams page",
    /\/retail-erp\/sales\/teams$/.test(await page.evaluate(() => location.pathname)),
    await page.evaluate(() => location.pathname));

  // Back / forward
  await page.goBack(); await page.waitForTimeout(1500);
  await page.goForward(); await page.waitForTimeout(2500);
  check("browser back and forward return to Sales Teams",
    /sales teams/i.test(await page.locator("h1").first().innerText().catch(() => "")));

  // Direct URL + refresh
  await page.goto(`${BASE}/retail-erp/sales/teams`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2500);
  check("direct URL works", /sales teams/i.test(await page.locator("h1").first().innerText().catch(() => "")));
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2500);
  check("refresh works", /sales teams/i.test(await page.locator("h1").first().innerText().catch(() => "")));

  // ---- 2. list page ----------------------------------------------------
  await page.goto(`${BASE}/retail-erp/sales/teams`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(3000);
  const h1 = await page.locator("h1").first().innerText().catch(() => "");
  check("Sales Teams list loads", /sales teams/i.test(h1), h1);
  const listBody = await page.evaluate(() => ({
    filters: !!document.querySelector(".rug-form-grid"),
    tableOrEmpty: !!document.querySelector(".rug-table-region, .rug-empty"),
    newBtn: !!Array.from(document.querySelectorAll("a,button")).find((e) => /new sales team/i.test(e.innerText || "")),
  }));
  check("list body renders (filters, table/empty, New button), not just the header",
    listBody.filters && listBody.tableOrEmpty && listBody.newBtn, JSON.stringify(listBody));
  check("the created team is listed",
    (await page.getByText(teamName, { exact: false }).count()) > 0);

  // ---- 3. new team form ------------------------------------------------
  const newBtn = page.getByRole("link", { name: /new sales team/i })
    .or(page.getByRole("button", { name: /new sales team/i })).first();
  check("New Sales Team button exists", (await newBtn.count()) > 0);
  await newBtn.click();
  await page.waitForTimeout(2500);
  check("New Sales Team opens the form", /new sales team/i.test(await page.locator("h1").first().innerText()));

  // Regression: the helper must transmit name="" for a new record, not drop it.
  const newReq = teamRequests.find((u) => u.includes("get_sales_team"));
  check("new-team request carries the name parameter",
    Boolean(newReq) && /[?&]name=(&|$)/.test(newReq), newReq || "(no request)");

  const shareInputs = page.locator('input[aria-label^="Share for row"]');
  const shareValues = await shareInputs.evaluateAll((els) => els.map((e) => Number(e.value)));
  check("default split is 50 / 25 / 25",
    JSON.stringify(shareValues) === JSON.stringify([50, 25, 25]), JSON.stringify(shareValues));

  const formBody = await page.evaluate(() => ({
    teamName: !!document.querySelector('input[type="text"]'),
    teamCode: Array.from(document.querySelectorAll("input")).some((i) => i.readOnly),
    rows: document.querySelectorAll('input[aria-label^="Person for row"]').length,
    add: !!Array.from(document.querySelectorAll("button")).find((e) => /add representative/i.test(e.innerText || "")),
    save: !!Array.from(document.querySelectorAll("button")).find((e) => /save sales team/i.test(e.innerText || "")),
    cancel: !!Array.from(document.querySelectorAll("a,button")).find((e) => /^cancel$/i.test((e.innerText || "").trim())),
    roles: Array.from(document.querySelectorAll('select[aria-label^="Role for row"]')).map((s2) => s2.value),
  }));
  check("form body shows name, code, member rows, Add, Save and Cancel",
    formBody.teamName && formBody.teamCode && formBody.rows === 3
      && formBody.add && formBody.save && formBody.cancel, JSON.stringify(formBody));
  check("default roles are Manager + 2 Representatives",
    JSON.stringify(formBody.roles) === JSON.stringify(
      ["Sales Manager", "Sales Representative", "Sales Representative"]),
    JSON.stringify(formBody.roles));

  const totalText = () => page.locator(".smj-team-total").innerText();
  check("live total shows 100%", /100/.test(await totalText()), await totalText());

  // add a representative -> 4 rows, total now 100 still (new row is 0)
  await page.getByRole("button", { name: /add representative/i }).click();
  await page.waitForTimeout(300);
  check("a representative can be added",
    (await page.locator('input[aria-label^="Share for row"]').count()) === 4);

  // ---- 4. validation ---------------------------------------------------
  await shareInputs.nth(0).fill("40");   // 40+25+25+0 = 90
  await page.waitForTimeout(300);
  check("90% is reported as invalid", /90/.test(await totalText()), await totalText());
  const saveBtn = page.getByRole("button", { name: /save sales team/i });
  check("saving is blocked at 90%", await saveBtn.isDisabled());

  await shareInputs.nth(0).fill("60");   // 60+25+25+0 = 110
  await page.waitForTimeout(300);
  check("110% is reported as invalid", /110/.test(await totalText()), await totalText());
  check("saving is blocked at 110%", await saveBtn.isDisabled());

  // fill the 4th row so 50/25/15/10 = 100
  await shareInputs.nth(0).fill("50");
  await shareInputs.nth(2).fill("15");
  await shareInputs.nth(3).fill("10");
  const personInputs = page.locator('input[aria-label^="Person for row"]');
  await personInputs.nth(0).fill(created.persons[0]);
  await personInputs.nth(1).fill(created.persons[1]);
  await personInputs.nth(2).fill(created.persons[2]);
  await personInputs.nth(3).fill(created.persons[2]);   // duplicate on purpose
  await page.locator('input[type="text"]').first().fill(`E2E UI Team ${stamp}`);
  await page.waitForTimeout(400);
  check("duplicate person is rejected in the UI", await saveBtn.isDisabled());

  await personInputs.nth(3).fill(created.persons[0]);   // still duplicate (manager)
  await page.waitForTimeout(300);
  check("duplicate manager is also rejected", await saveBtn.isDisabled());

  await personInputs.nth(3).fill(extra);
  await page.waitForTimeout(400);
  check("100% with unique people enables save", !(await saveBtn.isDisabled()),
    await totalText());

  await saveBtn.click();
  await page.waitForTimeout(3000);
  const listAfter = await page.locator("body").innerText();
  check("saving at exactly 100% succeeds", /E2E UI Team/.test(listAfter));

  // ---- 5. Smart Sales --------------------------------------------------
  await page.goto(`${BASE}/retail-erp/smart-sales`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(3000);

  const combo = page.locator('input[aria-controls="smj-customer-options"]');
  check("Smart Sales has exactly one customer field", (await combo.count()) === 1);
  check("idle state is shown before choosing a customer",
    /select a customer to load the assigned sales team/i.test(await page.locator(".smj-team-card").innerText()));

  await combo.click();
  await combo.type(`E2E Cust A ${stamp}`, { delay: 25 });
  await page.waitForTimeout(2000);
  const options = page.locator('#smj-customer-options li[role="option"]');
  check("typing finds the customer", (await options.count()) > 0);
  // Select by exact name: a prefix can match leftovers from an earlier run.
  const exact = options.filter({ hasText: `E2E Cust A ${stamp}` }).first();
  check("the typed customer is matched exactly", (await exact.count()) > 0);
  await exact.click();
  await page.waitForTimeout(3500);

  const cardText = await page.locator(".smj-team-card").innerText();
  check("Sales Team card is rendered", /sales team and commission/i.test(cardText));
  check("card shows the team name", cardText.includes(teamName),
    `expected "${teamName}" | card=${JSON.stringify(cardText.slice(0, 120))}`);
  check("card shows the manager", cardText.includes(created.persons[0]),
    `expected "${created.persons[0]}"`);
  check("card shows both representatives",
    cardText.includes(created.persons[1]) && cardText.includes(created.persons[2]));
  check("card shows 50% / 25% / 25%",
    /50%/.test(cardText) && (cardText.match(/25%/g) || []).length >= 2);
  check("card shows the commission rate", /4%/.test(cardText));
  check("total allocation is 100%", /Total Allocation\s*100%/i.test(cardText.replace(/\n/g, " ")));
  check("no undefined/null leaked into the card",
    !/undefined|null|NaN/.test(cardText), cardText.slice(0, 80));

  // dropdown stacking
  await combo.click();
  await combo.fill("");
  await combo.type(`E2E Cust B ${stamp}`, { delay: 25 });
  await page.waitForTimeout(1600);
  const front = await page.evaluate(() => {
    const list = document.querySelector("#smj-customer-options");
    if (!list) return { ok: false, why: "no list" };
    const r = list.getBoundingClientRect();
    const el = document.elementFromPoint(r.left + r.width / 2, r.top + Math.min(r.height - 4, 30));
    return { ok: !!el && list.contains(el), why: el ? (el.className || el.tagName) : "nothing" };
  });
  check("customer dropdown paints in front", front.ok, String(front.why));

  // switch to the customer with no team
  const opts2 = page.locator('#smj-customer-options li[role="option"]');
  const count2 = await opts2.count();
  let switched = false;
  for (let i = 0; i < count2; i += 1) {
    const label = await opts2.nth(i).locator("strong").innerText();
    if (label === `E2E Cust B ${stamp}`) { await opts2.nth(i).click(); switched = true; break; }
  }
  if (switched) {
    await page.waitForTimeout(3500);
    const after = await page.locator(".smj-team-card").innerText();
    check("previous team is cleared on customer change", !after.includes(teamName), after.slice(0, 70));
    check("customer without a team shows a clear empty state",
      /no sales team is assigned/i.test(after), after.slice(0, 70));
  } else {
    check("could switch to the second customer", false, "option not found");
  }

  // ---- 6. customer form assignment ------------------------------------
  await page.goto(`${BASE}/retail-erp/sales/customers/${encodeURIComponent(withTeam)}/edit`,
    { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(3500);
  const custText = await page.locator("body").innerText();
  check("Customer form shows Sales Assignment", /sales assignment/i.test(custText));
  check("assignment loads the saved team after refresh",
    custText.includes(teamName) || custText.includes(created.persons[0]), "");

  // ---- 6b. saved team round-trip --------------------------------------
  await page.goto(`${BASE}/retail-erp/sales/teams`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2800);
  const savedRow = page.locator("tbody tr").filter({ hasText: `E2E UI Team ${stamp}` }).first();
  check("the saved team appears in the list", (await savedRow.count()) > 0);
  if (await savedRow.count()) {
    await savedRow.click();
    await page.waitForTimeout(3000);
    const loaded = await page.evaluate(() => ({
      h1: (document.querySelector("h1") || {}).innerText || "",
      name: (document.querySelector('input[type="text"]') || {}).value || "",
      shares: Array.from(document.querySelectorAll('input[aria-label^="Share for row"]')).map((i) => Number(i.value)),
      total: (document.querySelector(".smj-team-total") || {}).innerText || "",
    }));
    check("opening the saved team loads its real data",
      loaded.name.includes(`E2E UI Team ${stamp}`), JSON.stringify(loaded).slice(0, 140));
    check("saved shares are preserved (50/25/15/10)",
      JSON.stringify(loaded.shares) === JSON.stringify([50, 25, 15, 10]),
      JSON.stringify(loaded.shares));
    check("reloaded team still totals 100%", /100/.test(loaded.total), loaded.total);
  }

  // ---- 6c. unauthorised user ------------------------------------------
  const rCtx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const rLogin = await rCtx.request.post(`${BASE}/api/method/login`,
    { data: { usr: restrictedEmail, pwd: restrictedPw } });
  if (rLogin.ok()) {
    const rp = await rCtx.newPage();
    await rp.goto(`${BASE}/retail-erp/home`, { waitUntil: "domcontentloaded" });
    await rp.waitForTimeout(2500);
    await rp.getByRole("button", { name: /^Sales submenu$/i }).click().catch(() => {});
    await rp.waitForTimeout(700);
    await rp.getByRole("button", { name: /show all \d+ links/i }).click().catch(() => {});
    await rp.waitForTimeout(700);
    check("unauthorised user does not see the Sales Teams navigation",
      (await rp.locator('a[href*="/sales/teams"]').count()) === 0);

    await rp.goto(`${BASE}/retail-erp/sales/teams`, { waitUntil: "domcontentloaded" });
    await rp.waitForTimeout(3000);
    // Assert on the page's own heading, not any occurrence in the whole document,
    // and confirm the Sales Teams body is genuinely absent.
    const rState = await rp.evaluate(() => ({
      heading: Array.from(document.querySelectorAll("h1,h2"))
        .map((h) => h.innerText.trim()).join(" | "),
      hasNewBtn: !!Array.from(document.querySelectorAll("a,button"))
        .find((e) => /new sales team/i.test(e.innerText || "")),
      hasTeamTable: !!document.querySelector(".rug-table-region"),
    }));
    check("unauthorised direct access is denied",
      /permission denied|not permitted|no access/i.test(rState.heading)
        && !rState.hasNewBtn && !rState.hasTeamTable,
      JSON.stringify(rState));

    const apiRes = await rCtx.request.get(
      `${BASE}/api/method/my_store_ui.sales_team.list_sales_teams`);
    check("backend refuses the unauthorised user too (not just the UI)",
      apiRes.status() === 403, `HTTP ${apiRes.status()}`);
    await rp.close();
  } else {
    check("restricted user could log in", false, `HTTP ${rLogin.status()}`);
  }
  await rCtx.close();

  // ---- 7. health -------------------------------------------------------
  check("no console errors", consoleErrors.length === 0, consoleErrors[0] || "");
  check("no failed API requests", failedRequests.length === 0, failedRequests[0] || "");

  await page.close();
} finally {
  // ---- cleanup ---------------------------------------------------------
  try {
    for (const c of created.customers) await api("frappe.client.delete", { doctype: "Customer", name: c }).catch(() => {});
    for (const t of created.teams) await api("frappe.client.delete", { doctype: "Retail Sales Team", name: t }).catch(() => {});
    const uiTeams = await api("frappe.client.get_list",
      { doctype: "Retail Sales Team", filters: JSON.stringify([["team_name", "like", `%${stamp}%`]]), limit_page_length: 20 }, "GET").catch(() => []);
    for (const t of uiTeams || []) await api("frappe.client.delete", { doctype: "Retail Sales Team", name: t.name }).catch(() => {});
    for (const p of created.persons) await api("frappe.client.delete", { doctype: "Sales Person", name: p }).catch(() => {});
    for (const u of created.users || []) await api("frappe.client.delete", { doctype: "User", name: u }).catch(() => {});
  } catch { /* cleanup is best effort */ }
  await browser.close();
}

const failed = results.filter((r) => !r.ok).length;
console.log(`\ntotal=${results.length} failures=${failed}`);
process.exit(failed ? 1 : 0);
