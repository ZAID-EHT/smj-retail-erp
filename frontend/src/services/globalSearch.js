const SEARCH_URL = "/api/method/my_store_ui.search.global_search";

export async function searchRetailERP(text, signal) {
  const query = new URLSearchParams({ text, limit: "20" });
  const response = await fetch(`${SEARCH_URL}?${query}`, {
    method: "GET",
    credentials: "same-origin",
    cache: "no-store",
    signal,
  });
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 || payload.exc_type === "AuthenticationError") {
    window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
    throw new Error("Your session expired.");
  }
  if (!response.ok || payload.exc) throw new Error("Search is temporarily unavailable.");
  return payload.message?.results || [];
}
