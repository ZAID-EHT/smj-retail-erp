<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

import ErrorState from "@/components/feedback/ErrorState.vue";
import {
  SmjActualStockWarehouse,
  SmjAvailableStockCheck,
  SmjClose,
  SmjCreditGauge,
  SmjInventoryCubeLayers,
  SmjReserveCubeLock,
  SmjSalesCartPulse,
} from "@/components/icons";
import PageContainer from "@/components/layout/PageContainer.vue";
import { createSmartOrder, getSmartSales, searchSmartCustomers } from "@/services/smartSales.js";
import { getCustomerCreditStatus } from "@/services/wholesale.js";

const router = useRouter();
const data = ref(null);
const error = ref(null);
const loading = ref(false);
const saving = ref(false);
const search = ref("");
const group = ref("");
const warehouse = ref("");
const priceList = ref("");
const customerSearch = ref("");
const customers = ref([]);
const customer = ref("");
const credit = ref(null);
const cart = reactive({});
let controller;
let timer;

async function loadCredit() {
  credit.value = null;
  if (!customer.value) return;
  try {
    credit.value = await getCustomerCreditStatus(customer.value, data.value?.company);
  } catch {
    credit.value = null;
  }
}

const cartRows = computed(() => Object.values(cart));
const cartQuantity = computed(() => cartRows.value.reduce((sum, row) => sum + Number(row.qty || 0), 0));
const total = computed(() => cartRows.value.reduce((sum, row) => sum + Number(row.qty) * Number(row.rate || 0), 0));
const selectedCustomer = computed(() => customers.value.find((row) => row.name === customer.value));
const stockSummary = computed(() => (data.value?.items || []).reduce(
  (summary, item) => ({
    actual: summary.actual + Number(item.actual_qty || 0),
    reserved: summary.reserved + Number(item.reserved_qty || 0),
    available: summary.available + Number(item.available_to_sell ?? item.actual_qty ?? 0),
  }),
  { actual: 0, reserved: 0, available: 0 },
));

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    data.value = await getSmartSales({
      page: 1,
      page_length: 48,
      search: search.value,
      item_group: group.value,
      warehouse: warehouse.value,
      price_list: priceList.value,
    }, controller.signal);
    warehouse.value ||= data.value.warehouses?.[0] || "";
    priceList.value ||= data.value.price_list || "";
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

function schedule() {
  clearTimeout(timer);
  timer = setTimeout(load, 300);
}

async function findCustomers() {
  if (customerSearch.value.trim().length < 2) {
    customers.value = [];
    return;
  }
  try {
    customers.value = await searchSmartCustomers(customerSearch.value, controller?.signal);
  } catch (caught) {
    error.value = caught;
  }
}

function add(item) {
  if (!cart[item.item_code]) {
    cart[item.item_code] = { item_code: item.item_code, item_name: item.item_name, rate: item.rate, qty: 1 };
  } else {
    cart[item.item_code].qty += 1;
  }
}

async function save() {
  if (saving.value) return;
  if (!customer.value || !warehouse.value || !cartRows.value.length) {
    error.value = new Error("Choose a customer and warehouse, then add at least one product.");
    return;
  }
  saving.value = true;
  error.value = null;
  try {
    const result = await createSmartOrder({
      request_id: crypto.randomUUID(),
      customer: customer.value,
      company: data.value.company,
      warehouse: warehouse.value,
      price_list: priceList.value,
      items: cartRows.value.map(({ item_code, qty }) => ({ item_code, qty })),
    });
    await router.push(result.route);
  } catch (caught) {
    error.value = caught;
  } finally {
    saving.value = false;
  }
}

watch([group, warehouse, priceList], load);
watch(customerSearch, () => {
  clearTimeout(timer);
  timer = setTimeout(findCustomers, 300);
});
watch(customer, loadCredit);
load();
onBeforeUnmount(() => {
  clearTimeout(timer);
  controller?.abort();
});
</script>

