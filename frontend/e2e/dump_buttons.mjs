/** Diagnostic: dump every button/link on a page so selectors can be based on fact. */
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const BASE = process.env.BASE_URL || "http://127.0.0.1:8000";
const USER = process.env.ERP_USER, PW = process.env.ERP_PW;
const paths = process.argv.slice(2);
if (!USER || !PW) { console.error("ERP_USER/ERP_PW required"); process.exit(2); }

const browser = await chromium.launch({ headless: true });
try {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const login = await ctx.request.post(`${BASE}/api/method/login`, { data: { usr: USER, pwd: PW } });
  if (!login.ok()) throw new Error(`login HTTP ${login.status()}`);
  for (const p of paths) {
    const page = await ctx.newPage();
    const errs = [];
    page.on("console", (m) => { if (m.type() === "error") errs.push(m.text().slice(0, 200)); });
    const resp = await page.goto(`${BASE}${p}`, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(2500);
    const info = await page.evaluate(() => ({
      url: location.pathname,
      buttons: Array.from(document.querySelectorAll("button, a[href], [role=button]"))
        .map((e) => (e.innerText || e.getAttribute("aria-label") || "").trim().replace(/\s+/g, " "))
        .filter(Boolean).slice(0, 40),
      heading: (document.querySelector("h1") || {}).innerText || "",
      bodyStart: (document.body.innerText || "").slice(0, 300),
    }));
    console.log(`\n=== ${p} (HTTP ${resp && resp.status()}) ===`);
    console.log("h1:", info.heading);
    console.log("buttons:", JSON.stringify(info.buttons));
    if (errs.length) console.log("console errors:", errs.slice(0, 3));
    console.log("body:", info.bodyStart.replace(/\n/g, " | ").slice(0, 260));
    await page.close();
  }
  await ctx.close();
} finally { await browser.close(); }
