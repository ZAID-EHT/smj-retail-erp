<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from "vue";

import { navigationModules } from "@/router/routes.js";

const activeMenu = ref(null);
const root = ref(null);
const session = inject("retailSession", null);
// Standalone navigation is server-owned. An empty permitted list must remain
// empty instead of falling back to the static Desk compatibility menu.
const modules = computed(() => session ? session.state.navigation : navigationModules);

function toggleMenu(name) {
  activeMenu.value = activeMenu.value === name ? null : name;
}

function closeMenus(event) {
  if (!root.value?.contains(event.target)) activeMenu.value = null;
}

onMounted(() => document.addEventListener("click", closeMenus));
onBeforeUnmount(() => document.removeEventListener("click", closeMenus));
</script>

<template>
  <nav ref="root" class="ref-module-navigation" aria-label="Main modules">
    <div
      v-for="module in modules"
      :key="module.name"
      class="ref-module-navigation__item"
      :data-accent="module.accent"
    >
      <button
        class="ref-module-button"
        type="button"
        :aria-expanded="activeMenu === module.name"
        @click="toggleMenu(module.name)"
      >
        <span class="ref-module-button__icon" aria-hidden="true">◆</span>
        {{ module.label }}
        <span class="ref-module-button__chevron" aria-hidden="true">⌄</span>
      </button>
      <div v-if="activeMenu === module.name" class="ref-module-dropdown">
        <RouterLink :to="module.path" @click="activeMenu = null">
          <strong>{{ module.label }} overview</strong>
          <small>Open the {{ module.label.toLowerCase() }} module</small>
        </RouterLink>
        <div class="ref-module-dropdown__notice">
          Detailed permitted links will be added in Stage 6.
        </div>
      </div>
    </div>
  </nav>
</template>
