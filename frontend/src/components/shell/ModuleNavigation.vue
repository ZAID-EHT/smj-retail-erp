<script setup>
import { computed, inject, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import { SmjChevronDown } from "@/components/icons";
import { moduleIcon } from "@/components/icons/moduleIconMap.js";
import { navigationModules } from "@/router/routes.js";

const activeMenu = ref(null);
const showAllLinks = ref(false);
const root = ref(null);
const route = useRoute();
const session = inject("retailSession", null);
// Standalone navigation is server-owned. An empty permitted list must remain
// empty instead of falling back to the static Desk compatibility menu.
const modules = computed(() => session ? session.state.navigation : navigationModules);
const primaryModuleNames = new Set(["home", "sales", "purchases", "inventory", "finance", "operations", "crm", "reports", "admin"]);
const displayModules = computed(() => {
  const primary = modules.value.filter((module) => primaryModuleNames.has(module.name));
  const hasSales = primary.some((module) => module.name === "sales");
  return hasSales ? primary : [...primary, ...modules.value.filter((module) => ["smart-sales", "pos"].includes(module.name))];
});

function linksFor(module) {
  const links = [...(module.links || [])];
  if (module.name === "sales") {
    for (const groupedName of ["smart-sales", "pos"]) {
      const grouped = modules.value.find((entry) => entry.name === groupedName);
      if (grouped?.path) links.unshift({ label: grouped.label, path: grouped.path, implemented: true });
    }
  }
  return links.filter((link, index, list) => list.findIndex((candidate) => candidate.path === link.path) === index);
}

function visibleLinks(module) {
  const links = linksFor(module);
  return showAllLinks.value ? links : links.slice(0, 7);
}

function linkSummary(link, module) {
  if (!link.implemented) return "Available safely inside Retail ERP";
  const value = `${link.label} ${link.path}`.toLowerCase();
  if (value.endsWith("/new")) return `Create a new ${link.label.toLowerCase()} record`;
  if (value.includes("dashboard") || value.includes("home")) return "Key metrics, alerts and recent activity";
  if (value.includes("report")) return "Reports, analysis and business insights";
  if (value.includes("customer") || value.includes("supplier")) return "Profiles, contacts and account activity";
  if (value.includes("order") || value.includes("quotation")) return "Create, review and manage documents";
  if (value.includes("invoice") || value.includes("payment")) return "Billing, balances and payment activity";
  if (value.includes("stock") || value.includes("warehouse") || value.includes("inventory")) return "Stock levels, movements and availability";
  if (value.includes("setting") || value.includes("permission") || value.includes("role")) return "Configuration and access controls";
  return `Open ${module.label} · ${link.label}`;
}

// The dropdown is teleported to <body> so it can never be clipped by an
// ancestor's overflow (the module row needs overflow-x: auto for
// horizontal scrolling on narrow desktops, and per the CSS overflow spec
// that silently forces overflow-y to "auto" too — even "visible" would be
// coerced — which clipped the dropdown to invisibility). Position is
// computed from the trigger button's own bounding box instead of CSS
// relative-positioning.
const dropdownStyle = reactive({ top: "0px", left: "0px", right: "auto" });

function isActiveModule(module) {
  if (!module.path || module.path === "/") return false;
  if (module.name === "sales" && ["/smart-sales", "/pos"].some((path) => route.path === path || route.path.startsWith(`${path}/`))) return true;
  return route.path === module.path || route.path.startsWith(`${module.path}/`);
}

let lastTrigger = null;

function toggleMenu(name, event) {
  const opening = activeMenu.value !== name;
  activeMenu.value = opening ? name : null;
  showAllLinks.value = false;
  if (!opening) return;
  const trigger = event?.currentTarget;
  lastTrigger = trigger || null;
  const anchor = trigger?.closest(".ref-module-navigation__item") || trigger;
  if (!anchor) return;
  const rect = anchor.getBoundingClientRect();
  const dropdownWidth = Math.min(560, window.innerWidth - 24);
  const overflowsRight = rect.left + dropdownWidth > window.innerWidth - 12;
  dropdownStyle.top = `${rect.bottom + 8}px`;
  if (overflowsRight) {
    dropdownStyle.left = "auto";
    dropdownStyle.right = `${Math.max(12, window.innerWidth - rect.right)}px`;
  } else {
    dropdownStyle.left = `${rect.left}px`;
    dropdownStyle.right = "auto";
  }
}

function closeMenu() {
  activeMenu.value = null;
  showAllLinks.value = false;
}

function closeMenus(event) {
  if (root.value?.contains(event.target)) return;
  if (event.target.closest?.(".ref-module-dropdown")) return;
  closeMenu();
}

function closeOnScroll(event) {
  if (event.target?.closest?.(".ref-module-dropdown")) return;
  closeMenu();
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
  window.addEventListener("resize", closeMenu);
  window.addEventListener("scroll", closeOnScroll, true);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", closeMenus);
  document.removeEventListener("keydown", onKeydown);
  window.removeEventListener("resize", closeMenu);
  window.removeEventListener("scroll", closeOnScroll, true);
});
</script>

