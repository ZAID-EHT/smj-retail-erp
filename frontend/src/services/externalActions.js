const PREFIX = "/api/method/my_store_ui.external_actions.";

async function call(method, { params, signal } = {}) {
  const query = params ? `?${new URLSearchParams(params)}` : "";
  const response = await fetch(`${PREFIX}${method}${query}`, {
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
    throw new Error(message || "External actions unavailable.");
  }
  return payload.message;
}

export function getExternalActions(filters, signal) {
  return call("get_external_actions", { params: filters, signal });
}

export function getGoLiveBlockers(signal) {
  return call("go_live_blockers", { signal });
}
