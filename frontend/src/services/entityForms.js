import { EntityApiError } from "./entities.js";

const PREFIX = "/api/method/my_store_ui.form_api.";

async function call(method, params, signal) {
  const response = await fetch(`${PREFIX}${method}`, {
    method: "POST", credentials: "same-origin", signal,
    headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" },
    body: JSON.stringify(params),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    let message = payload.message;
    try { message = JSON.parse(payload._server_messages || "[]").map((item) => JSON.parse(item).message)[0] || message; } catch { /* envelope varies */ }
    throw new EntityApiError(message || "Unable to save this record.", { status: response.status, type: payload.exc_type || "ServerError" });
  }
  return payload.message;
}

export const getEntityForm = (entity_key, name, signal) => call("get_entity_form", { entity_key, name }, signal);
export const saveEntityForm = (entity_key, values, name, request_id, signal) => call("save_entity_form", { entity_key, values, name, request_id }, signal);
export const searchLinkOptions = (entity_key, fieldname, search, signal) => call("search_link_options", { entity_key, fieldname, search }, signal);
export const getMappedDraftDetail = (entity_key, name, signal) => call("get_mapped_draft_detail", { entity_key, name }, signal);
