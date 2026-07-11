import { createRouter, createWebHistory } from "vue-router";

import { entityRoutes, moduleRoutes } from "./routes.js";

const BASE_PATH = "/app/retail-erp/";

export function routeFromLocation() {
  const pathname = window.location.pathname || "";
  const prefix = BASE_PATH.slice(0, -1);
  if (!pathname.startsWith(prefix)) return "/home";
  const route = pathname.slice(prefix.length) || "/home";
  return `${route}${window.location.search || ""}${window.location.hash || ""}`;
}

export function createRetailRouter() {
  const router = createRouter({
    history: createWebHistory(BASE_PATH),
    routes: [
      { path: "/", redirect: "/home" },
      ...moduleRoutes,
      ...entityRoutes,
      { path: "/:pathMatch(.*)*", redirect: "/home" },
    ],
    scrollBehavior: () => ({ top: 0 }),
  });

  return router;
}
