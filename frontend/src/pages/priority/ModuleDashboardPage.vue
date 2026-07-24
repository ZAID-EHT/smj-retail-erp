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
const analyticsCurrency = ref("");
const analyticsCompany = ref("");
const analyticsLoading = ref(false);
const analyticsError = ref("");
const analyticsRefreshedAt = ref("");
let controller;
let analyticsController;

const MODULE_PRESENTATIONS = {
  sales: {
    eyebrow: "Sales command centre",
    title: "Sell, fulfil and collect",
    description: "Track demand, order fulfilment, customer value and the work still waiting to be delivered or billed.",
    sectionTitle: "Sales performance",
    sectionDescription: "Order movement and fulfilment status for the current company.",
    actionTitle: "Start a sales workflow",
    cardOrder: ["annual-sales", "sales-orders-to-deliver", "sales-orders-to-bill", "average-sales-order-value", "active-customers", "sales-orders-count", "total-sales-amount"],
    focusCharts: ["sales-order-trends", "sales-order-analysis"],
    chartSubtitles: {
      "sales-order-trends": "Order value · last 6 months",
      "sales-order-analysis": "Submitted orders by current status",
      "top-customers": "Ranked by invoiced value",
      "item-wise-annual-sales": "Top items by net sales value",
    },
  },
  purchases: {
    eyebrow: "Purchasing control",
    title: "Source, receive and pay",
    description: "See supplier concentration, purchase demand and orders that still require receipt or billing.",
    sectionTitle: "Procurement movement",
    sectionDescription: "Purchase order value and current order pipeline.",
    actionTitle: "Start a purchasing workflow",
    cardOrder: ["annual-purchase", "purchase-orders-to-receive", "purchase-orders-to-bill", "average-order-values", "active-suppliers", "purchase-orders-count", "total-purchase-amount"],
    focusCharts: ["purchase-order-trends", "purchase-order-analysis"],
    chartSubtitles: {
      "purchase-order-trends": "Order value · last 6 months",
      "purchase-order-analysis": "Submitted orders by current status",
      "top-suppliers": "Ranked by invoiced purchase value",
      "material-request-analysis": "Submitted requests by status",
    },
  },
  finance: {
    eyebrow: "Finance control room",
    title: "Cash, exposure and profitability",
    description: "Monitor payments, invoice movement, ageing exposure, bank balances and operating result from ERPNext-maintained values.",
    sectionTitle: "Financial movement",
    sectionDescription: "Billing trends and the ageing position that needs attention.",
    actionTitle: "Record or review finance activity",
    cardOrder: ["outstanding-receivables", "overdue-receivables", "outstanding-payables", "total-incoming-payment", "total-outgoing-payment", "total-outgoing-bills", "total-incoming-bills"],
    focusCharts: ["outgoing-bills-sales-invoice", "accounts-receivable-ageing"],
    chartSubtitles: {
      "outgoing-bills-sales-invoice": "Sales invoice value · last 6 months",
      "incoming-bills-purchase-invoice": "Purchase invoice value · last 6 months",
      "accounts-receivable-ageing": "Outstanding customer invoices by age",
      "accounts-payable-ageing": "Outstanding supplier invoices by age",
      "profit-and-loss": "Income and expense for the selected period",
      "bank-balance": "ERPNext account balances by company bank account",
      "budget-variance": "Current fiscal-year variance",
    },
  },
  crm: {
    eyebrow: "CRM pipeline",
    title: "Convert attention into revenue",
    description: "Follow lead flow, open opportunity value, campaign contribution and territory performance.",
    sectionTitle: "Pipeline movement",
    sectionDescription: "Opportunity value and lead acquisition over the last 6 months.",
    actionTitle: "Grow the pipeline",
    cardOrder: ["open-pipeline-value", "open-opportunity", "new-lead-last-1-month", "new-opportunity-last-1-month", "won-opportunity-last-1-month"],
    focusCharts: ["opportunity-trends", "lead-source"],
    chartSubtitles: {
      "opportunity-trends": "Opportunity value · last 6 months",
      "incoming-leads": "New leads · last 6 months",
      "lead-source": "Lead volume by acquisition source",
      "won-opportunities": "Converted opportunities · last 6 months",
      "opportunities-via-campaigns": "Opportunity count by campaign",
      "territory-wise-opportunity-count": "Open pipeline distribution",
      "territory-wise-sales": "Invoiced value by territory",
    },
  },
  operations: {
    eyebrow: "Operations workspace",
    title: "Deliver work without losing the details",
    description: "Bring projects, tasks, support, assets and production workload into one actionable operational view.",
    sectionTitle: "Work in progress",
    sectionDescription: "Task creation and project portfolio status across permitted records.",
    actionTitle: "Create operational work",
    cardOrder: ["overdue-tasks", "open-tasks", "open-projects", "open-issues", "active-work-orders", "active-assets"],
    focusCharts: ["tasks-created-trend", "project-status"],
    chartSubtitles: {
      "tasks-created-trend": "New tasks · last 6 months",
      "project-status": "Current project portfolio",
      "task-status": "Tasks grouped by current status",
      "issue-priority": "Open and historical issues by priority",
      "work-order-status": "Submitted production work orders",
      "asset-status": "Submitted assets by status",
    },
  },
  admin: {
    eyebrow: "Administration overview",
    title: "Access, setup and system signals",
    description: "Review user access, organisational setup and safe operational health indicators without exposing secrets.",
    sectionTitle: "Access and health",
    sectionDescription: "User growth and recent system error activity.",
    actionTitle: "Manage configuration",
    cardOrder: ["recent-errors", "enabled-users", "disabled-users", "roles", "companies", "active-warehouses"],
    focusCharts: ["user-growth", "error-activity"],
    chartSubtitles: {
      "user-growth": "New user accounts · last 6 months",
      "error-activity": "Error Log records · last 7 days",
      "user-types": "Enabled accounts by user type",
      "role-assignment": "Most commonly assigned roles",
      "scheduler-status": "Enabled and stopped scheduled jobs",
    },
  },
  inventory: {
    eyebrow: "Inventory overview",
    title: "Know what is available and where",
    description: "Monitor stock value, shortages, warehouse concentration and physical movement.",
    sectionTitle: "Stock movement",
    sectionDescription: "Delivery and receipt activity across the last 6 months.",
    actionTitle: "Move or maintain stock",
    cardOrder: ["total-stock-value", "total-active-items", "total-warehouses"],
    focusCharts: ["delivery-trends", "item-shortage-summary"],
    chartSubtitles: {},
  },
};

