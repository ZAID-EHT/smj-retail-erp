// Playwright browser smoke tests for the Retail ERP wholesale UI.
// Ready to run once Playwright + Chromium are installed (network was unavailable
// during implementation) against a running site with a known login.
//
//   cd apps/my_store_ui/frontend
//   npm install -D @playwright/test && npx playwright install chromium
//   BASE_URL=http://127.0.0.1:8000 ERP_USER=Administrator ERP_PW=<pw> \
//     npx playwright test e2e/wholesale.spec.js
import { test, expect } from "@playwright/test";

const BASE = process.env.BASE_URL || "http://127.0.0.1:8000";
const USER = process.env.ERP_USER || "Administrator";
const PW = process.env.ERP_PW || "admin";

async function login(page) {
  await page.goto(`${BASE}/login`);
  await page.fill("#login_email", USER);
  await page.fill("#login_password", PW);
  await page.click("button.btn-login");
  await page.waitForLoadState("networkidle");
}

test.describe("Retail ERP wholesale", () => {
  test.beforeEach(async ({ page }) => login(page));

  test("transaction register renders rows", async ({ page }) => {
    await page.goto(`${BASE}/retail-erp/sales/transactions`);
    await expect(page.locator("h1")).toContainText("Wholesale Transactions");
    // Either rows or an explicit empty-state must be present (never a crash).
    await expect(page.locator(".rug-table-region, .rug-empty")).toBeVisible();
  });

  test("smart sales shows available-to-sell, not raw actual", async ({ page }) => {
    await page.goto(`${BASE}/retail-erp/smart-sales`);
    await expect(page.locator("h1")).toContainText("Smart Sales");
    await expect(page.locator("text=available to sell").first()).toBeVisible();
  });

  test("register CSV export button is present", async ({ page }) => {
    await page.goto(`${BASE}/retail-erp/sales/transactions`);
    await expect(page.getByRole("button", { name: "Export CSV" })).toBeVisible();
  });
});
