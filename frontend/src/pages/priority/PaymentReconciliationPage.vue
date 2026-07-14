<script setup>
import { computed, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  getUnreconciledEntries,
  previewReconciliationAllocation,
  reconcilePayments,
  searchReconciliationCompany,
  searchReconciliationParty,
} from "@/services/wholesale.js";

const filters = reactive({ company: "", party_type: "Customer", party: "" });
const companyOptions = ref([]);
const partyOptions = ref([]);
let companyTimer;
let partyTimer;

const step = ref("filter"); // filter -> entries -> allocation -> done
const loading = ref(false);
const error = ref(null);
const successMessage = ref(null);

const receivablePayableAccount = ref("");
const invoices = ref([]);
const payments = ref([]);
const selectedInvoiceNames = ref(new Set());
const selectedPaymentNames = ref(new Set());
const allocation = ref([]);

const selectedInvoices = computed(() => invoices.value.filter((row) => selectedInvoiceNames.value.has(row.invoice_number)));
const selectedPayments = computed(() => payments.value.filter((row) => selectedPaymentNames.value.has(row.reference_name)));
const canPreview = computed(() => selectedInvoices.value.length > 0 && selectedPayments.value.length > 0);
const allocationTotal = computed(() => allocation.value.reduce((sum, row) => sum + (Number(row.allocated_amount) || 0), 0));

function searchCompany() {
  window.clearTimeout(companyTimer);
  companyTimer = window.setTimeout(async () => {
    try { companyOptions.value = await searchReconciliationCompany(filters.company); } catch { companyOptions.value = []; }
  }, 250);
}
function searchParty() {
  window.clearTimeout(partyTimer);
  partyTimer = window.setTimeout(async () => {
    try { partyOptions.value = await searchReconciliationParty(filters.party_type, filters.party); } catch { partyOptions.value = []; }
  }, 250);
}

