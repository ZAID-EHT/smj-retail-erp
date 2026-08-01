<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import {
  getWarehouseBatches, getWarehouseMovements, getWarehouseStock,
} from "@/services/managementPages.js";

const route = useRoute();
const warehouse = computed(() => route.query.warehouse || "");

const filters = reactive({
  search: "", item_group: "", stock_status: "all", from_date: "", to_date: "",
});
const tab = ref("items"); // items | batches | movements
const data = ref(null);
const batches = ref(null);
const movements = ref(null);
const loading = ref(false);
const error = ref(null);
const expanded = ref("");
let controller = null;

function load() {
  if (!warehouse.value) return;
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  const signal = controller.signal;
  const params = { warehouse: warehouse.value, ...filters };

  const jobs = [getWarehouseStock(params, signal).then((r) => { data.value = r; })];
  if (tab.value === "batches") {
    jobs.push(getWarehouseBatches({ ...params, item_code: expanded.value }, signal)
      .then((r) => { batches.value = r; }));
  }
  if (tab.value === "movements") {
    jobs.push(getWarehouseMovements({ ...params, item_code: expanded.value }, signal)
      .then((r) => { movements.value = r; }));
  }
  Promise.all(jobs)
    .catch((err) => { if (err.name !== "AbortError") error.value = err; })
    .finally(() => { loading.value = false; });
}
load();
watch(() => route.query.warehouse, load);
watch(tab, load);
onBeforeUnmount(() => controller?.abort());

function openItem(code) {
  expanded.value = expanded.value === code ? "" : code;
  if (tab.value !== "items") load();
}

const totals = computed(() => data.value?.totals || {});
const num = (v) => new Intl.NumberFormat().format(Number(v || 0));
</script>

