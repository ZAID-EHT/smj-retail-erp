const PREFIX = "/api/method/my_store_ui.setup_wizard.";

async function call(method, { post = false, body = {} } = {}) {
  const options = { credentials: "same-origin", cache: "no-store" };
  if (post) {
    options.method = "POST";
    options.headers = { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" };
    options.body = JSON.stringify(body);
  } else {
    options.method = "GET";
  }
  const response = await fetch(`${PREFIX}${method}`, options);
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    let message = null;
    try { if (payload._server_messages) message = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message; } catch { message = null; }
    throw new Error(message || "Setup is unavailable.");
  }
  return payload.message;
}

export const getSetupStatus = () => call("get_setup_status");
export const getSetupOptions = () => call("get_setup_options");
export const createCompany = (values) => call("create_company", { post: true, body: { values } });
