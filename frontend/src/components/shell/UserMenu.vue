<script setup>
import { computed, inject, ref } from "vue";

const session = inject("retailSession", null);
const open = ref(false);
const fullName = computed(() => session?.state?.displayName || window.frappe?.session?.user_fullname || window.frappe?.session?.user || "User");
const initials = computed(() =>
  fullName.value.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]?.toUpperCase()).join("") || "U",
);

async function logout() {
  if (window.__retailERPFormDirty && !window.confirm("Discard unsaved changes and sign out?")) return;
  open.value = false;
  if (session?.logout) await session.logout();
  else window.location.href = "/?cmd=web_logout";
}
</script>

<template>
  <div class="ref-user-menu-wrap">
    <button class="ref-user-menu" type="button" aria-label="User menu" :aria-expanded="open" @click="open = !open">
      <span class="ref-user-menu__avatar">{{ initials }}</span>
      <span class="ref-user-menu__name">{{ fullName }}</span>
      <span aria-hidden="true">⌄</span>
    </button>
    <div v-if="open" class="ref-user-dropdown">
      <strong>{{ fullName }}</strong>
      <small>{{ session?.state?.user || window.frappe?.session?.user }}</small>
      <button type="button" @click="logout">Logout</button>
    </div>
  </div>
</template>
