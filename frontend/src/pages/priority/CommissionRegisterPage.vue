<script setup>
import { computed, ref } from "vue";
import { listCommissions, commissionExportUrl } from "@/services/commission.js";

const rows = ref([]);
const totals = ref(null);
const loading = ref(false);
const error = ref("");
const canSeeEveryone = ref(true);
const restrictedTo = ref([]);
const truncated = ref(false);

const filters = ref({
  from_date: "", to_date: "", team: "", sales_person: "", customer: "",
  sales_order: "", sales_invoice: "", payment_status: "", status: "",
});

// A late response for filters the user has already changed must never win.
let requestToken = 0;

async function load() {
  const token = ++requestToken;
  loading.value = true;
  error.value = "";
  try {
    const result = await listCommissions({ ...filters.value });
    if (token !== requestToken) return;
    rows.value = result.rows || [];
    totals.value = result.totals || null;
    canSeeEveryone.value = Boolean(result.can_see_everyone);
    restrictedTo.value = result.restricted_to || [];
    truncated.value = Boolean(result.truncated);
  } catch (caught) {
    if (token !== requestToken) return;
    error.value = caught?.message || "The commission register could not be loaded.";
    rows.value = [];
    totals.value = null;
  } finally {
    if (token === requestToken) loading.value = false;
  }
}
load();

function reset() {
  filters.value = {
    from_date: "", to_date: "", team: "", sales_person: "", customer: "",
    sales_order: "", sales_invoice: "", payment_status: "", status: "",
  };
  load();
}

const exportHref = computed(() => commissionExportUrl(filters.value));

function money(value, currency) {
  const n = Number(value || 0);
  return `${currency || ""} ${n.toLocaleString(undefined, {
    minimumFractionDigits: 2, maximumFractionDigits: 2 })}`.trim();
}
function pct(value) {
  const n = Number(value || 0);
  return `${Number.isInteger(n) ? n : n.toFixed(2)}%`;
}
</script>

<template>
  <div class="rug-page smj-commissions">
    <header class="rug-page-header">
      <div>
        <h1>Commission Register</h1>
        <p>
          Every figure is read from the team snapshot frozen onto the invoice.
          Editing a team today never changes what this report said yesterday.
        </p>
      </div>
      <a v-if="rows.length" class="rug-button" :href="exportHref" data-test="commission-export">
        Export CSV
      </a>
    </header>

    <p v-if="!canSeeEveryone" class="smj-commissions__scope" role="status">
      You are seeing your own commission lines only.
    </p>

    <section class="rug-section-card smj-commissions__filters">
      <div class="smj-commissions__filter-grid">
        <label><span>From</span><input v-model="filters.from_date" type="date" /></label>
        <label><span>To</span><input v-model="filters.to_date" type="date" /></label>
        <label><span>Team</span><input v-model="filters.team" placeholder="Team code" /></label>
        <label>
          <span>Team member</span>
          <input v-model="filters.sales_person" placeholder="Sales person" />
        </label>
        <label><span>Customer</span><input v-model="filters.customer" placeholder="Customer" /></label>
        <label>
          <span>Sales Order</span><input v-model="filters.sales_order" placeholder="Order" />
        </label>
        <label>
          <span>Sales Invoice</span><input v-model="filters.sales_invoice" placeholder="Invoice" />
        </label>
        <label>
          <span>Payment</span>
          <select v-model="filters.payment_status">
            <option value="">Any</option>
            <option value="Paid">Paid</option>
            <option value="Part Paid">Part Paid</option>
            <option value="Unpaid">Unpaid</option>
            <option value="Credit Note">Credit Note</option>
          </select>
        </label>
        <label>
          <span>Commission</span>
          <select v-model="filters.status">
            <option value="">Any</option>
            <option value="Earned">Earned</option>
            <option value="Reversed">Reversed</option>
          </select>
        </label>
      </div>
      <div class="smj-commissions__filter-actions">
        <button type="button" class="rug-button" data-test="commission-apply" @click="load">
          Apply
        </button>
        <button type="button" @click="reset">Reset</button>
      </div>
    </section>

    <p v-if="error" class="smj-team-card__warning" role="alert">{{ error }}</p>

    <section v-if="totals && rows.length" class="rug-section-card smj-commissions__totals">
      <span>Lines <strong>{{ totals.lines }}</strong></span>
      <span>Gross <strong>{{ money(totals.gross_commission) }}</strong></span>
      <span>Reversed <strong>{{ money(totals.return_reversal) }}</strong></span>
      <span>Net <strong data-test="commission-net">{{ money(totals.net_commission) }}</strong></span>
    </section>

    <section class="rug-section-card">
      <div v-if="loading" class="smj-team-card__state" role="status">Loading commission lines…</div>
      <div v-else-if="!rows.length" class="smj-team-card__state">
        No commission has been recorded for these filters yet.
      </div>
      <template v-else>
        <p v-if="truncated" class="smj-team-card__warning" role="status">
          Showing the most recent invoices only. Narrow the date range to see the rest.
        </p>
        <div class="smj-table-scroll">
          <table class="rug-table smj-commissions__table" data-test="commission-table">
            <thead>
              <tr>
                <th>Date</th><th>Invoice</th><th>Order</th><th>Customer</th><th>Team</th>
                <th>Member</th><th>Role</th><th class="is-num">Alloc</th>
                <th class="is-num">Base</th><th class="is-num">Rate</th>
                <th class="is-num">Gross</th><th class="is-num">Reversal</th>
                <th class="is-num">Net</th><th>Payment</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in rows" :key="`${row.sales_invoice}-${row.sales_person}-${index}`"
                  :class="row.is_return && 'is-return'">
                <td>{{ row.date }}</td>
                <td><router-link :to="`/sales/invoices/${encodeURIComponent(row.sales_invoice)}`">
                  {{ row.sales_invoice }}</router-link></td>
                <td>
                  <router-link v-if="row.sales_order"
                               :to="`/sales/orders/${encodeURIComponent(row.sales_order)}`">
                    {{ row.sales_order }}</router-link>
                  <span v-else>—</span>
                </td>
                <td>{{ row.customer_name }}</td>
                <td>
                  {{ row.team_name }}
                  <small v-if="row.team_source === 'Overridden'" :title="row.override_reason">
                    overridden</small>
                </td>
                <td>{{ row.sales_person_name }}</td>
                <td>{{ row.role }}</td>
                <td class="is-num">{{ pct(row.allocation_percentage) }}</td>
                <td class="is-num">{{ money(row.commission_base, row.currency) }}</td>
                <td class="is-num">{{ pct(row.commission_rate) }}</td>
                <td class="is-num">{{ money(row.gross_commission, row.currency) }}</td>
                <td class="is-num">{{ money(row.return_reversal, row.currency) }}</td>
                <td class="is-num"><strong>{{ money(row.net_commission, row.currency) }}</strong></td>
                <td>{{ row.payment_status }}</td>
                <td>{{ row.commission_status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </section>
  </div>
</template>
