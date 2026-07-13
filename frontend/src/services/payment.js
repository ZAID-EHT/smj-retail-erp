import { EntityApiError } from "./entities.js";
const PREFIX = "/api/method/my_store_ui.payment_api.";
async function call(method, params, signal) { const response = await fetch(`${PREFIX}${method}`, { method: "POST", credentials: "same-origin", signal, headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" }, body: JSON.stringify(params) }); const payload = await response.json().catch(() => ({})); if (!response.ok || payload.exc) throw new EntityApiError(payload.message || "Payment request failed.", { status: response.status, type: payload.exc_type || "ServerError" }); return payload.message; }
export const getOutstandingReferences = (args, signal) => call("get_outstanding_references", { args }, signal);
export const getAccountOptions = (company, payment_type, signal) => call("get_account_options", { company, payment_type }, signal);
