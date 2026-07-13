import { reactive } from "vue";

const BOOTSTRAP_URL = "/api/method/my_store_ui.standalone.get_session_bootstrap";
const AUTHORIZE_URL = "/api/method/my_store_ui.standalone.authorize_frontend_route";

function safeServerMessage(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch {
    // Frappe response envelopes vary by authentication failure type.
  }
  return payload?.message || fallback;
}

export function createSessionStore() {
  const state = reactive({
    ready: false,
    authenticated: false,
    user: null,
    displayName: "",
    company: "",
    roles: [],
    landingRoute: "/retail-erp/home",
    navigation: [],
    csrfToken: "",
    expired: false,
    error: "",
  });

  function applyBootstrap(message = {}) {
    state.authenticated = Boolean(message.authenticated);
    state.user = message.user || null;
    state.displayName = message.display_name || "";
    state.company = message.company || "";
    state.roles = message.roles || [];
    state.landingRoute = message.landing_route || "/retail-erp/home";
    state.navigation = message.navigation || [];
    state.csrfToken = message.csrf_token || window.frappe?.csrf_token || "";
    window.frappe = window.frappe || {};
    window.frappe.csrf_token = state.csrfToken;
    window.frappe.session = {
      user: state.user || "Guest",
      user_fullname: state.displayName || state.user || "Guest",
    };
  }

  async function refresh() {
    try {
      const response = await fetch(BOOTSTRAP_URL, { method: "GET", credentials: "same-origin", cache: "no-store" });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.exc) throw new Error("Unable to verify your session.");
      applyBootstrap(payload.message);
      state.error = "";
    } catch (error) {
      applyBootstrap({ authenticated: false });
      state.error = error.message || "Unable to verify your session.";
    } finally {
      state.ready = true;
    }
    return state.authenticated;
  }

  async function login({ username, password, otp, tmpId }) {
    const body = new URLSearchParams({ cmd: "login" });
    if (otp && tmpId) {
      body.set("otp", otp);
      body.set("tmp_id", tmpId);
    } else {
      body.set("usr", username);
      body.set("pwd", password);
    }
    const response = await fetch("/api/method/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest" },
      body,
    });
    const payload = await response.json().catch(() => ({}));
    if (payload.verification && payload.message !== "Logged In") {
      return { twoFactor: true, tmpId: payload.tmp_id, verification: payload.verification };
    }
    if (!response.ok || payload.exc || payload.message !== "Logged In") {
      throw new Error(safeServerMessage(payload, "Invalid username or password."));
    }
    await refresh();
    if (!state.authenticated) throw new Error("The session could not be started.");
    state.expired = false;
    return { authenticated: true };
  }

  async function authorize(path) {
    if (!state.authenticated) return { outcome: "authentication_required", route: "/" };
    const url = `${AUTHORIZE_URL}?${new URLSearchParams({ path })}`;
    const response = await fetch(url, { method: "GET", credentials: "same-origin", cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (response.status === 401 || payload.exc_type === "AuthenticationError") {
      clear(true);
      return { outcome: "authentication_required", route: "/" };
    }
    if (!response.ok || payload.exc) return { outcome: "denied", route: "/retail-erp/permission-denied" };
    return payload.message;
  }

  async function requestPasswordReset(user) {
    const response = await fetch("/api/method/frappe.core.doctype.user.user.reset_password", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: new URLSearchParams({ user }),
    });
    if (!response.ok) throw new Error("Password reset request failed.");
    return true;
  }

  function clear(expired = false) {
    applyBootstrap({ authenticated: false });
    state.expired = expired;
    state.navigation = [];
  }

  async function logout() {
    try {
      await fetch("/api/method/logout", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": state.csrfToken || "" },
        body: "{}",
      });
    } finally {
      clear(false);
      window.location.replace("/");
    }
  }

  return { state, refresh, login, authorize, requestPasswordReset, logout, clear };
}
