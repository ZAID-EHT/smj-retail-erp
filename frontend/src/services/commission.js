import { UniversalApiError } from "@/services/universal.js";

const PREFIX = "/api/method/my_store_ui.commission.";

function message(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* envelope shapes vary */ }
  return payload?.message?.message || payload?.message || fallback;
}

// Only an absent value is dropped. An empty string is a deliberate value -- a
// cleared filter means "all" -- so it must still reach the server.
function params(values) {
  return new URLSearchParams(
    Object.entries(values || {})
      .filter(([, value]) => value !== undefined && value !== null)
      .map(([key, value]) => [key, String(value)]),
  );
}

async function call(method, values, signal) {
  const query = params(values);
  const response = await fetch(`${PREFIX}${method}${query.size ? `?${query}` : ""}`, {
    method: "GET", credentials: "same-origin", cache: "no-store", signal,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    throw new UniversalApiError(
      message(payload, "The request could not be completed."), response, payload);
  }
  return payload.message;
}

export const listCommissions = (values, signal) => call("list_commissions", values, signal);
export const getTeamPerformance = (values, signal) => call("get_team_performance", values, signal);
export const getCustomerCommissionHistory = (values, signal) =>
  call("get_customer_commission_history", values, signal);

export function commissionExportUrl(values) {
  const query = params(values);
  return `${PREFIX}export_commissions${query.size ? `?${query}` : ""}`;
}
