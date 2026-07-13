const FOCUSABLE = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

function visibleControls(element) {
  return [...element.querySelectorAll(FOCUSABLE)].filter((control) => control.getClientRects().length);
}

export const focusTrap = {
  mounted(element) {
    if (element.dataset.retailFocusTrap === "1") return;
    element.dataset.retailFocusTrap = "1";
    const previousFocus = document.activeElement;
    const onKeydown = (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        const closeControl = element.querySelector(
          "[data-dialog-close], button[aria-label*='Close'], header button:last-child, footer button",
        );
        closeControl?.click();
        return;
      }
      if (event.key !== "Tab") return;
      const controls = visibleControls(element);
      if (!controls.length) return;
      const first = controls[0];
      const last = controls.at(-1);
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    element.__retailFocusTrap = { onKeydown, previousFocus };
    element.addEventListener("keydown", onKeydown);
    requestAnimationFrame(() => visibleControls(element)[0]?.focus());
  },
  beforeUnmount(element) {
    const state = element.__retailFocusTrap;
    if (!state) return;
    element.removeEventListener("keydown", state.onKeydown);
    if (state.previousFocus?.isConnected) state.previousFocus.focus();
    delete element.__retailFocusTrap;
    delete element.dataset.retailFocusTrap;
  },
};

export function installDialogFocusManager() {
  const attach = (root) => {
    if (!(root instanceof Element)) return;
    if (root.matches('[role="dialog"][aria-modal="true"]')) focusTrap.mounted(root);
    root.querySelectorAll?.('[role="dialog"][aria-modal="true"]').forEach((dialog) => focusTrap.mounted(dialog));
  };
  const detach = (root) => {
    if (!(root instanceof Element)) return;
    if (root.dataset.retailFocusTrap === "1") focusTrap.beforeUnmount(root);
    root.querySelectorAll?.('[data-retail-focus-trap="1"]').forEach((dialog) => focusTrap.beforeUnmount(dialog));
  };
  document.querySelectorAll('[role="dialog"][aria-modal="true"]').forEach((dialog) => focusTrap.mounted(dialog));
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      mutation.addedNodes.forEach(attach);
      mutation.removedNodes.forEach(detach);
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
  return () => {
    observer.disconnect();
    document.querySelectorAll('[data-retail-focus-trap="1"]').forEach((dialog) => focusTrap.beforeUnmount(dialog));
  };
}
