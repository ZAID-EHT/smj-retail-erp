<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getWarehouseCapacity, searchAnalyticsLink } from "@/services/analyticsPages.js";

const filters = reactive({ company: "", warehouse: "", parent_warehouse: "", item_code: "", sort_by: "stock_capacity", sort_order: "desc" });
const options = reactive({ company: [], warehouse: [], parent_warehouse: [], item_code: [] });
const records = ref([]);
const start = ref(0);
const hasMore = ref(false);
const loading = ref(false);
const error = ref(null);
let controller;
const timers = {};

function search(fieldname) {
  window.clearTimeout(timers[fieldname]);
  timers[fieldname] = window.setTimeout(async () => {
    try { options[fieldname] = await searchAnalyticsLink("warehouse-capacity-summary", fieldname, filters[fieldname]); }
    catch { options[fieldname] = []; }
  }, 180);
}
async function load(nextStart = 0) {
  if (!filters.company) { error.value = new Error("Select a permitted company first."); return; }
  controller?.abort(); controller = new AbortController(); loading.value = true; error.value = null;
  try {
    const result = await getWarehouseCapacity({ ...filters, start: nextStart }, controller.signal);
    records.value = result.records || []; start.value = result.start || 0; hasMore.value = Boolean(result.has_more);
  } catch (caught) { if (caught.name !== "AbortError") error.value = caught; }
  finally { loading.value = false; }
}
async function initialise() {
  try {
    options.company = await searchAnalyticsLink("warehouse-capacity-summary", "company", "");
    if (options.company.length) filters.company = options.company[0].value;
    if (filters.company) await load();
  } catch (caught) { error.value = caught; }
}
function quantity(value) { return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 3 }); }
onBeforeUnmount(() => { controller?.abort(); Object.values(timers).forEach(window.clearTimeout); });
initialise();
</script>

<template>
  <PageContainer>
    <main class="rug-page warehouse-capacity-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/inventory">Inventory</RouterLink><span>›</span><strong>Warehouse Capacity Summary</strong></nav>
      <header class="rug-banner rug-banner--orange"><div><span class="rug-badge">ERPNext putaway analytics</span><h1>Warehouse Capacity Summary</h1><p>Compare configured Putaway Rule capacity with current stock balances while respecting warehouse and item permissions.</p></div><div class="rug-banner-actions"><button class="rug-primary" type="button" :disabled="loading || !filters.company" @click="load(0)">{{ loading ? "Refreshing…" : "Refresh" }}</button></div></header>
      <section class="rug-section-card"><header><div><h2>Filters and sorting</h2><p>Choose permitted records; technical filters stay hidden.</p></div></header><div class="rug-form-grid">
        <label v-for="field in ['company', 'warehouse', 'parent_warehouse', 'item_code']" :key="field"><span>{{ { company: 'Company *', warehouse: 'Warehouse', parent_warehouse: 'Parent Warehouse', item_code: 'Item' }[field] }}</span><input v-model="filters[field]" :list="`capacity-${field}`" type="search" autocomplete="off" @focus="search(field)" @input="search(field)" /><datalist :id="`capacity-${field}`"><option v-for="item in options[field]" :key="item.value" :value="item.value" /></datalist></label>
        <label><span>Sort by</span><select v-model="filters.sort_by"><option value="stock_capacity">Capacity</option><option value="percent_occupied">% Occupied</option><option value="actual_qty">Balance Qty</option></select></label>
        <label><span>Order</span><select v-model="filters.sort_order"><option value="desc">Highest first</option><option value="asc">Lowest first</option></select></label>
      </div></section>
      <ErrorState v-if="error" title="Unable to load Warehouse Capacity" :message="error.message" @retry="load(start)" />
      <section class="rug-section-card"><header><div><h2>Capacity records</h2><p>{{ records.length }} permitted Putaway Rule result{{ records.length === 1 ? '' : 's' }} on this page.</p></div></header>
        <div v-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>
        <div v-else-if="!records.length" class="ru-empty">No configured warehouse capacity matches these filters.</div>
        <div v-else class="rug-table-wrap"><table><thead><tr><th>Item</th><th>Warehouse</th><th>Company</th><th>Capacity</th><th>Balance Qty</th><th>Occupied</th></tr></thead><tbody><tr v-for="row in records" :key="`${row.item_code}:${row.warehouse}`"><td><RouterLink :to="`/inventory/products/${encodeURIComponent(row.item_code)}`">{{ row.item_code }}</RouterLink></td><td><RouterLink :to="`/inventory/warehouses/${encodeURIComponent(row.warehouse)}`">{{ row.warehouse }}</RouterLink></td><td>{{ row.company }}</td><td>{{ quantity(row.stock_capacity) }}</td><td>{{ quantity(row.actual_qty) }}</td><td><span class="capacity-badge" :class="{ 'is-full': row.percent_occupied >= 100 }">{{ quantity(row.percent_occupied) }}%</span></td></tr></tbody></table></div>
        <footer class="capacity-pagination"><button type="button" :disabled="loading || start === 0" @click="load(Math.max(0, start - 10))">Previous</button><span>Page {{ Math.floor(start / 10) + 1 }}</span><button type="button" :disabled="loading || !hasMore" @click="load(start + 10)">Next</button></footer>
      </section>
    </main>
  </PageContainer>
</template>

<style scoped>
.warehouse-capacity-page label{display:grid;gap:.4rem;color:var(--ref-primary-text);font-weight:700}.warehouse-capacity-page label :is(input,select){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}.capacity-badge{display:inline-flex;padding:.3rem .55rem;border-radius:999px;background:var(--ref-success-background);color:var(--ref-success);font-weight:800}.capacity-badge.is-full{background:var(--ref-warning-background);color:var(--ref-danger)}.capacity-pagination{display:flex;align-items:center;justify-content:flex-end;gap:.75rem;padding-top:1rem}.capacity-pagination button{min-height:38px;padding:0 .8rem;border:1px solid var(--ref-border-colour);border-radius:.65rem;background:var(--ref-card-background)}
</style>
