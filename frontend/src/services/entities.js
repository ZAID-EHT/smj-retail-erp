const METHOD_PREFIX = "/api/method/my_store_ui.entity_api.";

export class EntityApiError extends Error {
  constructor(message, { status = 500, type = "ServerError" } = {}) {
    super(message);
    this.name = "EntityApiError";
    this.status = status;
    this.type = type;
    this.permissionDenied = status === 403 || type === "PermissionError";
    this.notFound = status === 404 || type === "DoesNotExistError";
    this.authenticationRequired = status === 401 || type === "AuthenticationError";
    if (this.authenticationRequired && window.retailERPConfig) {
      window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    }
  }
}

export async function callEntityApi(method, params, signal) {
  const response = await fetch(`${METHOD_PREFIX}${method}`, {
    method: "POST",
    credentials: "same-origin",
    signal,
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "",
    },
    body: JSON.stringify(params),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    let firstMessage = null;
    try {
      const serverMessages = payload._server_messages ? JSON.parse(payload._server_messages) : [];
      firstMessage = serverMessages.length ? JSON.parse(serverMessages[0]).message : null;
    } catch {
      // Frappe can omit or vary the message envelope for proxy/session failures.
    }
    throw new EntityApiError(firstMessage || payload.message || "Unable to load records.", {
      status: response.status,
      type: payload.exc_type || "ServerError",
    });
  }
  return payload.message;
}

export function getEntityList(params, signal) {
  return callEntityApi("get_entity_list", params, signal);
}
