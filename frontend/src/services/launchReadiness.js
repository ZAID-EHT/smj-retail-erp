const PREFIX = "/api/method/my_store_ui.launch_readiness.";
export async function getLaunchReadiness(signal) {
  const response = await fetch(`${PREFIX}get_launch_readiness`, { method: "GET", credentials: "same-origin", cache: "no-store", signal });
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    let m = null;
    try { if (payload._server_messages) m = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message; } catch { m = null; }
    throw new Error(m || "Launch readiness unavailable.");
  }
  return payload.message;
}
