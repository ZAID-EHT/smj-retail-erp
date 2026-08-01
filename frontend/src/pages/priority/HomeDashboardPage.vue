<script setup>
import { computed, inject, onBeforeUnmount, ref } from "vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { SmjCreditGauge, SmjDeliveryTruckArrow, SmjFinanceWalletLedger, SmjInventoryCubeLayers, SmjLowStockAlert, SmjPaymentWalletCheck, SmjReserveCubeLock, SmjSalesCartPulse } from "@/components/icons";
import { SmjBarChart, SmjChartCard, SmjDonutChart, SmjKpiCard, SmjLineChart } from "@/components/charts";
import {
  getHomeKpis, getLowStockAlerts, getPaymentCollection, getRecentTransactions,
  getSalesTrend, getStockOverview, getTopCategories, getTopParties,
} from "@/services/dashboardAnalytics.js";
import { getQuickCreateActions } from "@/services/quickCreate.js";

const session = inject("retailSession", null);
const company = computed(() => session?.state?.company || "");
const today = computed(() =>
  new Intl.DateTimeFormat(undefined, { dateStyle: "full" }).format(new Date()),
);

// Header shortcuts follow the same permission source as the rest of the shell:
// an action the user cannot perform is not offered. The server re-checks anyway.
const quickCreate = ref([]);
const shortcuts = computed(() => {
  const doctypes = new Set(quickCreate.value.flatMap((g) => g.items.map((i) => i.doctype)));
  return {
    sales: doctypes.has("Sales Order"),
    purchaseOrder: doctypes.has("Purchase Order"),
    payment: doctypes.has("Payment Entry"),
  };
});

const KPI_ICON = { total_sales: SmjSalesCartPulse, receivables: SmjCreditGauge, gross_profit: SmjFinanceWalletLedger, reserved_stock: SmjReserveCubeLock, available_to_sell: SmjInventoryCubeLayers, pending_deliveries: SmjDeliveryTruckArrow };
const KPI_ACCENT = { total_sales: "green", receivables: "orange", gross_profit: "gold", reserved_stock: "purple", available_to_sell: "turquoise", pending_deliveries: "pink" };

const loading = ref({ kpis: true, trend: true, collection: true, categories: true, transactions: true, stock: true, lowStock: true, customers: true, products: true });
const errors = ref({});
const kpis = ref(null);
const trend = ref(null);
const collection = ref(null);
const categories = ref(null);
const transactions = ref(null);
const stock = ref(null);
const lowStock = ref(null);
const topCustomers = ref(null);
const topProducts = ref(null);
const currency = computed(() => kpis.value?.currency || "");

function money(value) {
  const formatted = new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(Number(value || 0));
  return currency.value ? `${currency.value} ${formatted}` : formatted;
}

const controllers = [];
function tracked(promise, key, target) {
  loading.value[key] = true;
  errors.value[key] = "";
  promise
    .then((result) => { target.value = result; })
    .catch((error) => { if (error.name !== "AbortError") errors.value[key] = error.message; })
    .finally(() => { loading.value[key] = false; });
}

function loadAll() {
  controllers.forEach((controller) => controller.abort());
  controllers.length = 0;
  const make = () => { const c = new AbortController(); controllers.push(c); return c.signal; };
  tracked(getHomeKpis(make()), "kpis", kpis);
  tracked(getSalesTrend(6, make()), "trend", trend);
  tracked(getPaymentCollection(make()), "collection", collection);
  tracked(getTopCategories(6, make()), "categories", categories);
  tracked(getRecentTransactions(6, make()), "transactions", transactions);
  tracked(getStockOverview(make()), "stock", stock);
  tracked(getLowStockAlerts(6, make()), "lowStock", lowStock);
  tracked(getTopParties("customers", 5, make()), "customers", topCustomers);
  tracked(getTopParties("products", 5, make()), "products", topProducts);
  getQuickCreateActions(make())
    .then((groups) => { quickCreate.value = groups || []; })
    .catch(() => { quickCreate.value = []; });
}
loadAll();
onBeforeUnmount(() => controllers.forEach((controller) => controller.abort()));

const CATEGORY_COLORS = ["var(--ref-primary-blue)", "var(--ref-green)", "var(--ref-orange)", "var(--ref-purple)", "var(--ref-turquoise)", "var(--ref-pink)"];
const categoryBars = computed(() => (categories.value?.categories || []).map((entry, index) => ({ label: entry.label, value: entry.value, color: CATEGORY_COLORS[index % CATEGORY_COLORS.length] })));

const collectionSegments = computed(() => collection.value ? [
  { label: "Collected", value: collection.value.collected, color: "var(--ref-success)" },
  { label: "Pending", value: collection.value.pending, color: "var(--ref-warning)" },
  { label: "Overdue", value: collection.value.overdue, color: "var(--ref-danger)" },
] : []);
const collectionPercent = computed(() => collection.value?.total ? Math.round((collection.value.collected / collection.value.total) * 100) : 0);
</script>

