<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from "vue";

import { SmjChevronDown } from "@/components/icons";
import { moduleIcon } from "@/components/icons/moduleIconMap.js";
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