async function fetchEntries() {
  if (!filters.company || !filters.party) return;
  loading.value = true;
  error.value = null;
  successMessage.value = null;
  try {
    const result = await getUnreconciledEntries({ company: filters.company, party_type: filters.party_type, party: filters.party });
    receivablePayableAccount.value = result.receivable_payable_account;
    invoices.value = result.invoices || [];
    payments.value = result.payments || [];
    selectedInvoiceNames.value = new Set();
    selectedPaymentNames.value = new Set();
    allocation.value = [];
    step.value = "entries";
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

function toggleInvoice(name) {
  const set = new Set(selectedInvoiceNames.value);
  if (set.has(name)) set.delete(name); else set.add(name);
  selectedInvoiceNames.value = set;
}
function togglePayment(name) {
  const set = new Set(selectedPaymentNames.value);
  if (set.has(name)) set.delete(name); else set.add(name);
  selectedPaymentNames.value = set;
}

async function previewAllocation() {
  loading.value = true;
  error.value = null;
  try {
    const result = await previewReconciliationAllocation({
      company: filters.company, party_type: filters.party_type, party: filters.party,
      receivable_payable_account: receivablePayableAccount.value,
      invoices: selectedInvoices.value, payments: selectedPayments.value,
    });
    allocation.value = result.allocation || [];
    step.value = "allocation";
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

async function confirmReconcile() {
  if (!window.confirm(`Reconcile ${allocation.value.length} allocation row(s) totalling ${allocationTotal.value.toLocaleString()}? This posts against real Payment Entry / Invoice records and cannot be done from this screen once submitted.`)) return;
  loading.value = true;
  error.value = null;
  try {
    await reconcilePayments({
      company: filters.company, party_type: filters.party_type, party: filters.party,
      receivable_payable_account: receivablePayableAccount.value, allocation: allocation.value,
    });
    successMessage.value = `Reconciled ${allocation.value.length} allocation row(s) for ${filters.party}.`;
    step.value = "done";
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

function startOver() {
  step.value = "filter";
  invoices.value = []; payments.value = []; allocation.value = [];
  selectedInvoiceNames.value = new Set(); selectedPaymentNames.value = new Set();
  successMessage.value = null; error.value = null;
}
</script>

<template>
  <PageContainer>
    <main class="rug-page">
      <nav class="rug-breadcrumbs"><RouterLink to="/home">Home</RouterLink><span>›</span><strong>Payment Reconciliation</strong></nav>
      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Special adapter</span>
          <h1>Payment Reconciliation</h1>
          <p>Match unreconciled payments against outstanding invoices using ERPNext's standard reconciliation engine. No shadow ledger — every figure and the final posting come from ERPNext itself.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Reconciliation request failed" :message="error.message" @retry="() => (error = null)" />

      <section class="rug-section-card">
        <div class="rug-form-grid">
          <label>
            Company
            <input v-model="filters.company" list="rug-recon-companies" type="search" autocomplete="off" placeholder="Search company" :disabled="step !== 'filter'" @input="searchCompany" @focus="searchCompany" />
            <datalist id="rug-recon-companies"><option v-for="c in companyOptions" :key="c.value" :value="c.value">{{ c.label }}</option></datalist>
          </label>
          <label>
            Party type
            <select v-model="filters.party_type" :disabled="step !== 'filter'" @change="filters.party = ''">
              <option value="Customer">Customer (Receivable)</option>
              <option value="Supplier">Supplier (Payable)</option>
            </select>
          </label>
          <label>
            {{ filters.party_type }}
            <input v-model="filters.party" list="rug-recon-parties" type="search" autocomplete="off" :placeholder="`Search ${filters.party_type.toLowerCase()}`" :disabled="step !== 'filter'" @input="searchParty" @focus="searchParty" />
            <datalist id="rug-recon-parties"><option v-for="p in partyOptions" :key="p.value" :value="p.value">{{ p.label }}</option></datalist>
          </label>
        </div>
        <div class="rug-banner-actions">
          <button v-if="step === 'filter'" type="button" class="rug-primary" :disabled="!filters.company || !filters.party || loading" @click="fetchEntries">
            {{ loading ? "Loading…" : "Fetch unreconciled entries" }}
          </button>
          <button v-else type="button" class="rug-secondary" @click="startOver">Start over</button>
        </div>
      </section>

      <section v-if="step === 'entries' || step === 'allocation'" class="rug-list-card">
        <div class="rug-count"><span><strong>{{ invoices.length }}</strong> unreconciled invoices, <strong>{{ payments.length }}</strong> unreconciled payments</span></div>
        <div v-if="!invoices.length || !payments.length" class="rug-empty">
          {{ !invoices.length ? "No outstanding invoices for this party." : "No unallocated payments for this party." }}
        </div>
        <div v-else class="rug-table-region">
          <table>
            <thead><tr><th></th><th>Invoice</th><th>Date</th><th>Outstanding</th></tr></thead>
            <tbody>
              <tr v-for="row in invoices" :key="row.invoice_number">
                <td><input type="checkbox" :checked="selectedInvoiceNames.has(row.invoice_number)" :disabled="step !== 'entries'" @change="toggleInvoice(row.invoice_number)" /></td>
                <td>{{ row.invoice_number }}</td>
                <td>{{ row.invoice_date }}</td>
                <td>{{ Number(row.outstanding_amount || 0).toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
          <table>
            <thead><tr><th></th><th>Payment / Journal</th><th>Date</th><th>Amount</th></tr></thead>
            <tbody>
              <tr v-for="row in payments" :key="row.reference_name">
                <td><input type="checkbox" :checked="selectedPaymentNames.has(row.reference_name)" :disabled="step !== 'entries'" @change="togglePayment(row.reference_name)" /></td>
                <td>{{ row.reference_name }}</td>
                <td>{{ row.posting_date }}</td>
                <td>{{ Number(row.amount || 0).toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="step === 'entries'" class="rug-banner-actions">
          <button type="button" class="rug-primary" :disabled="!canPreview || loading" @click="previewAllocation">
            {{ loading ? "Calculating…" : `Preview allocation (${selectedInvoices.length} invoice(s), ${selectedPayments.length} payment(s))` }}
          </button>
        </div>
      </section>

      <section v-if="step === 'allocation'" class="rug-list-card">
        <div class="rug-count"><span><strong>{{ allocation.length }}</strong> proposed allocation row(s)</span><span>Total allocated: {{ allocationTotal.toLocaleString() }}</span></div>
        <div v-if="!allocation.length" class="rug-empty">No allocation could be computed for this selection.</div>
        <div v-else class="rug-table-region">
          <table>
            <thead><tr><th>Payment</th><th>Invoice</th><th>Allocated</th><th>Difference</th></tr></thead>
            <tbody>
              <tr v-for="(row, index) in allocation" :key="index">
                <td>{{ row.reference_name }}</td>
                <td>{{ row.invoice_number }}</td>
                <td>{{ Number(row.allocated_amount || 0).toLocaleString() }}</td>
                <td>{{ Number(row.difference_amount || 0).toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="rug-banner-actions">
          <button type="button" class="rug-primary" :disabled="!allocation.length || loading" @click="confirmReconcile">
            {{ loading ? "Posting…" : "Reconcile" }}
          </button>
        </div>
      </section>

      <section v-if="step === 'done'" class="rug-section-card">
        <p class="rug-empty">{{ successMessage }}</p>
        <div class="rug-banner-actions"><button type="button" class="rug-primary" @click="startOver">Reconcile another party</button></div>
      </section>

      <section class="rug-warning">
        <strong>Standard ERPNext reconciliation engine</strong>
        <span>This page calls the same get_unreconciled_entries / allocate_entries / reconcile methods the ERPNext Desk client uses. No GL Entry, Payment Ledger Entry or outstanding balance is computed here directly.</span>
      </section>
    </main>
  </PageContainer>
</template>
