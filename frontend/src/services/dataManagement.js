const PREFIX = "/api/method/my_store_ui.data_management.";

async function call(method, params = {}, signal) {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null);
  const query = new URLSearchParams(entries.map(([k, v]) => [k, String(v)]));
  const response = await fetch(`${PREFIX}${method}${query.size ? `?${query}` : ""}`, {
    method: "GET", credentials: "same-origin", cache: "no-store", signal,
  });
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) {
    let message = null;
    try {
      if (payload._server_messages) message = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message;
    } catch { message = null; }
    throw new Error(message || "Data management is unavailable.");
  }
  return payload.message;
}

export const getImportTypes = (signal) => call("get_import_types", {}, signal);
export const getImportTemplateFields = (doctype, signal) => call("get_import_template_fields", { doctype }, signal);
export const exportRecords = (doctype, limit, signal) => call("export_records", { doctype, limit }, signal);
export const getImportHistory = (signal) => call("get_import_history", {}, signal);

export function toCsv(fields, rows) {
  const esc = (v) => {
    const s = v == null ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const header = fields.join(",");
  const body = rows.map((row) => fields.map((f) => esc(row[f])).join(",")).join("\n");
  return `${header}\n${body}`;
}
