const PREFIX = "/api/method/my_store_ui.access_management.";

async function call(method, params = {}, { signal, post = false } = {}) {
  const entries = Object.entries(params).filter(([, value]) => value !== undefined && value !== null);
  const options = { credentials: "same-origin", cache: "no-store", signal };
  let url = `${PREFIX}${method}`;

  if (post) {
    options.method = "POST";
    options.headers = {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "",
    };
    options.body = JSON.stringify(Object.fromEntries(entries));
  } else {
    options.method = "GET";
    const query = new URLSearchParams(entries.map(([key, value]) => [key, String(value)]));
    if (query.size) url += `?${query}`;
  }

  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));

  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    // Surface the server's own message -- these are permission refusals the
    // administrator needs to read verbatim, not a generic failure.
    let message = null;
    try {
      if (payload._server_messages) {
        message = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message;
      }
    } catch {
      message = null;
    }
    const error = new Error(message || "Access management data is unavailable.");
    error.permissionDenied = response.status === 403 || payload.exc_type === "PermissionError";
    throw error;
  }
  return payload.message;
}

export const searchUsers = (filters, signal) => call("search_users", filters, { signal });
export const getUserAccessOverview = (user, signal) => call("get_user_access_overview", { user }, { signal });
export const getRoleOverview = (signal) => call("get_role_overview", {}, { signal });
export const getRolePermissionSummary = (role, signal) => call("get_role_permission_summary", { role }, { signal });
export const getRoleProfileOverview = (signal) => call("get_role_profile_overview", {}, { signal });
export const compareRoleProfiles = (first, second, signal) =>
  call("compare_role_profiles", { first, second }, { signal });
export const getRoleProfileChangeImpact = (roleProfile, signal) =>
  call("get_role_profile_change_impact", { role_profile: roleProfile }, { signal });
export const getRestrictionOptions = (doctype, search, signal) =>
  call("get_restriction_options", { doctype, search }, { signal });
export const getEmailConfigurationStatus = (signal) => call("get_email_configuration_status", {}, { signal });

export const setUserRestrictions = (user, doctype, values) =>
  call("set_user_restrictions", { user, doctype, values }, { post: true });
export const revokeUserSessions = (user) => call("revoke_user_sessions", { user }, { post: true });
