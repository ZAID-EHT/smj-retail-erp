const PREFIX = "/api/method/my_store_ui.system_operations.";

async function call(method, signal) {
  const response = await fetch(`${PREFIX}${method}`, {
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
    const error = new Error(message || "System status is unavailable.");
    error.permissionDenied = response.status === 403 || payload.exc_type === "PermissionError";
    throw error;
  }
  return payload.message;
}

export const getSystemHealth = (signal) => call("get_system_health", signal);
export const getReadiness = (signal) => call("get_readiness", signal);
export const getBackupStatus = (signal) => call("get_backup_status", signal);
export const getErrorLogSummary = (signal) => call("get_error_log_summary", signal);
