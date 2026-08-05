const PREFIX = "/api/method/my_store_ui.retail_options.";

// The admin page for a given dropdown. Absolute so `window.open` lands on the
// standalone shell whichever base path the SPA is currently mounted under.
export const optionAdminUrl = (optionType) =>
  `/retail-erp/admin/options?type=${encodeURIComponent(optionType)}`;

function serverMessage(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* envelope shapes vary by error type */ }
  return fallback;
}

async function call(method, params = {}, { post = false, signal } = {}) {
  const entries = Object.entries(params).filter(([, value]) => value !== undefined && value !== null);
  const options = { credentials: "same-origin", cache: "no-store", signal };
  let url = `${PREFIX}${method}`;
  if (post) {
    options.method = "POST";
    options.headers = { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" };
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
    throw new Error(serverMessage(payload, "The option could not be saved."));
  }
  return payload.message;
}

export const listOptions = (optionType, { query, includeInactive } = {}, signal) =>
  call("list_options", {
    option_type: optionType,
    query: query || "",
    include_inactive: includeInactive ? 1 : 0,
  }, { signal });

export const listAllOptions = (signal) => call("list_all_options", {}, { signal });

export const addOption = (optionType, optionValue, sortOrder = 0) =>
  call("add_option", { option_type: optionType, option_value: optionValue, sort_order: sortOrder }, { post: true });

export const setOptionActive = (name, isActive) =>
  call("set_option_active", { name, is_active: isActive ? 1 : 0 }, { post: true });

export const deleteOption = (name) => call("delete_option", { name }, { post: true });