const DEFAULT_PRESENTATION = {
  eyebrow: "Module dashboard",
  title: "Work overview",
  description: "Your permitted records, actions and recent activity.",
  sectionTitle: "Performance overview",
  sectionDescription: "Live, permission-aware ERPNext information.",
  actionTitle: "Quick actions",
  cardOrder: [], focusCharts: [], chartSubtitles: {},
};

const CURRENCY_CARD_KEYS = new Set([
  "annual-sales", "average-sales-order-value", "total-sales-amount",
  "annual-purchase", "average-order-values", "total-purchase-amount",
  "total-incoming-payment", "total-outgoing-payment", "total-stock-value",
  "outstanding-receivables", "overdue-receivables", "outstanding-payables", "open-pipeline-value",
]);

const presentation = computed(() => MODULE_PRESENTATIONS[route.name] || DEFAULT_PRESENTATION);

const orderedCards = computed(() => {
  const rank = new Map(presentation.value.cardOrder.map((key, index) => [key, index]));
  return [...analytics.value.cards].sort((a, b) => (rank.get(a.key) ?? 999) - (rank.get(b.key) ?? 999));
});

const focusCharts = computed(() => presentation.value.focusCharts
  .map((key) => analytics.value.charts.find((chart) => chart.key === key))
  .filter(Boolean));

const supportingCharts = computed(() => {
  const featured = new Set(presentation.value.focusCharts);
  return analytics.value.charts.filter((chart) => !featured.has(chart.key));
});

