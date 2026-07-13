<script setup>
import CompanyBrand from "./CompanyBrand.vue";
import GlobalSearch from "./GlobalSearch.vue";
import ModuleNavigation from "./ModuleNavigation.vue";
import UserMenu from "./UserMenu.vue";

defineEmits(["toggle-mobile-navigation"]);
</script>

<template>
  <header class="ref-header">
    <div class="ref-header__inner">
      <button
        class="ref-icon-button ref-mobile-toggle"
        type="button"
        aria-label="Open navigation"
        @click="$emit('toggle-mobile-navigation')"
      >
        <span aria-hidden="true">☰</span>
      </button>
      <CompanyBrand />
      <ModuleNavigation class="ref-header__navigation" />
      <GlobalSearch class="ref-header__search" />
      <div class="ref-header__actions">
        <UserMenu />
      </div>
    </div>
  </header>
</template>
