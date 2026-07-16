const PREFIX = "/api/method/my_store_ui.module_dashboards.";

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

export const getAccountsDashboard = (signal) => call("get_accounts_dashboard", {}, signal);
export const getPaymentsDashboard = (signal) => call("get_payments_dashboard", {}, signal);
export const getBuyingDashboard = (signal) => call("get_buying_dashboard", {}, signal);
export const getCrmDashboard = (signal) => call("get_crm_dashboard", {}, signal);
export const getSellingDashboard = (signal) => call("get_selling_dashboard", {}, signal);
export const getStockDashboard = (signal) => call("get_stock_dashboard", {}, signal);

export const MODULE_DASHBOARD_LOADERS = {
  finance: [getAccountsDashboard, getPaymentsDashboard],
  purchases: [getBuyingDashboard],
  crm: [getCrmDashboard],
  sales: [getSellingDashboard],
  inventory: [getStockDashboard],
};
