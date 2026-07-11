const METHOD = "/api/method/my_store_ui.entity_api.get_entity_list";

export class EntityApiError extends Error {
  constructor(message, { status = 500, type = "ServerError" } = {}) {
    super(message);
    this.name = "EntityApiError";
    this.status = status;
    this.type = type;
    this.permissionDenied = status === 403 || type === "PermissionError";
  }
}

export async function getEntityList(params, signal) {
  const response = await fetch(METHOD, {
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
