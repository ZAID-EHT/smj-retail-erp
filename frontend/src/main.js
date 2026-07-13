import { createApp } from "vue";

import App from "./App.vue";
import StandaloneRoot from "./StandaloneRoot.vue";
import { focusTrap, installDialogFocusManager } from "./directives/focusTrap.js";
import { createSessionStore } from "./services/session.js";
import { createRetailRouter, DESK_BASE_PATH, routeFromLocation, STANDALONE_BASE_PATH } from "./router/index.js";
import "./design/tokens.css";
import "./design/base.css";
import "./design/responsive.css";
import "./design/standalone.css";
import "./design/universal.css";
import "./design/generated-ux.css";

let activeInstance = null;

export function mount(target, context = {}) {
  if (activeInstance) {
    activeInstance.stopDialogFocus?.();
    activeInstance.app.unmount();
  }

  const router = createRetailRouter(DESK_BASE_PATH);
  const app = createApp(App, { context });
  app.directive("focus-trap", focusTrap);
  app.provide("retailContext", context);
  app.use(router);
  app.mount(target);
  const stopDialogFocus = installDialogFocusManager();

  activeInstance = {
    app,
    router,
    stopDialogFocus,
    syncRoute() {
      const route = routeFromLocation(DESK_BASE_PATH);
      if (router.currentRoute.value.fullPath !== route) {
        router.replace(route);
      }
    },
    closeTransientUi() {
      window.dispatchEvent(new CustomEvent("retail-erp:close-transient-ui"));
    },
  };

  return activeInstance;
}

export async function mountStandalone(target, branding = {}) {
  const session = createSessionStore();
  await session.refresh();
  const pathname = window.location.pathname.replace(/\/+$/, "") || "/";
  if (session.state.authenticated && (pathname === "/" || pathname === "/retail-erp")) {
    window.location.replace(session.state.landingRoute);
    return null;
  }
  if (!session.state.authenticated && pathname.startsWith("/retail-erp")) {
    const query = new URLSearchParams({ return_to: `${window.location.pathname}${window.location.search}` });
    window.location.replace(`/?${query}`);
    return null;
  }
  const router = createRetailRouter(STANDALONE_BASE_PATH);
  router.beforeEach(async (to) => {
    if (!session.state.authenticated) return true;
    const result = await session.authorize(`/retail-erp${to.fullPath}`);
    if (result.outcome === "allowed") return true;
    if (result.outcome === "authentication_required") return false;
    const fallback = (result.route || "/retail-erp/permission-denied").replace(/^\/retail-erp/, "");
    if (to.path === fallback) return true;
    return fallback;
  });
  const app = createApp(StandaloneRoot, { session, branding });
  app.directive("focus-trap", focusTrap);
  app.use(router);
  app.mount(target);
  installDialogFocusManager();

  window.addEventListener("retail-erp:session-expired", () => {
    const returnTo = window.location.pathname.startsWith("/retail-erp/") ? window.location.pathname + window.location.search : "";
    session.clear(true);
    const query = new URLSearchParams({ session_expired: "1" });
    if (returnTo) query.set("return_to", returnTo);
    window.location.replace(`/?${query}`);
  }, { once: true });
  return { app, router, session };
}

// Frappe's asset loader evaluates bundles inside its own callback scope, so an
// IIFE library variable is not guaranteed to become a window property.
// Publish the intentionally small mount contract explicitly for the Desk Page.
if (typeof window !== "undefined") {
  window.RetailERPFrontend = { mount, mountStandalone };
  window.addEventListener("DOMContentLoaded", () => {
    const target = document.getElementById("retail-erp-root");
    if (target) mountStandalone(target, window.retailERPConfig || {});
  }, { once: true });
}
