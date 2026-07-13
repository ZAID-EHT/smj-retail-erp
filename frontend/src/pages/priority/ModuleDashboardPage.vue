<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import { useRoute } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getModuleDashboard } from "@/services/priority.js";

const route = useRoute();
const dashboard = ref(null);
const error = ref(null);
let controller;

async function load() {
  controller?.abort(); controller = new AbortController(); error.value = null; dashboard.value = null;
  try { dashboard.value = await getModuleDashboard(String(route.name || "home"), controller.signal); }
  catch (caught) { if (caught.name !== "AbortError") error.value = caught; }
}
watch(() => route.name, load, { immediate: true });
onBeforeUnmount(() => controller?.abort());
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="error?.permissionDenied" />
    <ErrorState v-else-if="error" title="Unable to load dashboard" :message="error.message" @retry="load" />
    <main v-else-if="dashboard" class="rug-page priority-dashboard">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/home">Home</RouterLink><span>›</span><strong>{{ dashboard.label }}</strong></nav>
      <header :class="['rug-banner', `rug-banner--${dashboard.accent}`]"><div><span class="rug-badge">Module dashboard</span><h1>{{ dashboard.label }}</h1><p>{{ dashboard.description }}</p></div><div class="rug-banner-actions"><RouterLink v-for="action in dashboard.quick_actions.slice(0, 2)" :key="action.path" class="rug-primary priority-button-link" :to="action.path">{{ action.label }}</RouterLink></div></header>
      <section v-if="dashboard.metrics.length" class="rug-summary-grid"><RouterLink v-for="metric in dashboard.metrics" :key="metric.path" :to="metric.path" class="priority-metric"><span>{{ metric.label }}</span><strong>{{ metric.value }}</strong><small>Permitted records</small></RouterLink></section>
      <section v-if="dashboard.quick_actions.length" class="rug-section-card"><header><div><h2>Quick actions</h2><p>Create records using your current ERPNext permissions.</p></div></header><div class="priority-link-grid"><RouterLink v-for="action in dashboard.quick_actions" :key="action.path" :to="action.path"><span>＋</span><strong>{{ action.label }}</strong><small>Open form</small></RouterLink></div></section>
      <div class="priority-dashboard-grid">
        <section class="rug-section-card"><header><div><h2>Important pages</h2><p>Only pages permitted for your account are shown.</p></div></header><div class="priority-link-grid"><RouterLink v-for="link in dashboard.links" :key="link.path" :to="link.path"><span>◆</span><strong>{{ link.label }}</strong><small>Open page</small></RouterLink></div></section>
        <section class="rug-section-card"><header><div><h2>Recent activity</h2><p>Your most recently modified permitted records.</p></div><button type="button" @click="load">Refresh</button></header><div v-if="!dashboard.recent.length" class="rug-muted">No recent permitted records.</div><RouterLink v-for="record in dashboard.recent" :key="`${record.doctype}-${record.name}`" :to="record.path" class="rug-related"><span>{{ record.doctype }}<small>{{ record.modified }}</small></span><strong>{{ record.title }}</strong></RouterLink></section>
      </div>
      <section v-if="dashboard.reports.length" class="rug-section-card"><header><h2>Reports</h2></header><div class="priority-link-grid"><RouterLink v-for="report in dashboard.reports" :key="report.path" :to="report.path"><span>◇</span><strong>{{ report.label }}</strong><small>Run report</small></RouterLink></div></section>
    </main>
    <div v-else class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
  </PageContainer>
</template>
