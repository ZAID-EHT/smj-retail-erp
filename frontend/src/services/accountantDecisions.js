const PREFIX = "/api/method/my_store_ui.finance.accountant_decisions.";

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
    // The server's own refusal is far more useful than a status code -- it names
    // the missing capability or the missing evidence.
    let message = null;
    try {
      if (payload._server_messages) {
        message = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message;
      }
    } catch {
      message = null;
    }
    throw new Error(message || "Accountant decisions unavailable.");
  }
  return payload.message;
}

export function getDecisionCentre(company, signal) {
  return call("get_decision_centre", { params: company ? { company } : null, signal });
}

export function getDecisionHistory(topic, company, signal) {
  return call("decision_history", { params: { topic: topic || "", company: company || "" }, signal });
}
