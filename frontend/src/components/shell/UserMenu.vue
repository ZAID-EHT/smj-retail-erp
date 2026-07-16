<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from "vue";
import { SmjChevronDown, SmjHelp, SmjLogout, SmjProfile } from "@/components/icons";

const session = inject("retailSession", null);
const root = ref(null);
const open = ref(false);
const shortcutsOpen = ref(false);
const fullName = computed(() => session?.state?.displayName || window.frappe?.session?.user_fullname || window.frappe?.session?.user || "User");
const userId = computed(() => session?.state?.user || window.frappe?.session?.user || "");
const company = computed(() => session?.state?.company || window.frappe?.boot?.sysdefaults?.company || "");
const initials = computed(() =>
  fullName.value.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]?.toUpperCase()).join("") || "U",
);

function closeOnOutsideClick(event) {
  if (!root.value?.contains(event.target)) { open.value = false; shortcutsOpen.value = false; }
}
onMounted(() => document.addEventListener("click", closeOnOutsideClick));
onBeforeUnmount(() => document.removeEventListener("click", closeOnOutsideClick));

function openProfile() {
  open.value = false;
  window.open("/app/user-profile", "_blank", "noopener");
}

async function logout() {
  if (window.__retailERPFormDirty && !window.confirm("Discard unsaved changes and sign out?")) return;
  open.value = false;
  if (session?.logout) await session.logout();
  else window.location.href = "/?cmd=web_logout";
}
</script>

<template>
  <div ref="root" class="ref-user-menu-wrap">
    <button class="ref-user-menu" type="button" aria-label="User menu" :aria-expanded="open" @click="open = !open; shortcutsOpen = false">
      <span class="ref-user-menu__avatar">{{ initials }}</span>
      <span class="ref-user-menu__name">{{ fullName }}</span>
      <SmjChevronDown size="14" decorative />
    </button>
    <div v-if="open" class="ref-user-dropdown" role="menu">
      <strong>{{ fullName }}</strong>
      <small>{{ userId }}<template v-if="company"> · {{ company }}</template></small>
      <button type="button" role="menuitem" @click="openProfile">
        <SmjProfile size="16" decorative /> My Profile
      </button>
      <button type="button" role="menuitem" :aria-expanded="shortcutsOpen" @click="shortcutsOpen = !shortcutsOpen">
        <SmjHelp size="16" decorative /> Keyboard shortcuts
      </button>
      <ul v-if="shortcutsOpen" class="ref-user-dropdown__shortcuts">
        <li><kbd>Ctrl</kbd> <kbd>G</kbd> Focus global search</li>
        <li><kbd>Esc</kbd> Close dialogs and menus</li>
        <li><kbd>↑</kbd> <kbd>↓</kbd> Navigate search results</li>
      </ul>
      <button type="button" role="menuitem" class="ref-user-dropdown__logout" @click="logout">
        <SmjLogout size="16" decorative /> Logout
      </button>
    </div>
  </div>
</template>
