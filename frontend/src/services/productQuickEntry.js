const PREFIX = "/api/method/my_store_ui.quick_entry.product.";

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
    throw new Error(m || "Product save failed.");
  }
  return payload.message;
}

export const createProduct = (values, name) => call("create_product", name ? { values, name } : { values }, { post: true });
export const getProduct = (name) => call("get_product", { name });

export async function getDefaultMargin(signal) {
  const r = await fetch("/api/method/my_store_ui.quick_entry.product.get_default_margin", {
    credentials: "same-origin", cache: "no-store", signal,
  });
  const p = await r.json().catch(() => ({}));
  if (!r.ok || p.exc) return null;
  return p.message?.margin ?? null;
}

export async function saveDefaultMargin(margin, signal) {
  const r = await fetch("/api/method/my_store_ui.quick_entry.product.save_default_margin", {
    method: "POST",
    credentials: "same-origin",
    signal,
    headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" },
    body: JSON.stringify({ margin }),
  });
  const p = await r.json().catch(() => ({}));
  if (!r.ok || p.exc) {
    const detail = (() => {
      try {
        const msgs = JSON.parse(p?._server_messages || "[]");
        return msgs.length ? JSON.parse(msgs[0]).message : null;
      } catch { return null; }
    })();
    throw new Error(detail || "Could not save the default margin.");
  }
  return p.message?.margin ?? margin;
}
