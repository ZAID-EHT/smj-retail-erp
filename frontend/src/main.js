import { createApp } from "vue";

import App from "./App.vue";
import { createRetailRouter, routeFromLocation } from "./router/index.js";
import "./design/tokens.css";
import "./design/base.css";
import "./design/responsive.css";

let activeInstance = null;

export function mount(target, context = {}) {
  if (activeInstance) {
    activeInstance.app.unmount();
  }

  const router = createRetailRouter();
  const app = createApp(App, { context });
  app.provide("retailContext", context);
  app.use(router);
  app.mount(target);

  activeInstance = {
    app,
    router,
    syncRoute() {
      const route = routeFromLocation();
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

// Frappe's asset loader evaluates bundles inside its own callback scope, so an
// IIFE library variable is not guaranteed to become a window property.
// Publish the intentionally small mount contract explicitly for the Desk Page.
if (typeof window !== "undefined") {
  window.RetailERPFrontend = { mount };
}
