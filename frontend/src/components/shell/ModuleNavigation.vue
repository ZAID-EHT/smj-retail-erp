<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { SmjChevronDown } from "@/components/icons";
import { moduleIcon } from "@/components/icons/moduleIconMap.js";
import { navigationModules } from "@/router/routes.js";

const activeMenu = ref(null);
const root = ref(null);
const route = useRoute();
const session = inject("retailSession", null);
// Standalone navigation is server-owned. An empty permitted list must remain
// empty instead of falling back to the static Desk compatibility menu.
const modules = computed(() => session ? session.state.navigation : navigationModules);

function isActiveModule(module) {
  if (!module.path || module.path === "/") return false;
  return route.path === module.path || route.path.startsWith(`${module.path}/`);
}

let lastTrigger = null;

function toggleMenu(name, event) {
  const opening = activeMenu.value !== name;
  activeMenu.value = opening ? name : null;
  if (opening) lastTrigger = event?.currentTarget || null;
}

function closeMenu() {
  activeMenu.value = null;
}

function closeMenus(event) {
  if (!root.value?.contains(event.target)) closeMenu();
}

function onKeydown(event) {
  if (event.key === "Escape" && activeMenu.value) {
    event.preventDefault();
    closeMenu();
    lastTrigger?.focus();
  }
}

onMounted(() => {
  document.addEventListener("click", closeMenus);
  document.addEventListener("keydown", onKeydown);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", closeMenus);
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <nav ref="root" class="ref-module-navigation" aria-label="Main modules">
    <div
      v-for="module in modules"
      :key="module.name"
      class="ref-module-navigation__item"
      :class="{ 'is-active': isActiveModule(module) }"
      :data-accent="module.accent"
    >
      <button
        class="ref-module-button"
        type="button"
        :aria-expanded="activeMenu === module.name"
        :aria-current="isActiveModule(module) ? 'page' : undefined"
        @click="toggleMenu(module.name, $event)"
      >
        <span class="ref-module-button__icon" aria-hidden="true">
          <component :is="moduleIcon(module.icon)" size="15" decorative />
        </span>
        {{ module.label }}
        <SmjChevronDown class="ref-module-button__chevron" size="13" decorative />
      </button>
      <div v-if="activeMenu === module.name" class="ref-module-dropdown" role="menu">
        <RouterLink
          v-for="link in module.links"
          :key="`${module.name}-${link.label}`"
          :to="link.path"
          role="menuitem"
          @click="activeMenu = null"
        >
          <span class="ref-module-dropdown__icon" aria-hidden="true">
            <component :is="moduleIcon(module.icon)" size="13" decorative />
          </span>
          <span>
            <strong>{{ link.label }}</strong>
            <small>{{ link.implemented ? `Open ${link.label}` : 'Opens safely inside Retail ERP' }}</small>
          </span>
        </RouterLink>
        <div v-if="!module.links?.length" class="ref-module-dropdown__empty">
          No permitted features are available in this module.
        </div>
      </div>
    </div>
  </nav>
</template>
