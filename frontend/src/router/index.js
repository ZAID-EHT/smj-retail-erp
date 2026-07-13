import { createRouter, createWebHistory } from "vue-router";

import { entityRoutes, generatedRoutes, moduleRoutes, priorityRoutes } from "./routes.js";

export const DESK_BASE_PATH = "/app/retail-erp/";
export const STANDALONE_BASE_PATH = "/retail-erp/";

export function routeFromLocation(basePath = DESK_BASE_PATH) {
  const pathname = window.location.pathname || "";
  const prefix = basePath.slice(0, -1);
  if (!pathname.startsWith(prefix)) return "/home";
  const route = pathname.slice(prefix.length) || "/home";
  return `${route}${window.location.search || ""}${window.location.hash || ""}`;
}

export function createRetailRouter(basePath = DESK_BASE_PATH) {
  const router = createRouter({
    history: createWebHistory(basePath),
    routes: [
      { path: "/", redirect: "/home" },
      ...moduleRoutes,
      ...entityRoutes,
      ...priorityRoutes,
      ...generatedRoutes,
      { path: "/:pathMatch(.*)*", name: "route-not-found", component: () => import("@/pages/NotFoundPage.vue"), meta: { title: "Page Not Found", accent: "orange" } },
    ],
    scrollBehavior: () => ({ top: 0 }),
  });

  return router;
}
