import { UniversalApiError } from "@/services/universal.js";

const URL = "/api/method/my_store_ui.services.frontend_routes.get_quick_create_actions";

export async function getQuickCreateActions(signal) {
  const response = await fetch(URL, { method: "GET", credentials: "same-origin", cache: "no-store", signal });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    throw new UniversalApiError(payload.message || "Unable to load create actions.", response, payload);
  }
  return payload.message?.groups || [];
}