<template>
  <PageContainer>
    <ErrorState
      v-if="error && !data"
      title="Unable to load Smart Sales"
      :message="error.message"
      @retry="load"
    />
    <main v-else class="rug-page smj-sales-workspace">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span><strong>Smart Sales</strong>
      </nav>

      <header class="rug-banner rug-banner--green">
        <div>
          <span class="rug-badge">Wholesale catalogue &amp; cart</span>
          <h1>Smart Sales</h1>
          <p>Select a customer, check live credit and stock, then create a standard ERPNext Draft Sales Order.</p>
        </div>
        <button
          class="rug-primary"
          type="button"
          :disabled="saving || !data?.can_create_sales_order"
          @click="save"
        >
          {{ saving ? "Creating order…" : "Create Draft Order" }}
        </button>
      </header>

      <div v-if="error" class="rug-inline-error" role="alert">{{ error.message }}</div>

      <section class="smj-sales-kpis" aria-label="Current sale summary">
        <article>
          <span class="smj-sales-kpis__icon"><SmjSalesCartPulse size="20" decorative /></span>
          <div><small>Cart lines</small><strong>{{ cartRows.length }}</strong><em>{{ cartQuantity }} total quantity</em></div>
        </article>
        <article>
          <span class="smj-sales-kpis__icon"><SmjActualStockWarehouse size="20" decorative /></span>
          <div><small>Actual stock shown</small><strong>{{ stockSummary.actual.toLocaleString() }}</strong><em>{{ warehouse || "Select warehouse" }}</em></div>
        </article>
        <article>
          <span class="smj-sales-kpis__icon"><SmjReserveCubeLock size="20" decorative /></span>
          <div><small>Reserved stock</small><strong>{{ stockSummary.reserved.toLocaleString() }}</strong><em>ERPNext reservations</em></div>
        </article>
        <article>
          <span class="smj-sales-kpis__icon"><SmjAvailableStockCheck size="20" decorative /></span>
          <div><small>Available to sell</small><strong>{{ stockSummary.available.toLocaleString() }}</strong><em>Actual minus reserved</em></div>
        </article>
      </section>

      <section class="rug-section-card smj-sale-context">
        <header>
          <div><h2>Sale setup</h2><p>Customer, warehouse and pricing context for this order.</p></div>
          <span v-if="selectedCustomer" class="rug-value-badge">{{ selectedCustomer.customer_name }}</span>
        </header>
        <div class="priority-sales-controls">
          <label>
            <span>Find customer</span>
            <input v-model="customerSearch" type="search" placeholder="Name, mobile or customer ID…" autocomplete="off" />
          </label>
          <label>
            <span>Customer</span>
            <select v-model="customer">
              <option value="">Choose customer</option>
              <option v-for="row in customers" :key="row.name" :value="row.name">{{ row.customer_name }} · {{ row.name }}</option>
            </select>
          </label>
          <label>
            <span>Warehouse</span>
            <select v-model="warehouse"><option v-for="value in data?.warehouses || []" :key="value">{{ value }}</option></select>
          </label>
          <label>
            <span>Price List</span>
            <select v-model="priceList"><option v-for="value in data?.price_lists || []" :key="value">{{ value }}</option></select>
          </label>
        </div>

        <div
          v-if="credit"
          class="priority-credit-strip"
          :class="{ 'is-warning': credit.has_overdue || (credit.available_credit !== null && credit.available_credit <= 0) }"
        >
          <span class="smj-credit-heading"><SmjCreditGauge size="17" decorative /><strong>{{ credit.credit_type || "Credit type not set" }}</strong></span>
          <span>Outstanding <strong>{{ data?.currency }} {{ Number(credit.current_outstanding || 0).toLocaleString() }}</strong></span>
          <span v-if="credit.credit_limit">Limit <strong>{{ Number(credit.credit_limit).toLocaleString() }}</strong></span>
          <span v-if="credit.available_credit !== null">Available <strong>{{ Number(credit.available_credit).toLocaleString() }}</strong></span>
          <span v-if="credit.has_overdue" class="priority-credit-overdue">Overdue {{ Number(credit.overdue_amount).toLocaleString() }}</span>
        </div>
      </section>

      <div class="priority-sales-layout">
        <section class="rug-section-card smj-catalogue">
          <header>
            <div><h2>Product catalogue</h2><p>Live ERPNext prices and warehouse availability.</p></div>
            <span class="rug-value-badge">{{ data?.items?.length || 0 }} results</span>
          </header>
          <div class="priority-sales-controls smj-catalogue-filters">
            <label><span>Search products</span><input v-model="search" type="search" placeholder="Item code, name, group or brand…" @input="schedule" /></label>
            <label><span>Item Group</span><select v-model="group"><option value="">All groups</option><option v-for="value in data?.item_groups || []" :key="value">{{ value }}</option></select></label>
          </div>
          <div v-if="loading" class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
          <div v-else-if="!data?.items?.length" class="rug-empty"><SmjInventoryCubeLayers size="28" decorative /><h2>No products found</h2><p>Change the search, group or warehouse.</p></div>
          <div v-else class="priority-product-grid">
            <button v-for="item in data.items" :key="item.item_code" type="button" @click="add(item)">
              <img v-if="item.image" :src="item.image" :alt="item.item_name" />
              <span v-else class="priority-product-placeholder"><SmjInventoryCubeLayers size="26" decorative /></span>
              <strong>{{ item.item_name }}</strong>
              <small>{{ item.item_code }} · {{ item.item_group }}</small>
              <b>{{ data.currency }} {{ Number(item.rate || 0).toFixed(2) }}</b>
              <em>{{ Number(item.available_to_sell ?? item.actual_qty ?? 0) }} {{ item.stock_uom }} available</em>
              <span class="smj-stock-triplet">
                <small>Actual <b>{{ Number(item.actual_qty ?? 0) }}</b></small>
                <small>Reserved <b>{{ Number(item.reserved_qty ?? 0) }}</b></small>
              </span>
              <span class="smj-product-add">+ Add to cart</span>
            </button>
          </div>
        </section>

        <aside class="rug-section-card priority-cart">
          <header>
            <div><h2>Cart</h2><p>{{ cartRows.length }} product lines · {{ cartQuantity }} units</p></div>
            <SmjSalesCartPulse size="22" decorative />
          </header>
          <div v-if="!cartRows.length" class="smj-cart-empty">
            <SmjSalesCartPulse size="30" decorative />
            <strong>Your cart is empty</strong>
            <span>Select products from the catalogue.</span>
          </div>
          <article v-for="row in cartRows" :key="row.item_code">
            <div><strong>{{ row.item_name }}</strong><small>{{ row.item_code }}</small><b>{{ data?.currency }} {{ Number(row.rate || 0).toFixed(2) }}</b></div>
            <label><span class="sr-only">Quantity for {{ row.item_name }}</span><input v-model.number="row.qty" type="number" min="0.001" step="0.001" /></label>
            <button type="button" :aria-label="`Remove ${row.item_name}`" @click="delete cart[row.item_code]"><SmjClose size="14" decorative /></button>
          </article>
          <footer>
            <span>Estimated total</span>
            <strong>{{ data?.currency }} {{ total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</strong>
          </footer>
          <button class="smj-cart-submit" type="button" :disabled="saving || !data?.can_create_sales_order || !cartRows.length" @click="save">
            {{ saving ? "Creating order…" : "Create Draft Sales Order" }}
          </button>
        </aside>
      </div>
    </main>
  </PageContainer>
</template>
