<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

import AppBreadcrumbs from "@/components/navigation/AppBreadcrumbs.vue";
import ConfirmDialogHost from "@/components/feedback/ConfirmDialogHost.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import LoadingState from "@/components/feedback/LoadingState.vue";
import ToastHost from "@/components/feedback/ToastHost.vue";
import MobileNavigation from "@/components/navigation/MobileNavigation.vue";
import AppHeader from "./AppHeader.vue";

defineProps({ fatalError: { type: Error, default: null } });

const booting = ref(false);
const mobileNavigationOpen = ref(false);

function closeTransientUi() {
  mobileNavigationOpen.value = false;
}

onMounted(() => {
  window.addEventListener("retail-erp:close-transient-ui", closeTransientUi);
});

onBeforeUnmount(() => {
  window.removeEventListener("retail-erp:close-transient-ui", closeTransientUi);
});
</script>

<template>
  <div class="ref-app-shell">
    <AppHeader @toggle-mobile-navigation="mobileNavigationOpen = !mobileNavigationOpen" />
    <MobileNavigation :open="mobileNavigationOpen" @close="mobileNavigationOpen = false" />

    <main class="ref-main" tabindex="-1">
      <AppBreadcrumbs />
      <LoadingState v-if="booting" label="Preparing Retail ERP…" />
      <ErrorState
        v-else-if="fatalError"
        title="Retail ERP could not load"
        :message="fatalError.message"
      />
      <RouterView v-else v-slot="{ Component }">
        <Suspense>
          <component :is="Component" />
          <template #fallback>
            <LoadingState label="Loading module…" />
          </template>
        </Suspense>
      </RouterView>
    </main>

    <ToastHost />
    <ConfirmDialogHost />
  </div>
</template>
