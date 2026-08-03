import { UniversalApiError } from "@/services/universal.js";

const PREFIX = "/api/method/my_store_ui.sales_team.";

function message(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* envelope shapes vary */ }
  return payload?.message?.message || payload?.message || fallback;
}

async function call(method, params = {}, { signal, httpMethod = "GET" } = {}) {
  const isGet = httpMethod === "GET";
  const query = new URLSearchParams(
    Object.entries(params)
      // Only an absent value is dropped. An empty string is a deliberate value --
      // a blank record name means "a new record", and a cleared filter means "all"
      // -- so it must reach the server. Dropping it previously made the API run
      // without a required argument and return HTTP 500.
      .filter(([, value]) => value !== undefined && value !== null)
      .map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : value]),
  );
  const response = await fetch(`${PREFIX}${method}${isGet && query.size ? `?${query}` : ""}`, {
    method: httpMethod,
    credentials: "same-origin",
    cache: "no-store",
    signal,
    headers: isGet
      ? {}
      : { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" },
    body: isGet ? undefined : JSON.stringify(params),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    // Never surface a raw traceback; the server message is the human one.
    throw new UniversalApiError(message(payload, "The request could not be completed."), response, payload);
  }
  return payload.message;
}

export const listSalesTeams = (params, signal) => call("list_sales_teams", params || {}, { signal });
export const getSalesTeam = (name, signal) => call("get_sales_team", { name: name || "" }, { signal });
export const saveSalesTeam = (payload, name, signal) =>
  call("save_sales_team", { payload, name: name || "" }, { signal, httpMethod: "POST" });
export const searchSalesPersons = (txt, signal) => call("search_sales_persons", { txt }, { signal });

export const getCustomerSalesAssignment = (customer, signal) =>
  call("get_customer_sales_assignment", { customer }, { signal });
export const assignCustomerSalesTeam = (customer, team, signal) =>
  call("assign_customer_sales_team", { customer, team: team || "" }, { signal, httpMethod: "POST" });

export const getDocumentSalesTeam = (doctype, name, signal) =>
  call("get_document_sales_team", { doctype, name }, { signal });