function money(value) {
  return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
}

function cardValue(card) {
  const value = typeof card.value === "number" ? money(card.value) : String(card.value);
  return CURRENCY_CARD_KEYS.has(card.key) && analyticsCurrency.value ? `${analyticsCurrency.value} ${value}` : value;
}

function chartSubtitle(chart) {
  return chart.subtitle || presentation.value.chartSubtitles?.[chart.key] || "";
}

function chartHasData(chart) {
  return Boolean(chart.bars?.length || chart.segments?.length || chart.series?.some((series) => series.values?.some((value) => Number(value) !== 0)));
}

async function load() {
  controller?.abort(); controller = new AbortController(); error.value = null; dashboard.value = null;
  try { dashboard.value = await getModuleDashboard(String(route.name || "home"), controller.signal); }
  catch (caught) { if (caught.name !== "AbortError") error.value = caught; }
}

async function loadAnalytics() {
  const loaders = MODULE_DASHBOARD_LOADERS[route.name];
  if (!loaders) {
    analytics.value = { cards: [], charts: [] };
    analyticsCurrency.value = "";
    analyticsCompany.value = "";
    return;
  }
  analyticsController?.abort(); analyticsController = new AbortController();
  analyticsLoading.value = true; analyticsError.value = "";
  try {
    const results = await Promise.all(loaders.map((loader) => loader(analyticsController.signal)));
    analytics.value = {
      cards: results.flatMap((result) => result?.cards || []),
      charts: results.flatMap((result) => result?.charts || []),
    };
    analyticsCurrency.value = results.find((result) => result?.currency)?.currency || "";
    analyticsCompany.value = results.find((result) => result?.company)?.company || "";
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
    <main v-else-if="dashboard" class="rug-page module-dashboard" :data-module="dashboard.module">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span><strong>{{ dashboard.label }}</strong>
      </nav>

      <header class="module-dashboard__hero" :data-accent="dashboard.accent">
        <div class="module-dashboard__hero-copy">
          <span class="module-dashboard__eyebrow">{{ presentation.eyebrow }}</span>
          <h1>{{ presentation.title }}</h1>
          <p>{{ presentation.description }}</p>
          <div class="module-dashboard__source">
            <span>Live ERPNext data</span>
            <span v-if="analyticsCompany">{{ analyticsCompany }}</span>
            <span v-if="analyticsRefreshedAt">Updated {{ analyticsRefreshedAt }}</span>
          </div>
        </div>
        <div v-if="dashboard.quick_actions.length" class="module-dashboard__hero-actions">
          <RouterLink
            v-for="(action, index) in dashboard.quick_actions.slice(0, 3)"
            :key="action.path"
            :class="index === 0 ? 'rug-primary' : 'rug-secondary'"
            class="priority-button-link"
            :to="action.path"
          >{{ action.label }}</RouterLink>
        </div>
      </header>

      <p v-if="analyticsError" class="rug-inline-error" role="alert">{{ analyticsError }}</p>

      <section v-if="analyticsLoading && !orderedCards.length" class="module-dashboard__kpi-skeleton" aria-label="Loading module summary">
        <i v-for="n in 5" :key="n" />
      </section>
      <section v-else-if="orderedCards.length" class="module-dashboard__kpis" aria-label="Module summary">
        <SmjKpiCard
          v-for="card in orderedCards"
          :key="card.key"
          :label="card.label"
          :value="cardValue(card)"
          :accent="card.accent"
          :to="card.to"
        />
      </section>
      <section v-else-if="dashboard.metrics.length" class="rug-summary-grid">
        <RouterLink v-for="metric in dashboard.metrics" :key="metric.path" :to="metric.path" class="priority-metric">
          <span>{{ metric.label }}</span><strong>{{ metric.value }}</strong><small>Permitted records</small>
        </RouterLink>
      </section>

      <template v-if="hasAnalytics">
        <div class="module-dashboard__section-heading">
          <div><span>01</span><h2>{{ presentation.sectionTitle }}</h2><p>{{ presentation.sectionDescription }}</p></div>
          <button type="button" @click="loadAnalytics">Refresh data</button>
        </div>
        <section v-if="analyticsLoading && !focusCharts.length" class="module-dashboard__focus-grid" aria-label="Loading dashboard charts">
          <div v-for="n in 2" :key="n" class="module-dashboard__chart-skeleton"><i /><i /><i /></div>
        </section>
        <section v-else-if="focusCharts.length" class="module-dashboard__focus-grid">
          <SmjChartCard
            v-for="(chart, index) in focusCharts"
            :key="chart.key"
            :class="{ 'is-primary': index === 0 }"
            :title="chart.title"
            :subtitle="chartSubtitle(chart)"
            :loading="analyticsLoading"
            :empty="!analyticsLoading && !chartHasData(chart)"
            :report-link="chart.report_link"
            :last-refreshed="analyticsRefreshedAt"
            @refresh="loadAnalytics"
          >
            <SmjBarChart v-if="chart.type === 'bar' && chart.bars?.length" :bars="chart.bars" :value-formatter="money" />
            <SmjDonutChart v-else-if="chart.type === 'donut' && chart.segments?.length" :segments="chartSegments(chart)" :value-formatter="money" />
            <SmjLineChart v-else-if="chart.type === 'line' && chart.series" :labels="chart.labels" :series="chart.series" :value-formatter="money" />
          </SmjChartCard>
        </section>

        <section v-if="supportingCharts.length" class="module-dashboard__supporting-grid" aria-label="Supporting analysis">
          <SmjChartCard
            v-for="chart in supportingCharts"
            :key="chart.key"
            :title="chart.title"
            :subtitle="chartSubtitle(chart)"
            :empty="!chartHasData(chart)"
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

      <section v-if="dashboard.quick_actions.length" class="rug-section-card module-dashboard__actions">
        <header><div><h2>{{ presentation.actionTitle }}</h2><p>Actions are shown only when your ERPNext permissions allow creation.</p></div></header>
        <div class="priority-link-grid">
          <RouterLink v-for="action in dashboard.quick_actions" :key="action.path" :to="action.path">
            <span>＋</span><strong>{{ action.label }}</strong><small>Open form</small>
          </RouterLink>
        </div>
      </section>

      <div class="module-dashboard__activity-grid">
        <section class="rug-section-card">
          <header><div><h2>Important pages</h2><p>Direct access to your permitted {{ dashboard.label.toLowerCase() }} work.</p></div></header>
          <div class="priority-link-grid">
            <RouterLink v-for="link in dashboard.links" :key="link.path" :to="link.path">
              <span><SmjChevronDown size="16" style="transform:rotate(-90deg)" decorative /></span><strong>{{ link.label }}</strong><small>Open page</small>
            </RouterLink>
          </div>
        </section>
        <section class="rug-section-card module-dashboard__recent">
          <header><div><h2>Recent activity</h2><p>Recently modified records you are allowed to read.</p></div><button type="button" @click="load">Refresh</button></header>
          <div v-if="!dashboard.recent.length" class="rug-muted">No recent permitted records.</div>
          <RouterLink v-for="record in dashboard.recent" :key="`${record.doctype}-${record.name}`" :to="record.path" class="rug-related">
            <span>{{ record.doctype }}<small>{{ record.modified }}</small></span><strong>{{ record.title }}</strong>
          </RouterLink>
        </section>
      </div>

      <section v-if="dashboard.reports.length" class="rug-section-card module-dashboard__reports">
        <header><div><h2>Module reports</h2><p>Run the permitted ERPNext reports relevant to this workspace.</p></div></header>
        <div class="priority-link-grid">
          <RouterLink v-for="report in dashboard.reports" :key="report.path" :to="report.path">
            <span><SmjReportsBarsSpark size="16" decorative /></span><strong>{{ report.label }}</strong><small>Run report</small>
          </RouterLink>
        </div>
      </section>
    </main>
    <div v-else class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
  </PageContainer>
</template>
