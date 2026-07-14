import { UniversalApiError } from "@/services/universal.js";

const PREFIX = "/api/method/my_store_ui.wholesale.";

function message(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* envelope shapes vary */ }
  return payload?.message?.message || payload?.message || fallback;
}

async function call(method, params = {}, { signal, httpMethod = "GET" } = {}) {
  const isGet = httpMethod === "GET";
  const query = new URLSearchParams(
    Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : value]),
  );
  const response = await fetch(`${PREFIX}${method}${isGet && query.size ? `?${query}` : ""}`, {
    method: httpMethod,
    credentials: "same-origin",
    cache: "no-store",
    signal,
    headers: isGet ? {} : { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" },
    body: isGet ? undefined : JSON.stringify(params),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    throw new UniversalApiError(message(payload, "The request could not be completed."), response, payload);
  }
  return payload.message;
}

export const getWholesaleTransactions = (params, signal) =>
  call("register.get_wholesale_transactions", params, { signal });
export const getTransactionTimeline = (salesOrder, signal) =>
  call("register.get_transaction_timeline", { sales_order: salesOrder }, { signal });
export const getCustomerCreditStatus = (customer, company, signal) =>
  call("credit.get_customer_credit_status", { customer, company }, { signal });
export const getStockAvailability = (itemCode, warehouse, company, signal) =>
  call("reservation.get_stock_availability", { item_code: itemCode, warehouse, company }, { signal });
