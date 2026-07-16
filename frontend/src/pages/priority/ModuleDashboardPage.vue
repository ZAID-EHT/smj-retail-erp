<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { SmjBarChart, SmjChartCard, SmjDonutChart, SmjKpiCard, SmjLineChart } from "@/components/charts";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import { SmjChevronDown, SmjReportsBarsSpark } from "@/components/icons";
import PageContainer from "@/components/layout/PageContainer.vue";
import { MODULE_DASHBOARD_LOADERS } from "@/services/moduleDashboards.js";
import { getModuleDashboard } from "@/services/priority.js";

const route = useRoute();
const dashboard = ref(null);
const error = ref(null);
const analytics = ref({ cards: [], charts: [] });
const analyticsLoading = ref(false);
const analyticsError = ref("");
const analyticsRefreshedAt = ref("");
let controller;
let analyticsController;

function money(value) {
  return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
}

async function load() {
  controller?.abort(); controller = new AbortController(); error.value = null; dashboard.value = null;
  try { dashboard.value = await getModuleDashboard(String(route.name || "home"), controller.signal); }
  catch (caught) { if (caught.name !== "AbortError") error.value = caught; }
}

async function loadAnalytics() {
  const loaders = MODULE_DASHBOARD_LOADERS[route.name];
  if (!loaders) { analytics.value = { cards: [], charts: [] }; return; }
  analyticsController?.abort(); analyticsController = new AbortController();
  analyticsLoading.value = true; analyticsError.value = "";
  try {
    const results = await Promise.all(loaders.map((loader) => loader(analyticsController.signal)));
    analytics.value = {
      cards: results.flatMap((result) => result?.cards || []),
      charts: results.flatMap((result) => result?.charts || []),
    };
    analyticsRefreshedAt.value = new Date().toLocaleTimeString();
  } catch (caught) {
    if (caught.name !== "AbortError") analyticsError.value = caught.message || "Analytics are temporarily unavailable.";
  } finally {
    analyticsLoading.value = false;
  }
}

function chartSegments(chart) {
  const colors = ["var(--ref-primary-blue)", "var(--ref-success)", "var(--ref-warning)", "#7038d4", "var(--ref-danger)"];
  return (chart.segments || []).map((segment, index) => ({ ...segment, color: segment.color || colors[index % colors.length] }));
}

const hasAnalytics = computed(() => Boolean(MODULE_DASHBOARD_LOADERS[route.name]));

watch(() => route.name, () => { load(); loadAnalytics(); }, { immediate: true });
onBeforeUnmount(() => { controller?.abort(); analyticsController?.abort(); });
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

      <template v-if="hasAnalytics">
        <p v-if="analyticsError" class="rug-inline-error" role="alert">{{ analyticsError }}</p>
        <section v-if="analytics.cards.length || analyticsLoading" class="smj-sales-kpis" aria-label="Module analytics summary">
          <SmjKpiCard
            v-for="card in analytics.cards"
            :key="card.key"
            :label="card.label"
            :value="typeof card.value === 'number' ? money(card.value) : String(card.value)"
            :accent="card.accent"
            :to="card.to"
          />
        </section>
        <section v-if="analytics.charts.length || analyticsLoading" class="priority-dashboard-grid">
          <SmjChartCard
            v-for="chart in analytics.charts"
            :key="chart.key"
            :title="chart.title"
            :loading="analyticsLoading"
            :empty="!analyticsLoading && !(chart.bars?.length || chart.segments?.length || chart.series?.some((s) => s.values.some((v) => v)))"
            :report-link="chart.report_link"
            :last-refreshed="analyticsRefreshedAt"
            @refresh="loadAnalytics"
          >
            <SmjBarChart v-if="chart.type === 'bar' && chart.bars?.length" :bars="chart.bars" :value-formatter="money" />
            <SmjDonutChart v-else-if="chart.type === 'donut' && chart.segments?.length" :segments="chartSegments(chart)" :value-formatter="money" />
            <SmjLineChart v-else-if="chart.type === 'line' && chart.series" :labels="chart.labels" :series="chart.series" :value-formatter="money" />
          </SmjChartCard>
        </section>
      </template>

      <div class="priority-dashboard-grid">
        <section class="rug-section-card"><header><div><h2>Important pages</h2><p>Only pages permitted for your account are shown.</p></div></header><div class="priority-link-grid"><RouterLink v-for="link in dashboard.links" :key="link.path" :to="link.path"><span><SmjChevronDown size="16" style="transform:rotate(-90deg)" decorative /></span><strong>{{ link.label }}</strong><small>Open page</small></RouterLink></div></section>
        <section class="rug-section-card"><header><div><h2>Recent activity</h2><p>Your most recently modified permitted records.</p></div><button type="button" @click="load">Refresh</button></header><div v-if="!dashboard.recent.length" class="rug-muted">No recent permitted records.</div><RouterLink v-for="record in dashboard.recent" :key="`${record.doctype}-${record.name}`" :to="record.path" class="rug-related"><span>{{ record.doctype }}<small>{{ record.modified }}</small></span><strong>{{ record.title }}</strong></RouterLink></section>
      </div>
      <section v-if="dashboard.reports.length" class="rug-section-card"><header><h2>Reports</h2></header><div class="priority-link-grid"><RouterLink v-for="report in dashboard.reports" :key="report.path" :to="report.path"><span><SmjReportsBarsSpark size="16" decorative /></span><strong>{{ report.label }}</strong><small>Run report</small></RouterLink></div></section>
    </main>
    <div v-else class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
  </PageContainer>
</template>
