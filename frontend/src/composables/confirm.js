import { reactive } from "vue";

const state = reactive({ dialog: null });

// Returns a Promise<boolean> — true if the user confirmed, false on cancel/Escape.
export function confirmAction({ title, message, confirmLabel = "Confirm", cancelLabel = "Cancel", danger = false } = {}) {
  return new Promise((resolve) => {
    state.dialog = {
      title,
      message,
      confirmLabel,
      cancelLabel,
      danger,
      resolve: (value) => {
        state.dialog = null;
        resolve(value);
      },
    };
  });
}

export function useConfirmDialog() {
  return state;
}
