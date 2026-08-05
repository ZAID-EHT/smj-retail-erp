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

// The sales-person roster and the actions behind the admin page that the customer
// form's "Add / edit / delete" button opens.
export const salesPersonAdminUrl = () => "/retail-erp/admin/sales-persons";
export const listSalesPersons = (params = {}, signal) =>
  call("list_sales_persons", {
    query: params.query || "",
    include_disabled: params.includeDisabled ? 1 : 0,
  }, { signal });
export const addSalesPerson = (salesPersonName, signal) =>
  call("add_sales_person", { sales_person_name: salesPersonName }, { signal, httpMethod: "POST" });
export const renameSalesPerson = (name, salesPersonName, signal) =>
  call("rename_sales_person", { name, sales_person_name: salesPersonName }, { signal, httpMethod: "POST" });
export const deleteSalesPerson = (name, signal) =>
  call("delete_sales_person", { name }, { signal, httpMethod: "POST" });
export const setSalesPersonEnabled = (name, enabled, signal) =>
  call("set_sales_person_enabled", { name, enabled: enabled ? 1 : 0 }, { signal, httpMethod: "POST" });

export const getCustomerSalesAssignment = (customer, signal) =>
  call("get_customer_sales_assignment", { customer }, { signal });
export const assignCustomerSalesTeam = (customer, team, signal) =>
  call("assign_customer_sales_team", { customer, team: team || "" }, { signal, httpMethod: "POST" });

// The customer form assigns by sales manager, not by team: the manager identifies
// the team that still carries the commission split.
export const searchSalesManagers = (query = "", signal) =>
  call("search_sales_managers", { query }, { signal });
export const assignCustomerSalesManager = (
  customer, { salesManager, team, commissionRate, salesPerson } = {}, signal,
) =>
  call("assign_customer_sales_manager", {
    customer,
    sales_manager: salesManager || "",
    team: team || "",
    // A blank rate means "follow the team's", and a blank person means "nobody is
    // named", so both must reach the server as empty strings rather than being
    // dropped as absent.
    commission_rate: commissionRate === null || commissionRate === undefined ? "" : commissionRate,
    sales_person: salesPerson || "",
  }, { signal, httpMethod: "POST" });

export const getDocumentSalesTeam = (doctype, name, signal) =>
  call("get_document_sales_team", { doctype, name }, { signal });

export const searchSalesTeams = (params, signal) =>
  call("search_sales_teams", params || {}, { signal });
export const getSalesTeamSnapshot = (params, signal) =>
  call("get_sales_team_snapshot", params || {}, { signal });
