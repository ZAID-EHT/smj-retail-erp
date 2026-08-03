import { UniversalApiError } from "@/services/universal.js";
const PREFIX = "/api/method/my_store_ui.api.";
async function call(method, params = {}, httpMethod = "GET", signal) {
  // Only an absent value is dropped; an empty string is a deliberate value.
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== null).map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : value]));
  const response = await fetch(`${PREFIX}${method}${httpMethod === "GET" && query.size ? `?${query}` : ""}`, { method: httpMethod, credentials: "same-origin", cache: "no-store", signal, headers: httpMethod === "GET" ? {} : { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" }, body: httpMethod === "GET" ? undefined : JSON.stringify(params) });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) throw new UniversalApiError(payload.message || "Smart Sales request failed.", response, payload);
  return payload.message;
}
export const getSmartSales = (params, signal) => call("get_bootstrap", params, "GET", signal);
export const searchSmartCustomers = (txt, signal) => call("search_customers", { txt }, "GET", signal);
export const getCartPricing = (payload, signal) => call("get_cart_pricing", payload, "POST", signal);
export const createSmartOrder = (payload) => call("create_draft_sales_order", { payload }, "POST");
