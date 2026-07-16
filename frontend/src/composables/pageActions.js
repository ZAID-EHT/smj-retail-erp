import { reactive, readonly } from "vue";

// Global, permission-aware page action registry. Pages call setPageActions()
// with an array of { key, label, icon, variant, onClick } and the header
// renders them on the left, next to the brand. Clearing on unmount keeps
// the header free of stale actions when the route changes.
const state = reactive({ actions: [] });

export function setPageActions(actions) {
  state.actions = Array.isArray(actions) ? actions.filter(Boolean) : [];
}

export function clearPageActions() {
  state.actions = [];
}

export function usePageActions() {
  return readonly(state);
}
