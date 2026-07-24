<script setup>
import { SmjMenu, SmjMessage, SmjNotification } from "@/components/icons";
import CompanyBrand from "./CompanyBrand.vue";
import GlobalSearch from "./GlobalSearch.vue";
import HeaderPageActions from "./HeaderPageActions.vue";
import ModuleNavigation from "./ModuleNavigation.vue";
import QuickCreateMenu from "./QuickCreateMenu.vue";
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
        <SmjMenu size="20" decorative />
      </button>
      <CompanyBrand />
      <HeaderPageActions />
      <ModuleNavigation class="ref-header__navigation" />
      <GlobalSearch class="ref-header__search" />
      <div class="ref-header__actions">
        <QuickCreateMenu />
        <RouterLink
          class="ref-header-utility"
          to="/feature-unavailable?feature=Notifications"
          aria-label="Notifications"
          title="Notifications"
        >
          <SmjNotification size="19" decorative />
        </RouterLink>
        <RouterLink
          class="ref-header-utility"
          to="/feature-unavailable?feature=Messages"
          aria-label="Messages"
          title="Messages"
        >
          <SmjMessage size="19" decorative />
        </RouterLink>
        <UserMenu />
      </div>
    </div>
  </header>
</template>
