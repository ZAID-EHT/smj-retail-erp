const PREFIX = "/api/method/my_store_ui.universal.api.";

export class UniversalApiError extends Error {
  constructor(message, response = {}, payload = {}) {
    super(message || "The requested feature could not be loaded.");
    this.name = "UniversalApiError";
    this.status = response.status || 500;
    this.type = payload.exc_type || "ServerError";
    this.permissionDenied = this.status === 403 || this.type === "PermissionError";
    this.notFound = this.status === 404 || this.type === "DoesNotExistError";
    this.authenticationRequired = this.status === 401 || this.type === "AuthenticationError";
    if (this.authenticationRequired) window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
  }
}

function serverMessage(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* Frappe envelopes vary. */ }
  return payload?.message?.message || payload?.message || fallback;
}

export async function callUniversal(method, params = {}, { signal, httpMethod = "POST" } = {}) {
  const isGet = httpMethod === "GET";
  const url = `${PREFIX}${method}${isGet ? `?${new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== null).map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : value]))}` : ""}`;
  const response = await fetch(url, {
    method: httpMethod,
    credentials: "same-origin",
    cache: "no-store",
    signal,
    headers: isGet ? {} : { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" },
    body: isGet ? undefined : JSON.stringify(params),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) throw new UniversalApiError(serverMessage(payload, "The request could not be completed."), response, payload);
  return payload.message;
}

export const getMetadata = (feature, signal) => callUniversal("get_doctype_metadata", { feature }, { signal, httpMethod: "GET" });
export const getListConfiguration = (feature, signal) => callUniversal("get_list_configuration", { feature }, { signal, httpMethod: "GET" });
export const getDocumentList = (params, signal) => callUniversal("get_document_list", params, { signal });
export const getDocumentDetail = (feature, name, signal) => callUniversal("get_document_detail", { feature, name }, { signal, httpMethod: "GET" });
export const createDocument = (feature, values) => callUniversal("create_document", { feature, values });
export const updateDocument = (feature, name, values, modified) => callUniversal("update_document", { feature, name, values, modified });
export const deleteDocument = (feature, name, modified) => callUniversal("delete_document", { feature, name, modified });
export const runDocumentAction = (feature, name, action, modified) => callUniversal("run_document_action", { feature, name, action, modified });
export const getWorkflowActions = (feature, name, signal) => callUniversal("get_workflow_actions", { feature, name }, { signal, httpMethod: "GET" });
export const runWorkflowAction = (feature, name, action, modified) => callUniversal("run_workflow_action", { feature, name, action, modified });
export const getLinkOptions = (feature, fieldname, search, parentFieldname, signal) => callUniversal("get_link_options", { feature, fieldname, search, parent_fieldname: parentFieldname }, { signal, httpMethod: "GET" });
export const getTimeline = (feature, name, signal) => callUniversal("get_document_timeline", { feature, name }, { signal, httpMethod: "GET" });
export const getRelated = (feature, name, signal) => callUniversal("get_related_documents", { feature, name }, { signal, httpMethod: "GET" });
export const getPrintFormats = (feature, name, signal) => callUniversal("get_print_formats", { feature, name }, { signal, httpMethod: "GET" });
export const getReportDefinition = (feature, signal) => callUniversal("get_report_definition", { feature: `report:${feature}` }, { signal, httpMethod: "GET" });
export const runReport = (feature, filters) => callUniversal("run_report", { feature: `report:${feature}`, filters });
