const ENDPOINT =
  "/api/method/my_store_ui.production_configuration.get_production_configuration";

export async function getProductionConfiguration(signal) {
  const response = await fetch(ENDPOINT, {
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
    let message = null;
    try {
      if (payload._server_messages) {
        message = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message;
      }
    } catch {
      message = null;
    }
    throw new Error(message || "Production configuration unavailable.");
  }
  return payload.message;
}
