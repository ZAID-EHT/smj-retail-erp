import { UniversalApiError } from "@/services/universal.js";

const PREFIX = "/api/method/my_store_ui.";

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
    throw new UniversalApiError(message(payload, "The request could not be completed."), response, payload);
  }
  return payload.message;
}

/* Accounts workspace */
export const getAccountsWorkspace = (company, signal) =>
  call("accounts_workspace.get_accounts_workspace", { company }, { signal });

/* Henderson management analysis */
export const getHendersonAnalysis = (params, signal) =>
  call("henderson.get_henderson_analysis", params || {}, { signal });
export const saveHendersonAnalysis = (params, signal) =>
  call("henderson.save_henderson_analysis", params, { signal, httpMethod: "POST" });

/* Print format administration */
export const getPrintFormatAdmin = (signal) =>
  call("print_format_admin.get_print_format_admin", {}, { signal });
export const setDefaultPrintFormat = (params, signal) =>
  call("print_format_admin.set_default_print_format", params, { signal, httpMethod: "POST" });
export const createCustomPrintFormat = (params, signal) =>
  call("print_format_admin.create_custom_print_format", params, { signal, httpMethod: "POST" });
export const setPrintFormatDisabled = (params, signal) =>
  call("print_format_admin.set_print_format_disabled", params, { signal, httpMethod: "POST" });
export const previewPrintFormat = (params, signal) =>
  call("print_format_admin.preview_print_format", params, { signal });

/* Warehouse drill-down */
export const getWarehouseStock = (params, signal) =>
  call("warehouse_stock.get_warehouse_stock", params, { signal });
export const getWarehouseBatches = (params, signal) =>
  call("warehouse_stock.get_warehouse_batches", params, { signal });
export const getWarehouseMovements = (params, signal) =>
  call("warehouse_stock.get_warehouse_movements", params, { signal });
