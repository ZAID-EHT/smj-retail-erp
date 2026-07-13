<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import UniversalDetailPage from "@/pages/generated/UniversalDetailPage.vue";
import UniversalFormPage from "@/pages/generated/UniversalFormPage.vue";
import UniversalListPage from "@/pages/generated/UniversalListPage.vue";
import PriorityReportPage from "@/pages/priority/PriorityReportPage.vue";
import PriorityReportHubPage from "@/pages/priority/PriorityReportHubPage.vue";
import PrioritySpecialPage from "@/pages/priority/PrioritySpecialPage.vue";
import PriorityTreePage from "@/pages/priority/PriorityTreePage.vue";
import { getPriorityRouteDefinition } from "@/services/priority.js";

const route = useRoute();
const router = useRouter();
const definition = ref(null);
const error = ref(null);
let controller;
const recordName = computed(() => definition.value?.params?.name || "");

async function load() {
  controller?.abort();
  controller = new AbortController();
  definition.value = null;
  error.value = null;
  try {
    const result = await getPriorityRouteDefinition(route.path, controller.signal);
    if (result.redirect) {
      await router.replace(result.redirect);
      return;
    }
    definition.value = result;
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  }
}

watch(() => route.fullPath, load, { immediate: true });
onBeforeUnmount(() => controller?.abort());
</script>

<template>
  <PermissionDenied v-if="error?.permissionDenied" />
  <PageContainer v-else-if="error"><ErrorState title="Unable to load page" :message="error.message" @retry="load" /></PageContainer>
  <UniversalListPage v-else-if="definition?.component === 'entity' && definition.mode === 'list'" :feature-key="definition.feature" :base-path="definition.base_path" />
  <UniversalFormPage v-else-if="definition?.component === 'entity' && ['new', 'edit'].includes(definition.mode)" :feature-key="definition.feature" :base-path="definition.base_path" :record-name="recordName" :defaults="definition.defaults" />
  <UniversalDetailPage v-else-if="definition?.component === 'entity' && definition.mode === 'detail'" :feature-key="definition.feature" :base-path="definition.base_path" :record-name="recordName" />
  <PriorityTreePage v-else-if="definition?.component === 'tree'" :definition="definition" />
  <PriorityReportHubPage v-else-if="definition?.component === 'report_hub'" :group="definition.group" />
  <PriorityReportPage v-else-if="definition?.component === 'report'" :report-name="definition.report" />
  <PrioritySpecialPage v-else-if="definition?.component === 'special'" :definition="definition" />
  <PageContainer v-else><div class="rug-skeleton"><i v-for="n in 8" :key="n" /></div></PageContainer>
</template>
