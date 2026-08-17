const PREFIX = "/api/method/my_store_ui.role_pages.";

async function call(method, params = {}, { post = false } = {}) {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined);
  const options = { credentials: "same-origin", cache: "no-store" };
  let url = `${PREFIX}${method}`;
  if (post) {
    options.method = "POST";
    options.headers = { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" };
    options.body = JSON.stringify(Object.fromEntries(entries));
  } else {
    options.method = "GET";
    const q = new URLSearchParams(entries.map(([k, v]) => [k, String(v)]));
    if (q.size) url += `?${q}`;
  }
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    let m = null;
    try { if (payload._server_messages) m = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message; } catch { m = null; }
    throw new Error(m || "Role access is unavailable.");
  }
  return payload.message;
}

export const getPageCatalogue = () => call("get_page_catalogue");
export const listManageableRoles = () => call("list_manageable_roles");
export const createRole = (role_name) => call("create_role", { role_name }, { post: true });
export const createRoleWithPageAccess = (values) =>
  call("create_role_with_page_access", values, { post: true });
export const getRolePageAccess = (role) => call("get_role_page_access", { role });
export const saveRolePageAccess = (role, paths) =>
  call("save_role_page_access", { role, paths }, { post: true });
export const clearRolePageAccess = (role) => call("clear_role_page_access", { role }, { post: true });
