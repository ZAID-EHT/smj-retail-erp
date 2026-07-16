const PREFIX = "/api/method/my_store_ui.dashboard_analytics.";

async function call(method, params = {}, signal) {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== null));
  const response = await fetch(`${PREFIX}${method}${query.size ? `?${query}` : ""}`, {
    method: "GET",
    credentials: "same-origin",
    cache: "no-store",
    signal,
  });
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    const message = payload._server_messages
      ? JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message
      : null;
    throw new Error(message || "Dashboard data is temporarily unavailable.");
  }
  return payload.message;
}

export const getHomeKpis = (signal) => call("get_home_kpis", {}, signal);
export const getSalesTrend = (months, signal) => call("get_sales_trend", { months }, signal);
export const getPaymentCollection = (signal) => call("get_payment_collection", {}, signal);
export const getTopCategories = (limit, signal) => call("get_top_categories", { limit }, signal);
export const getTopParties = (kind, limit, signal) => call("get_top_parties", { kind, limit }, signal);
export const getStockOverview = (signal) => call("get_stock_overview", {}, signal);
export const getLowStockAlerts = (limit, signal) => call("get_low_stock_alerts", { limit }, signal);
export const getRecentTransactions = (limit, signal) => call("get_recent_transactions", { limit }, signal);
