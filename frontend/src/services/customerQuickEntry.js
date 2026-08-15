const PREFIX = "/api/method/my_store_ui.quick_entry.customer.";

async function call(method, params = {}, { post = false } = {}) {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined);
  const options = { credentials: "same-origin", cache: "no-store" };
  let url = `${PREFIX}${method}`;
  if (post) {
    options.method = "POST";
    options.headers = { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" };
    options.body = JSON.stringify(Object.fromEntries(entries));
  } else {
    options.method = "GET";
    const q = new URLSearchParams(entries.map(([k, v]) => [k, String(v)]));
    if (q.size) url += `?${q}`;
  }
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    let m = null;
    try { if (payload._server_messages) m = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message; } catch { m = null; }
    throw new Error(m || "Customer save failed.");
  }
  return payload.message;
}

export const createCustomer = (values, name) => call("create_customer", name ? { values, name } : { values }, { post: true });
export const getCustomer = (name) => call("get_customer", { name });
export const findDuplicateCustomers = (customer_name) => call("find_duplicate_customers", { customer_name });
// Only the WhatsApp number has to be unique. Asked while typing so the answer
// arrives before the save; the save enforces the same rule regardless.
export const checkWhatsappNumber = (whatsapp_no, name) =>
  call("check_whatsapp_number", name ? { whatsapp_no, name } : { whatsapp_no });
// The three Price Categories -- Wholesale, Department, Retail -- and which of them
// the site actually has a selling Price List for.
export const getPriceCategories = () => call("get_price_categories");
export const previewCustomerId = () => call("preview_customer_id");
