import { reactive } from "vue";

const state = reactive({ toasts: [] });
let nextId = 1;
const DEFAULT_TIMEOUT_MS = 5000;

function dismissToast(id) {
  const index = state.toasts.findIndex((toast) => toast.id === id);
  if (index !== -1) state.toasts.splice(index, 1);
}

function pushToast({ type = "info", title, message = "", timeout = DEFAULT_TIMEOUT_MS, actionLabel, onAction } = {}) {
  const id = nextId++;
  state.toasts.push({ id, type, title, message, actionLabel, onAction });
  if (timeout > 0) setTimeout(() => dismissToast(id), timeout);
  return id;
}

export function useToast() {
  return {
    toasts: state.toasts,
    success: (title, message, extra) => pushToast({ type: "success", title, message, ...extra }),
    error: (title, message, extra) => pushToast({ type: "error", title, message, timeout: 8000, ...extra }),
    warning: (title, message, extra) => pushToast({ type: "warning", title, message, ...extra }),
    info: (title, message, extra) => pushToast({ type: "info", title, message, ...extra }),
    dismiss: dismissToast,
  };
}
