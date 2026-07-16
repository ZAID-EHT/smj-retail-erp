import { UniversalApiError } from "@/services/universal.js";

const PREFIX = "/api/method/my_store_ui.analytics_pages.";

function message(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* Frappe response envelopes vary. */ }
  return payload?.message?.message || payload?.message || fallback;
}

async function get(method, params = {}, signal) {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ""));
  const response = await fetch(`${PREFIX}${method}${query.size ? `?${query}` : ""}`, {
    credentials: "same-origin",
    cache: "no-store",
    signal,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) throw new UniversalApiError(message(payload, "The analytics page could not be loaded."), response, payload);
  return payload.message;
}

export const searchAnalyticsLink = (page, fieldname, txt, signal) => get("search_link", { page, fieldname, txt }, signal);
export const getSalesFunnel = (params, signal) => get("get_sales_funnel", params, signal);
export const getWarehouseCapacity = (params, signal) => get("get_warehouse_capacity", params, signal);
