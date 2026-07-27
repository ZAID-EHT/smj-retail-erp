const PREFIX = "/api/method/my_store_ui.admin_landing.";

async function call(method, signal) {
  const response = await fetch(`${PREFIX}${method}`, {
    method: "GET", credentials: "same-origin", cache: "no-store", signal,
  });
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    let message = null;
    try { if (payload._server_messages) message = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message; } catch { message = null; }
    throw new Error(message || "Administration is unavailable.");
  }
  return payload.message;
}

export const getAdminLanding = (signal) => call("get_admin_landing", signal);