<template>
  <nav ref="root" class="ref-module-navigation" aria-label="Main modules">
    <div
      v-for="module in displayModules"
      :key="module.name"
      class="ref-module-navigation__item"
      :class="{ 'is-active': isActiveModule(module) }"
      :data-accent="module.accent"
    >
      <RouterLink
        :to="module.path"
        class="ref-module-button"
        :aria-current="isActiveModule(module) ? 'page' : undefined"
        @click="closeMenu"
      >
        <span class="ref-module-button__icon" aria-hidden="true">
          <component :is="moduleIcon(module.icon)" size="15" decorative />
        </span>
        {{ module.label }}
      </RouterLink>
      <button
        v-if="linksFor(module).length"
        type="button"
        class="ref-module-button__toggle"
        :aria-expanded="activeMenu === module.name"
        :aria-label="`${module.label} submenu`"
        @click="toggleMenu(module.name, $event)"
      >
        <SmjChevronDown class="ref-module-button__chevron" size="13" decorative />
      </button>
      <Teleport to="body">
        <div
          v-if="activeMenu === module.name"
          class="ref-app-shell ref-module-dropdown"
          role="menu"
          :data-accent="module.accent"
          :style="{ position: 'fixed', top: dropdownStyle.top, left: dropdownStyle.left, right: dropdownStyle.right }"
        >
          <header class="ref-module-dropdown__header">
            <span class="ref-module-dropdown__hero-icon" aria-hidden="true">
              <component :is="moduleIcon(module.icon)" size="22" decorative />
            </span>
            <span class="ref-module-dropdown__heading">
              <strong>{{ module.label }}</strong>
              <small>{{ linksFor(module).length }} pages available to you</small>
            </span>
            <RouterLink class="ref-module-dropdown__overview" :to="module.path" role="menuitem" @click="closeMenu">
              Overview <span aria-hidden="true">→</span>
            </RouterLink>
          </header>
          <div class="ref-module-dropdown__section-title">
            <span>Quick access</span>
            <small>Only pages permitted for your account are shown</small>
          </div>
          <div class="ref-module-dropdown__links">
          <RouterLink
            v-for="link in visibleLinks(module)"
            :key="`${module.name}-${link.label}`"
            :to="link.path"
            role="menuitem"
            @click="activeMenu = null"
          >
            <span class="ref-module-dropdown__icon" aria-hidden="true">
              <component :is="moduleIcon(module.icon)" size="15" decorative />
            </span>
            <span class="ref-module-dropdown__copy">
              <strong>{{ link.label }}</strong>
              <small>{{ linkSummary(link, module) }}</small>
            </span>
            <span class="ref-module-dropdown__arrow" aria-hidden="true">→</span>
          </RouterLink>
          </div>
          <button
            v-if="linksFor(module).length > 7"
            class="ref-module-dropdown__more"
            type="button"
            @click="showAllLinks = !showAllLinks"
          >
            {{ showAllLinks ? 'Show fewer links' : `Show all ${linksFor(module).length} links` }}
          </button>
          <div v-if="!module.links?.length" class="ref-module-dropdown__empty">
            No permitted features are available in this module.
          </div>
        </div>
      </Teleport>
    </div>
  </nav>
</template>
