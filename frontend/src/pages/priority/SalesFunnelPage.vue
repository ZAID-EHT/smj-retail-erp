<script setup>
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { SmjBarChart, SmjChartCard, SmjKpiCard } from "@/components/charts";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getSalesFunnel, searchAnalyticsLink } from "@/services/analyticsPages.js";

function dateString(date) {
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 10);
}
const today = new Date();
const monthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
const filters = reactive({ company: "", from_date: dateString(monthAgo), to_date: dateString(today) });
const companies = ref([]);
const data = ref(null);
const loading = ref(false);
const error = ref(null);
let controller;
let searchTimer;

const funnelCards = computed(() => (data.value?.funnel || []).map((item, index) => ({ ...item, key: item.label, accent: ["red", "orange", "blue", "green"][index] })));
const pipelineBars = computed(() => (data.value?.pipeline || []).map((item) => ({ ...item, color: "var(--ref-primary-blue)" })));
const sourceBars = computed(() => (data.value?.by_source || []).map((item) => ({ ...item, color: "var(--ref-module-crm)" })));
function formatAmount(value) { return `${data.value?.currency || ""} ${Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`.trim(); }

async function searchCompanies() {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(async () => {
    try { companies.value = await searchAnalyticsLink("sales-funnel", "company", filters.company); } catch { companies.value = []; }
  }, 180);
}
async function load() {
  if (!filters.company) { error.value = new Error("Select a permitted company first."); return; }
  controller?.abort(); controller = new AbortController(); loading.value = true; error.value = null;
  try { data.value = await getSalesFunnel({ ...filters }, controller.signal); }
  catch (caught) { if (caught.name !== "AbortError") error.value = caught; }
  finally { loading.value = false; }
}
async function initialise() {
  try {
    companies.value = await searchAnalyticsLink("sales-funnel", "company", "");
    if (!filters.company && companies.value.length) filters.company = companies.value[0].value;
    if (filters.company) await load();
  } catch (caught) { error.value = caught; }
}
onBeforeUnmount(() => { controller?.abort(); window.clearTimeout(searchTimer); });
initialise();
</script>

<template>
  <PageContainer>
    <main class="rug-page sales-funnel-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/sales">Sales</RouterLink><span>›</span><strong>Sales Funnel</strong></nav>
      <header class="rug-banner rug-banner--green"><div><span class="rug-badge">ERPNext sales analytics</span><h1>Sales Funnel</h1><p>Follow permitted leads through opportunities, quotations and customer conversion using live ERPNext records.</p></div><div class="rug-banner-actions"><button class="rug-primary" type="button" :disabled="loading || !filters.company" @click="load">{{ loading ? "Refreshing…" : "Refresh" }}</button></div></header>
      <section class="rug-section-card"><header><div><h2>Analysis period</h2><p>Results respect your Page, DocType, document and User Permissions.</p></div></header><div class="rug-form-grid">
        <label><span>Company <b>*</b></span><input v-model="filters.company" list="sales-funnel-companies" type="search" autocomplete="off" @focus="searchCompanies" @input="searchCompanies" /><datalist id="sales-funnel-companies"><option v-for="item in companies" :key="item.value" :value="item.value" /></datalist></label>
        <label><span>From Date</span><input v-model="filters.from_date" type="date" /></label>
        <label><span>To Date</span><input v-model="filters.to_date" type="date" /></label>
      </div></section>
      <ErrorState v-if="error" title="Unable to load Sales Funnel" :message="error.message" @retry="load" />
      <section v-if="funnelCards.length || loading" class="smj-sales-kpis" aria-label="Sales funnel stages"><SmjKpiCard v-for="card in funnelCards" :key="card.key" :label="card.label" :value="String(card.value)" :accent="card.accent" /></section>
      <div class="priority-dashboard-grid">
        <SmjChartCard title="Sales pipeline by stage" :loading="loading" :empty="!pipelineBars.length"><SmjBarChart v-if="pipelineBars.length" :bars="pipelineBars" :value-formatter="formatAmount" /></SmjChartCard>
        <SmjChartCard title="Opportunities by lead source" :loading="loading" :empty="!sourceBars.length"><SmjBarChart v-if="sourceBars.length" :bars="sourceBars" :value-formatter="formatAmount" /></SmjChartCard>
      </div>
      <p v-if="data?.truncated" class="rug-inline-error">The opportunity analysis reached the safe 5,000-row page limit. Narrow the date range for a complete breakdown.</p>
    </main>
  </PageContainer>
</template>

<style scoped>
.sales-funnel-page label { display:grid; gap:.4rem; color:var(--ref-primary-text); font-weight:700; }
.sales-funnel-page label input { min-height:44px; border:1px solid var(--ref-border-colour); border-radius:.75rem; padding:0 .8rem; background:var(--ref-card-background); color:var(--ref-primary-text); }
</style>
