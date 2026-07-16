<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import { SmjDeliveryTruckArrow, SmjFinanceWalletLedger, SmjPaymentWalletCheck, SmjTransactionDocumentChain } from "@/components/icons";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getWholesaleTransactions } from "@/services/wholesale.js";

const data = ref(null);
const error = ref(null);
const loading = ref(false);
const page = ref(1);
const sort = reactive({ field: "transaction_date", order: "desc" });
const filters = reactive({ customer: "", status: "", from_date: "", to_date: "" });
let controller;

const columns = computed(() => data.value?.columns || []);
const rows = computed(() => data.value?.rows || []);
const pagination = computed(() => data.value?.pagination || { page: 1, pages: 1, total: 0 });

const totals = computed(() => {
  if (!data.value?.shows_financials) return null;
  return rows.value.reduce(
    (acc, row) => ({
      grand_total: acc.grand_total + (row.grand_total || 0),
      paid_amount: acc.paid_amount + (row.paid_amount || 0),
      outstanding_amount: acc.outstanding_amount + (row.outstanding_amount || 0),
    }),
    { grand_total: 0, paid_amount: 0, outstanding_amount: 0 },
  );
});

const registerSummary = computed(() => ({
  transactions: pagination.value.total || 0,
  delivered: rows.value.filter((row) => /delivered|completed/i.test(String(row.delivery_status || ""))).length,
  paid: rows.value.filter((row) => /paid|completed/i.test(String(row.payment_status || ""))).length,
  pageValue: totals.value?.grand_total || 0,
  outstanding: totals.value?.outstanding_amount || 0,
}));

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    const activeFilters = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
    data.value = await getWholesaleTransactions(
      { filters: activeFilters, page: page.value, page_size: 20, sort_field: sort.field, sort_order: sort.order },
      controller.signal,
    );
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

function applyFilters() { page.value = 1; load(); }
function resetFilters() { Object.keys(filters).forEach((k) => (filters[k] = "")); page.value = 1; load(); }
function setSort(field) {
  if (sort.field === field) sort.order = sort.order === "asc" ? "desc" : "asc";
  else { sort.field = field; sort.order = "asc"; }
  load();
}
function changePage(delta) {
  const next = page.value + delta;
  if (next >= 1 && next <= pagination.value.pages) { page.value = next; load(); }
}

function formatValue(row, column) {
  const value = row[column.fieldname];
  if (value === undefined || value === null || value === "") return "—";
  if (column.fieldtype === "Currency") return Number(value).toLocaleString();
  return value;
}

function docRoute(doctype, name) {
  const map = {
    "Sales Order": "/sales/orders/",
    "Sales Invoice": "/sales/invoices/",
    "Delivery Note": "/sales/delivery-notes/",
    "Payment Entry": "/finance/payments/",
  };
  return map[doctype] ? `${map[doctype]}${encodeURIComponent(name)}` : null;
}

function exportCsv() {
  const header = columns.value.map((c) => c.label);
  const lines = rows.value.map((row) => columns.value.map((c) => JSON.stringify(row[c.fieldname] ?? "")).join(","));
  const csv = [header.join(","), ...lines].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "wholesale-transactions.csv";
  link.click();
  URL.revokeObjectURL(url);
}