<template>
  <PageContainer>
    <main class="rug-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span>
        <RouterLink to="/inventory/warehouses">Warehouses</RouterLink><span>›</span>
        <strong>{{ warehouse || "Warehouse" }}</strong>
      </nav>

      <header class="rug-banner rug-banner--green">
        <div>
          <span class="rug-badge">Warehouse stock</span>
          <h1>{{ warehouse || "Select a warehouse" }}</h1>
          <p>Item-wise and batch-wise stock inside this warehouse.</p>
        </div>
        <button type="button" @click="load">Refresh</button>
      </header>

      <section v-if="!warehouse" class="rug-section-card">
        <div class="rug-empty">
          <h2>No warehouse selected</h2>
          <p>Open a warehouse from the <RouterLink to="/inventory/warehouses">Warehouses</RouterLink> tree.</p>
        </div>
      </section>

      <template v-else>
        <ErrorState v-if="error && !data" title="Unable to load warehouse stock" :message="error.message" @retry="load" />
        <p v-else-if="error" class="rug-inline-error" role="alert">{{ error.message }}</p>

        <section class="rug-section-card">
          <div class="rug-form-grid">
            <label><span>Product</span><input v-model="filters.search" type="search" placeholder="Name or code" @change="load" /></label>
            <label><span>Category</span>
              <select v-model="filters.item_group" @change="load">
                <option value="">All categories</option>
                <option v-for="g in data?.item_groups || []" :key="g" :value="g">{{ g }}</option>
              </select>
            </label>
            <label><span>Stock status</span>
              <select v-model="filters.stock_status" @change="load">
                <option value="all">All</option>
                <option value="in_stock">In stock</option>
                <option value="low_stock">Low stock</option>
                <option value="out_of_stock">Out of stock</option>
              </select>
            </label>
            <label><span>From date</span><input v-model="filters.from_date" type="date" @change="load" /></label>
            <label><span>To date</span><input v-model="filters.to_date" type="date" @change="load" /></label>
          </div>
        </section>

        <section class="smj-henderson-summary" aria-label="Warehouse totals">
          <article><small>Products</small><strong>{{ num(totals.items) }}</strong><em>in this warehouse</em></article>
          <article><small>Actual stock</small><strong>{{ num(totals.actual_qty) }}</strong><em>physical</em></article>
          <article><small>Reserved</small><strong>{{ num(totals.reserved_qty) }}</strong><em>committed</em></article>
          <article><small>Available to sell</small><strong>{{ num(totals.available_to_sell) }}</strong><em>actual − reserved</em></article>
        </section>

        <nav class="smj-wh-tabs" aria-label="Stock views">
          <button type="button" :class="tab === 'items' && 'is-active'" @click="tab = 'items'">Item-wise</button>
          <button type="button" :class="tab === 'batches' && 'is-active'" @click="tab = 'batches'">Batch-wise</button>
          <button type="button" :class="tab === 'movements' && 'is-active'" @click="tab = 'movements'">Recent movements</button>
        </nav>

        <div v-if="loading" class="rug-skeleton"><i v-for="n in 5" :key="n" /></div>

        <section v-else-if="tab === 'items'" class="rug-section-card">
          <div v-if="!data?.rows?.length" class="rug-empty">
            <h2>No stock matches these filters</h2>
          </div>
          <div v-else class="rug-table-region">
            <table>
              <thead>
                <tr><th>Product</th><th>Category</th><th>Actual</th><th>Reserved</th><th>Available</th><th>Carton</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in data.rows" :key="row.item_code" :class="expanded === row.item_code && 'is-open'" @click="openItem(row.item_code)">
                  <td data-label="Product"><strong>{{ row.item_name }}</strong><small> {{ row.item_code }}</small></td>
                  <td data-label="Category">{{ row.item_group || "—" }}</td>
                  <td data-label="Actual">{{ num(row.actual_qty) }}</td>
                  <td data-label="Reserved">{{ num(row.reserved_qty) }}</td>
                  <td data-label="Available">{{ num(row.available_to_sell) }}</td>
                  <td data-label="Carton">{{ row.carton_qty > 1 ? `${num(row.carton_qty)} ${row.stock_uom}` : "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-if="data?.truncated" class="smj-accounts-note">Showing the first {{ data.rows.length }} of {{ data.total_rows }} products. Narrow the filters to see more.</p>
        </section>

        <section v-else-if="tab === 'batches'" class="rug-section-card">
          <header><h2>Batch-wise stock</h2><p>Oldest batch first — the order FIFO consumes them.</p></header>
          <div v-if="!batches?.rows?.length" class="rug-empty"><h2>No batch stock here</h2></div>
          <div v-else class="rug-table-region">
            <table>
              <thead><tr><th>Batch</th><th>Product</th><th>Quantity</th><th>Expiry</th></tr></thead>
              <tbody>
                <tr v-for="row in batches.rows" :key="row.batch_no + row.item_code" :class="row.expired && 'is-critical'">
                  <td data-label="Batch"><strong>{{ row.batch_no }}</strong></td>
                  <td data-label="Product">{{ row.item_code }}</td>
                  <td data-label="Quantity">{{ num(row.qty) }}</td>
                  <td data-label="Expiry">{{ row.expiry_date || "—" }}<span v-if="row.expired"> (expired)</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-else class="rug-section-card">
          <header><h2>Recent movements</h2><p>Receipts, issues and transfers from the standard Stock Ledger.</p></header>
          <div v-if="!movements?.rows?.length" class="rug-empty"><h2>No movements in this range</h2></div>
          <div v-else class="rug-table-region">
            <table>
              <thead><tr><th>Date</th><th>Product</th><th>Change</th><th>Balance</th><th>Document</th></tr></thead>
              <tbody>
                <tr v-for="(row, i) in movements.rows" :key="i">
                  <td data-label="Date">{{ row.posting_date }}</td>
                  <td data-label="Product">{{ row.item_code }}</td>
                  <td data-label="Change" :class="row.direction === 'out' ? 'is-out' : 'is-in'">{{ row.direction === "out" ? "" : "+" }}{{ num(row.actual_qty) }}</td>
                  <td data-label="Balance">{{ num(row.qty_after_transaction) }}</td>
                  <td data-label="Document">{{ row.voucher_type }} · {{ row.voucher_no }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </main>
  </PageContainer>
</template>
