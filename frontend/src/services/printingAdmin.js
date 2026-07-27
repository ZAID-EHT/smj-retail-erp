const PREFIX = "/api/method/my_store_ui.printing_admin.";

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
    try { if (payload._server_messages) message = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message; } catch { message = null; }
    throw new Error(message || "Printing is unavailable.");
  }
  return payload.message;
}

export const getPrintingOverview = (signal) => call("get_printing_overview", {}, signal);
export const getPreviewCandidates = (doctype, signal) => call("get_preview_candidates", { doctype }, signal);
export const previewDocument = (doctype, name, print_format, signal) =>
  call("preview_document", { doctype, name, print_format }, signal);

export function downloadPdfUrl(doctype, name, print_format) {
  const q = new URLSearchParams({ doctype, name });
  if (print_format) q.set("print_format", print_format);
  return `/api/method/my_store_ui.printing_admin.download_pdf?${q}`;
}
