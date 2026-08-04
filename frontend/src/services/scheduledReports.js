const PREFIX = "/api/method/my_store_ui.scheduled_reports.";

async function call(method, params = {}, { post = false } = {}) {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null);
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
    throw new Error(m || "Scheduled reports unavailable.");
  }
  return payload.message;
}

export const getScheduledReportsOverview = (search, status) => call("get_scheduled_reports_overview", { search, status });
export const getSchedulableReports = (search) => call("get_schedulable_reports", { search });
export const createScheduledReport = (body) => call("create_scheduled_report", body, { post: true });
export const setScheduleEnabled = (name, enabled) => call("set_schedule_enabled", { name, enabled }, { post: true });
