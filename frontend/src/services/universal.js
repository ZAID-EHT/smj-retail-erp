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
export const runDocumentAction = (feature, name, action, modified, parameters = {}) => callUniversal("run_document_action", { feature, name, action, modified, parameters });
export const getWorkflowActions = (feature, name, signal) => callUniversal("get_workflow_actions", { feature, name }, { signal, httpMethod: "GET" });
export const runWorkflowAction = (feature, name, action, modified) => callUniversal("run_workflow_action", { feature, name, action, modified });
export const getLinkOptions = (feature, fieldname, search, parentFieldname, signal, dynamicDoctype) => callUniversal("get_link_options", { feature, fieldname, search, parent_fieldname: parentFieldname, dynamic_doctype: dynamicDoctype }, { signal, httpMethod: "GET" });
export const getTimeline = (feature, name, signal) => callUniversal("get_document_timeline", { feature, name }, { signal, httpMethod: "GET" });
export const getRelated = (feature, name, signal) => callUniversal("get_related_documents", { feature, name }, { signal, httpMethod: "GET" });
export const getDashboardConnections = (feature, name, signal) => callUniversal("get_dashboard_connections", { feature, name }, { signal, httpMethod: "GET" });
export const getPrintFormats = (feature, name, signal) => callUniversal("get_print_formats", { feature, name }, { signal, httpMethod: "GET" });
export const getReportDefinition = (feature, signal) => callUniversal("get_report_definition", { feature: `report:${feature}` }, { signal, httpMethod: "GET" });
export const runReport = (feature, filters) => callUniversal("run_report", { feature: `report:${feature}`, filters });

// Collaboration lives in a sibling module, so use its full allowlisted method prefix.
export async function callCollaboration(method, params = {}, { signal, httpMethod = "POST" } = {}) {
  const original = `${PREFIX}${method}`;
  const url = original.replace("my_store_ui.universal.api.", "my_store_ui.universal.collaboration.");
  const isGet = httpMethod === "GET";
  const target = `${url}${isGet ? `?${new URLSearchParams(Object.entries(params).filter(([, value]) => value != null).map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : value]))}` : ""}`;
  const response = await fetch(target, { method: httpMethod, credentials: "same-origin", cache: "no-store", signal, headers: isGet ? {} : { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" }, body: isGet ? undefined : JSON.stringify(params) });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) throw new UniversalApiError(serverMessage(payload, "The collaboration request could not be completed."), response, payload);
  return payload.message;
}
export const getCollaborationState = (feature, name, signal) => callCollaboration("get_collaboration_state", { feature, name }, { signal, httpMethod: "GET" });
export const addComment = (feature, name, content) => callCollaboration("add_comment", { feature, name, content });
export const removeAttachment = (feature, name, fileName) => callCollaboration("remove_attachment", { feature, name, file_name: fileName });
export const searchAssignmentUsers = (feature, name, search, signal) => callCollaboration("search_assignment_users", { feature, name, search }, { signal, httpMethod: "GET" });
export const addAssignment = (feature, name, user, dueDate, description) => callCollaboration("add_assignment", { feature, name, user, due_date: dueDate, description });
export const removeAssignment = (feature, name, user) => callCollaboration("remove_assignment", { feature, name, user });
export const addShare = (feature, name, user, permissions = {}) => callCollaboration("add_share", { feature, name, user, ...permissions });
export const removeShare = (feature, name, user) => callCollaboration("remove_share", { feature, name, user });
export const setTags = (feature, name, tags) => callCollaboration("set_tags", { feature, name, tags });
export const emailDocument = (feature, name, values) => callCollaboration("email_document", { feature, name, ...values });
export async function uploadAttachment(upload, file, signal) {
  const body = new FormData(); body.set("file", file); body.set("doctype", upload.doctype); body.set("docname", upload.docname); body.set("is_private", String(upload.is_private ?? 1));
  const response = await fetch(upload.endpoint, { method: "POST", credentials: "same-origin", signal, headers: { "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" }, body });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) throw new UniversalApiError(serverMessage(payload, "Attachment upload failed."), response, payload);
  return payload.message;
}