<template>
  <PageContainer>
    <main class="rug-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/home">Home</RouterLink><span>›</span><strong>Home</strong></nav>

      <header class="smj-home-hero">
        <div>
          <h1>{{ company || "Retail ERP" }}</h1>
          <p>{{ today }}</p>
        </div>
        <div class="smj-home-hero__actions">
          <RouterLink v-if="shortcuts.sales" class="ref-button ref-button--primary" to="/smart-sales">Sales</RouterLink>
          <RouterLink v-if="shortcuts.purchaseOrder" class="ref-button ref-button--secondary" to="/purchases/orders/new">+ Purchase Order</RouterLink>
          <RouterLink v-if="shortcuts.payment" class="ref-button ref-button--secondary" to="/finance/payments/new">+ Payment</RouterLink>
        </div>
      </header>

      <p v-if="errors.kpis" class="rug-inline-error">{{ errors.kpis }}</p>
      <section class="smj-home-kpis">
        <div v-if="loading.kpis" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>
        <template v-else>
          <SmjKpiCard
            v-for="kpi in kpis?.kpis || []"
            :key="kpi.key"
            :label="kpi.label"
            :value="money(kpi.value)"
            :icon="KPI_ICON[kpi.key]"
            :accent="KPI_ACCENT[kpi.key]"
            :trend="kpi.trend"
            :spark="kpi.spark"
            :to="kpi.path"
          />
        </template>
      </section>

      <section class="smj-home-charts">
        <SmjChartCard title="Sales Trend" subtitle="last 6 months" :loading="loading.trend" :error="errors.trend" :empty="!trend?.series?.some((s) => s.values.some((v) => v))" report-link="/reports/view/Sales%20Register" @refresh="loadAll">
          <SmjLineChart
            v-if="trend"
            :labels="trend.labels"
            :series="trend.series.map((s, i) => ({ ...s, color: i === 0 ? 'var(--ref-primary-blue)' : 'var(--ref-border-colour)' }))"
            :value-formatter="money"
          />
        </SmjChartCard>
        <SmjChartCard title="Payment Collection" :loading="loading.collection" :error="errors.collection" :empty="!collection?.total" @refresh="loadAll">
          <SmjDonutChart v-if="collection" :segments="collectionSegments" :center-value="`${collectionPercent}%`" center-label="Collected" :value-formatter="money" />
        </SmjChartCard>
        <SmjChartCard title="Top Selling Categories" :loading="loading.categories" :error="errors.categories" :empty="!categoryBars.length" @refresh="loadAll">
          <SmjBarChart v-if="categoryBars.length" :bars="categoryBars" :value-formatter="money" />
        </SmjChartCard>
      </section>

      <section class="smj-home-lower">
        <div class="rug-section-card smj-home-transactions">
          <header><div><h2>Recent Transactions</h2></div></header>
          <div v-if="loading.transactions" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>
          <p v-else-if="errors.transactions" class="rug-inline-error">{{ errors.transactions }}</p>
          <p v-else-if="!transactions?.items?.length" class="rug-muted">No recent transactions yet.</p>
          <table v-else class="ref-data-table">
            <thead><tr><th>Type</th><th>Party</th><th>Status</th><th>Amount</th></tr></thead>
            <tbody>
              <tr v-for="row in transactions.items" :key="`${row.doctype}-${row.name}`" tabindex="0" @click="$router.push(row.path)">
                <td><code>{{ row.name }}</code></td>
                <td>{{ row.party }}</td>
                <td><span class="ref-status-badge">{{ row.status }}</span></td>
                <td>{{ money(row.amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="rug-section-card">
          <header><div><h2>Stock Overview</h2></div></header>
          <div v-if="loading.stock" class="rug-skeleton"><i v-for="n in 3" :key="n" /></div>
          <p v-else-if="errors.stock" class="rug-inline-error">{{ errors.stock }}</p>
          <template v-else-if="stock">
            <div class="smj-stock-row"><SmjInventoryCubeLayers size="16" decorative /><span>Actual Stock</span><b>{{ money(stock.actual) }}</b></div>
            <div class="smj-stock-row"><SmjReserveCubeLock size="16" decorative /><span>Reserved Stock</span><b>{{ money(stock.reserved) }}</b></div>
            <div class="smj-stock-row"><SmjPaymentWalletCheck size="16" decorative /><span>Available-to-Sell</span><b>{{ money(stock.available) }}</b></div>
            <p class="rug-muted">{{ stock.total_items }} items · {{ stock.warehouses }} warehouses</p>
          </template>
        </div>

        <div class="rug-section-card">
          <header><div><h2>Low Stock Alerts</h2></div></header>
          <div v-if="loading.lowStock" class="rug-skeleton"><i v-for="n in 3" :key="n" /></div>
          <p v-else-if="!lowStock?.items?.length" class="rug-muted">Nothing is low on stock right now.</p>
          <ul v-else class="smj-alert-list">
            <li v-for="item in lowStock.items" :key="item.item_code">
              <SmjLowStockAlert size="14" decorative />
              <RouterLink :to="item.path">{{ item.item_name }}</RouterLink>
              <small>{{ item.warehouse }} · {{ item.available }} left</small>
            </li>
          </ul>
        </div>
      </section>

      <section class="smj-home-lower smj-home-lower--two">
        <div class="rug-section-card">
          <header><div><h2>Top Customers</h2></div></header>
          <div v-if="loading.customers" class="rug-skeleton"><i v-for="n in 3" :key="n" /></div>
          <p v-else-if="!topCustomers?.items?.length" class="rug-muted">No customer sales yet.</p>
          <ol v-else class="smj-rank-list">
            <li v-for="(item, index) in topCustomers.items" :key="item.label"><span>{{ index + 1 }}</span><RouterLink :to="item.path">{{ item.label }}</RouterLink><b>{{ money(item.value) }}</b></li>
          </ol>
        </div>
        <div class="rug-section-card">
          <header><div><h2>Top Products</h2></div></header>
          <div v-if="loading.products" class="rug-skeleton"><i v-for="n in 3" :key="n" /></div>
          <p v-else-if="!topProducts?.items?.length" class="rug-muted">No product sales yet.</p>
          <ol v-else class="smj-rank-list">
            <li v-for="(item, index) in topProducts.items" :key="item.label"><span>{{ index + 1 }}</span><RouterLink :to="item.path">{{ item.label }}</RouterLink><b>{{ money(item.value) }}</b></li>
          </ol>
        </div>
      </section>
    </main>
  </PageContainer>
</template>
