import { UniversalApiError } from "@/services/universal.js";

const PREFIX = "/api/method/my_store_ui.priority_pages.";

function message(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* Frappe response envelopes vary. */ }
  return payload?.message?.message || payload?.message || fallback;
}

export async function callPriority(method, params = {}, { signal, httpMethod = "GET" } = {}) {
  const isGet = httpMethod === "GET";
  const query = new URLSearchParams(
    Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : value]),
  );
  const response = await fetch(`${PREFIX}${method}${isGet && query.size ? `?${query}` : ""}`, {
    method: httpMethod,
    credentials: "same-origin",
    cache: "no-store",
    signal,
    headers: isGet ? {} : {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "",
    },
    body: isGet ? undefined : JSON.stringify(params),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    throw new UniversalApiError(message(payload, "The page could not be loaded."), response, payload);
  }
  return payload.message;
}

export const getPriorityRouteDefinition = (path, signal) => callPriority("get_priority_route_definition", { path }, { signal });
export const getModuleDashboard = (module, signal) => callPriority("get_module_dashboard", { module }, { signal });
export const getReportHub = (group, signal) => callPriority("get_report_hub", { group }, { signal });
export const getPriorityReportDefinition = (report, signal) => callPriority("get_priority_report_definition", { report }, { signal });
export const runPriorityReport = (report, filters, signal) => callPriority("run_priority_report", { report, filters }, { signal, httpMethod: "POST" });
export const getTreeNodes = (path, parent, company, signal) => callPriority("get_tree_nodes", { path, parent, company }, { signal });
export const getSpecialPage = (path, signal) => callPriority("get_special_page", { path }, { signal });
