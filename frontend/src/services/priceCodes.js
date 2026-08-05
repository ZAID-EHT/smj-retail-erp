const PREFIX = "/api/method/my_store_ui.price_codes.";

// Absolute, so the Product form's Price Codes button opens the standalone shell
// in a new tab regardless of the base path the SPA is mounted under.
export const priceCodeAdminUrl = () => "/retail-erp/admin/price-codes";

function serverMessage(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* envelope shapes vary by error type */ }
  return fallback;
}

async function call(method, params = {}, { post = false, signal } = {}) {
  const entries = Object.entries(params).filter(([, value]) => value !== undefined && value !== null);
  const options = { credentials: "same-origin", cache: "no-store", signal };
  let url = `${PREFIX}${method}`;
  if (post) {
    options.method = "POST";
    options.headers = { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" };
    options.body = JSON.stringify(Object.fromEntries(entries));
  } else {
    options.method = "GET";
    const query = new URLSearchParams(
      entries.map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : String(value)]),
    );
    if (query.size) url += `?${query}`;
  }
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    throw new Error(serverMessage(payload, "The price code could not be saved."));
  }
  return payload.message;
}

export const listPriceCodes = (params = {}, signal) =>
  call("list_price_codes", {
    query: params.query || "",
    category: params.category || "",
    include_inactive: params.includeInactive ? 1 : 0,
  }, { signal });

export const getPriceCode = (name, signal) => call("get_price_code", { name }, { signal });

export const savePriceCode = (values, name) =>
  call("save_price_code", name ? { values, name } : { values }, { post: true });

export const deletePriceCode = (name) => call("delete_price_code", { name }, { post: true });

export const listCategories = (query = "", signal) => call("list_categories", { query }, { signal });

export const addCategory = (category) => call("add_category", { category }, { post: true });