watch(() => null, load, { immediate: true });
onBeforeUnmount(() => controller?.abort());
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="error?.permissionDenied" />
    <ErrorState v-else-if="error" title="Unable to load transactions" :message="error.message" @retry="load" />
    <main v-else class="rug-page">
      <nav class="rug-breadcrumbs"><RouterLink to="/home">Home</RouterLink><span>›</span><strong>Wholesale Transactions</strong></nav>
      <header class="rug-banner rug-banner--blue">
        <div>
          <span class="rug-badge">Register</span>
          <h1>Wholesale Transactions</h1>
          <p>One row per transaction. Figures come from ERPNext; there is no shadow ledger.</p>
        </div>
        <div class="rug-banner-actions">
          <button type="button" class="rug-primary" :disabled="!rows.length" @click="exportCsv">Export CSV</button>
        </div>
      </header>

      <section class="smj-register-kpis" aria-label="Transaction register summary">
        <article><span><SmjTransactionDocumentChain size="20" decorative /></span><div><small>Total transactions</small><strong>{{ registerSummary.transactions.toLocaleString() }}</strong><em>All matching records</em></div></article>
        <article><span><SmjDeliveryTruckArrow size="20" decorative /></span><div><small>Delivered</small><strong>{{ registerSummary.delivered.toLocaleString() }}</strong><em>Current page</em></div></article>
        <article><span><SmjPaymentWalletCheck size="20" decorative /></span><div><small>Paid</small><strong>{{ registerSummary.paid.toLocaleString() }}</strong><em>Current page</em></div></article>
        <article v-if="data?.shows_financials"><span><SmjFinanceWalletLedger size="20" decorative /></span><div><small>Page value</small><strong>{{ registerSummary.pageValue.toLocaleString() }}</strong><em>ERPNext totals</em></div></article>
        <article v-if="data?.shows_financials"><span><SmjFinanceWalletLedger size="20" decorative /></span><div><small>Outstanding</small><strong>{{ registerSummary.outstanding.toLocaleString() }}</strong><em>Current page</em></div></article>
      </section>

      <section class="rug-section-card">
        <div class="rug-form-grid">
          <label>Customer<input v-model="filters.customer" type="text" placeholder="Customer id" /></label>
          <label>Status<input v-model="filters.status" type="text" placeholder="e.g. To Deliver and Bill" /></label>
          <label>From<input v-model="filters.from_date" type="date" /></label>
          <label>To<input v-model="filters.to_date" type="date" /></label>
        </div>
        <div class="rug-banner-actions">
          <button type="button" class="rug-primary" @click="applyFilters">Apply</button>
          <button type="button" class="rug-secondary" @click="resetFilters">Reset</button>
        </div>
      </section>

      <section class="rug-list-card">
        <div class="rug-count">
          <span><strong>{{ pagination.total }}</strong> transactions</span>
          <span v-if="!data?.shows_financials">Financial columns are hidden for your role</span>
        </div>

        <div v-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>
        <div v-else-if="!rows.length" class="rug-empty">No transactions match the current filters.</div>

        <div v-else class="rug-table-region">
          <table>
            <thead>
              <tr>
                <th v-for="column in columns" :key="column.fieldname">
                  <button type="button" class="rug-sort" @click="setSort(column.fieldname === 'transaction_id' ? 'name' : column.fieldname)">{{ column.label }}</button>
                </th>
                <th>Documents</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.sales_order">
                <td v-for="column in columns" :key="column.fieldname">
                  <RouterLink v-if="column.fieldname === 'sales_order'" :to="`/sales/orders/${encodeURIComponent(row.sales_order)}`">{{ row.sales_order }}</RouterLink>
                  <span v-else>{{ formatValue(row, column) }}</span>
                </td>
                <td class="rug-doc-links">
                  <RouterLink v-for="si in row.sales_invoices" :key="si" :to="`/sales/invoices/${encodeURIComponent(si)}`" class="rug-chip">{{ si }}</RouterLink>
                  <RouterLink v-for="dn in row.delivery_notes" :key="dn" :to="`/sales/delivery-notes/${encodeURIComponent(dn)}`" class="rug-chip">{{ dn }}</RouterLink>
                  <RouterLink v-for="pe in row.payment_entries" :key="pe" :to="`/finance/payments/${encodeURIComponent(pe)}`" class="rug-chip">{{ pe }}</RouterLink>
                </td>
              </tr>
            </tbody>
            <tfoot v-if="totals">
              <tr>
                <td :colspan="columns.findIndex((c) => c.fieldname === 'grand_total')">Totals (page)</td>
                <td>{{ totals.grand_total.toLocaleString() }}</td>
                <td>{{ totals.paid_amount.toLocaleString() }}</td>
                <td>{{ totals.outstanding_amount.toLocaleString() }}</td>
                <td :colspan="4"></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Mobile card layout -->
        <div v-if="rows.length && !loading" class="rug-card-list">
          <article v-for="row in rows" :key="`card-${row.sales_order}`" class="rug-txn-card">
            <header><strong>{{ row.transaction_id }}</strong><span>{{ row.overall_status }}</span></header>
            <p>{{ row.customer_name }} <small v-if="row.customer_type">· {{ row.customer_type }}</small></p>
            <dl>
              <div><dt>Delivery</dt><dd>{{ row.delivery_status }}</dd></div>
              <div><dt>Payment</dt><dd>{{ row.payment_status }}</dd></div>
              <div v-if="data?.shows_financials"><dt>Outstanding</dt><dd>{{ (row.outstanding_amount || 0).toLocaleString() }}</dd></div>
            </dl>
          </article>
        </div>

        <div class="rug-count">
          <button type="button" class="rug-secondary" :disabled="pagination.page <= 1" @click="changePage(-1)">Previous</button>
          <span>Page {{ pagination.page }} of {{ pagination.pages }}</span>
          <button type="button" class="rug-secondary" :disabled="pagination.page >= pagination.pages" @click="changePage(1)">Next</button>
        </div>
      </section>

      <section v-if="!data?.transaction_id_field_present" class="rug-warning">
        <strong>Interim transaction ids</strong>
        <span>The shared Transaction ID field is not applied on this site yet, so the Sales Order number is shown as the transaction id. Apply the my_store_ui fixtures to enable TRX-YYYY-###### ids.</span>
      </section>
    </main>
  </PageContainer>
</template>
