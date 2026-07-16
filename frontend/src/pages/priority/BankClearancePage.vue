<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  getBankClearanceEntries,
  searchBankClearanceAccounts,
  searchBankClearanceBankAccounts,
  updateBankClearanceDates,
} from "@/services/wholesale.js";

const now = new Date();
const filters = reactive({
  account: "",
  bank_account: "",
  from_date: new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10),
  to_date: new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().slice(0, 10),
  include_reconciled_entries: 0,
  include_pos_transactions: 0,
});
const accountOptions = ref([]);
const bankAccountOptions = ref([]);
const entries = ref([]);
const changed = ref(new Set());
const loading = ref(false);
const saving = ref(false);
const loaded = ref(false);
const error = ref(null);
const success = ref("");
let accountTimer;
let bankTimer;

function key(row) { return `${row.payment_document}:${row.payment_entry}`; }
function documentRoute(row) {
  const bases = {
    "Journal Entry": "/finance/journal-entries",
    "Payment Entry": "/finance/payments",
    "Sales Invoice": "/sales/invoices",
    "Purchase Invoice": "/purchases/invoices",
  };
  return bases[row.payment_document] ? `${bases[row.payment_document]}/${encodeURIComponent(row.payment_entry)}` : "";
}
function searchAccounts() {
  window.clearTimeout(accountTimer);
  accountTimer = window.setTimeout(async () => {
    try { accountOptions.value = await searchBankClearanceAccounts(filters.account); } catch { accountOptions.value = []; }
  }, 200);
}
function searchBankAccounts() {
  window.clearTimeout(bankTimer);
  bankTimer = window.setTimeout(async () => {
    try { bankAccountOptions.value = await searchBankClearanceBankAccounts(filters.bank_account, filters.account); } catch { bankAccountOptions.value = []; }
  }, 200);
}
function markChanged(row) {
  const next = new Set(changed.value);
  next.add(key(row));
  changed.value = next;
}
async function loadEntries() {
  loading.value = true;
  error.value = null;
  success.value = "";
  try {
    const result = await getBankClearanceEntries({ ...filters });
    entries.value = result.payment_entries || [];
    changed.value = new Set();
    loaded.value = true;
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}
async function saveDates() {
  const rows = entries.value
    .filter((row) => changed.value.has(key(row)))
    .map((row) => ({ payment_document: row.payment_document, payment_entry: row.payment_entry, clearance_date: row.clearance_date || null }));
  if (!rows.length) return;
  if (!window.confirm(`Update clearance dates on ${rows.length} ERPNext voucher(s)?`)) return;
  saving.value = true;
  error.value = null;
  success.value = "";
  try {
    const result = await updateBankClearanceDates({ ...filters }, rows);
    entries.value = result.payment_entries || [];
    changed.value = new Set();
    success.value = `${result.updated} clearance date${result.updated === 1 ? "" : "s"} updated through ERPNext.`;
  } catch (caught) {
    error.value = caught;
  } finally {
    saving.value = false;
  }
}
function beforeUnload(event) {
  if (!changed.value.size) return;
  event.preventDefault();
  event.returnValue = "";
}
window.addEventListener("beforeunload", beforeUnload);
onBeforeUnmount(() => {
  window.clearTimeout(accountTimer);
  window.clearTimeout(bankTimer);
  window.removeEventListener("beforeunload", beforeUnload);
});
</script>

<template>
  <PageContainer>
    <main class="rug-page bank-clearance-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/finance">Finance</RouterLink><span>›</span><strong>Bank Clearance</strong></nav>
      <header class="rug-banner rug-banner--purple">
        <div><span class="rug-badge">ERPNext banking tool</span><h1>Bank Clearance</h1><p>Review submitted payments and update their clearance dates through ERPNext's standard Bank Clearance controller.</p></div>
        <div class="rug-banner-actions"><button type="button" :disabled="loading" @click="loadEntries">{{ loading ? "Loading…" : "Get payment entries" }}</button><button class="rug-primary" type="button" :disabled="saving || !changed.size" @click="saveDates">{{ saving ? "Updating…" : `Update clearance dates${changed.size ? ` (${changed.size})` : ""}` }}</button></div>
      </header>

      <ErrorState v-if="error" title="Bank Clearance could not be completed" :message="error.message" @retry="loadEntries" />
      <p v-if="success" class="rug-success" role="status">{{ success }}</p>

      <section class="rug-section-card">
        <header><div><h2>Filters</h2><p>Only permitted Bank, Cash and company Bank Account records are searchable.</p></div></header>
        <div class="rug-form-grid">
          <label><span>Account <b>*</b></span><input v-model="filters.account" list="bank-clearance-accounts" type="search" autocomplete="off" placeholder="Search Bank or Cash account…" @focus="searchAccounts" @input="searchAccounts" /><datalist id="bank-clearance-accounts"><option v-for="option in accountOptions" :key="option.value" :value="option.value">{{ option.label }}</option></datalist></label>
          <label><span>Bank Account</span><input v-model="filters.bank_account" list="bank-clearance-bank-accounts" type="search" autocomplete="off" placeholder="Optional company Bank Account…" @focus="searchBankAccounts" @input="searchBankAccounts" /><datalist id="bank-clearance-bank-accounts"><option v-for="option in bankAccountOptions" :key="option.value" :value="option.value">{{ option.label }}</option></datalist></label>
          <label><span>From Date <b>*</b></span><input v-model="filters.from_date" type="date" /></label>
          <label><span>To Date <b>*</b></span><input v-model="filters.to_date" type="date" /></label>
          <label class="bank-clearance-check"><input v-model="filters.include_reconciled_entries" :true-value="1" :false-value="0" type="checkbox" /><span>Include reconciled entries</span></label>
          <label class="bank-clearance-check"><input v-model="filters.include_pos_transactions" :true-value="1" :false-value="0" type="checkbox" /><span>Include POS transactions</span></label>
        </div>
      </section>

      <section class="rug-section-card">
        <header><div><h2>Payment entries</h2><p>{{ entries.length }} permitted voucher{{ entries.length === 1 ? "" : "s" }} returned.</p></div></header>
        <div v-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>
        <div v-else-if="loaded && !entries.length" class="ru-empty">No eligible payment entries match these filters.</div>
        <div v-else-if="entries.length" class="rug-table-wrap">
          <table><thead><tr><th>Document</th><th>Posting Date</th><th>Against Account</th><th>Cheque / Reference</th><th>Amount</th><th>Clearance Date</th></tr></thead><tbody>
            <tr v-for="row in entries" :key="key(row)">
              <td><RouterLink v-if="documentRoute(row)" :to="documentRoute(row)">{{ row.payment_entry }}</RouterLink><strong v-else>{{ row.payment_entry }}</strong><small>{{ row.payment_document }}</small></td>
              <td>{{ row.posting_date || "—" }}</td><td>{{ row.against_account || "—" }}</td><td>{{ row.cheque_number || "—" }}<small>{{ row.cheque_date || "" }}</small></td><td>{{ row.amount || "—" }}</td>
              <td><input v-model="row.clearance_date" type="date" :aria-label="`Clearance date for ${row.payment_entry}`" @input="markChanged(row)" /></td>
            </tr>
          </tbody></table>
        </div>
      </section>
    </main>
  </PageContainer>
</template>

<style scoped>
.bank-clearance-page label { display: grid; gap: .4rem; color: var(--ref-primary-text); font-weight: 700; }
.bank-clearance-page label input:not([type="checkbox"]) { min-height: 44px; border: 1px solid var(--ref-border-colour); border-radius: .75rem; padding: 0 .8rem; background: var(--ref-card-background); color: var(--ref-primary-text); }
.bank-clearance-check { display: flex !important; align-items: center; align-self: end; min-height: 44px; }
.bank-clearance-check input { width: 1.1rem; height: 1.1rem; }
.bank-clearance-page td small { display: block; color: var(--ref-secondary-text); margin-top: .2rem; }
.bank-clearance-page td input { min-width: 9rem; min-height: 38px; border: 1px solid var(--ref-border-colour); border-radius: .6rem; padding: 0 .5rem; }
.rug-success { border: 1px solid var(--ref-success); border-radius: .75rem; padding: .8rem 1rem; background: var(--ref-success-background); color: var(--ref-primary-text); }
@media (max-width: 720px) { .rug-banner-actions { width: 100%; } .rug-banner-actions button { flex: 1; } }
</style>
