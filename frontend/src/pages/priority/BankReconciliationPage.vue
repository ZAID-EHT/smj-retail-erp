<script setup>
import { computed, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  autoReconcileBankTransactions,
  confirmBankJournalEntry,
  confirmBankPaymentEntry,
  getBankReconciliationSummary,
  getBankTransactionMatches,
  previewBankJournalEntry,
  previewBankPaymentEntry,
  reconcileBankTransaction,
  searchAccount,
  searchBankAccount,
  searchBankReconciliationParty,
  searchModeOfPayment,
  searchReconciliationCompany,
  unreconcileBankTransaction,
  updateBankTransactionReference,
} from "@/services/wholesale.js";

const today = new Date().toISOString().slice(0, 10);
const monthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);

const filters = reactive({
  company: "", bank_account: "",
  bank_statement_from_date: monthAgo, bank_statement_to_date: today,
  bank_statement_closing_balance: 0,
});
const companyOptions = ref([]);
const bankAccountOptions = ref([]);
let companyTimer, bankAccountTimer;

const loading = ref(false);
const autoReconciling = ref(false);
const error = ref(null);
const successMessage = ref(null);
const summary = ref(null);
const loaded = ref(false);

const expandedRow = ref(null); // bank_transaction name
const panelMode = ref(null); // 'match' | 'payment' | 'journal'
const matches = ref([]);
const selectedMatchKeys = ref(new Set());
const matchLoading = ref(false);

const peForm = reactive({ party_type: "Customer", party: "", reference_number: "", reference_date: today, posting_date: today, mode_of_payment: "", project: "", cost_center: "" });
const jeForm = reactive({ second_account: "", entry_type: "Bank Entry", party_type: "", party: "", reference_number: "", reference_date: today, posting_date: today, mode_of_payment: "" });
const partyOptions = ref([]);
const accountOptions = ref([]);
const modeOptions = ref([]);
const previewDoc = ref(null);

const JE_TYPES = ["Bank Entry", "Cash Entry", "Journal Entry", "Credit Card Entry", "Contra Entry", "Debit Note", "Credit Note"];

const difference = computed(() => summary.value?.difference ?? 0);
const selectedMatches = computed(() => matches.value.filter((row) => selectedMatchKeys.value.has(`${row.doctype}:${row.name}`)));
const selectedMatchTotal = computed(() => selectedMatches.value.reduce((sum, row) => sum + (Number(row.paid_amount) || 0), 0));

function searchCompany() {
  window.clearTimeout(companyTimer);
  companyTimer = window.setTimeout(async () => {
    try { companyOptions.value = await searchReconciliationCompany(filters.company); } catch { companyOptions.value = []; }
  }, 250);
}
function searchBankAcct() {
  window.clearTimeout(bankAccountTimer);
  bankAccountTimer = window.setTimeout(async () => {
    try { bankAccountOptions.value = await searchBankAccount(filters.bank_account, filters.company); } catch { bankAccountOptions.value = []; }
  }, 250);
}
let partyTimer, accountTimer, modeTimer;
function searchPartyFor(form) {
  window.clearTimeout(partyTimer);
  partyTimer = window.setTimeout(async () => {
    try { partyOptions.value = await searchBankReconciliationParty(form.party_type, form.party); } catch { partyOptions.value = []; }
  }, 250);
}
function searchJeAccount() {
  window.clearTimeout(accountTimer);
  accountTimer = window.setTimeout(async () => {
    try { accountOptions.value = await searchAccount(jeForm.second_account, filters.company); } catch { accountOptions.value = []; }
  }, 250);
}
function searchMode(form) {
  window.clearTimeout(modeTimer);
  modeTimer = window.setTimeout(async () => {
    try { modeOptions.value = await searchModeOfPayment(form.mode_of_payment); } catch { modeOptions.value = []; }
  }, 250);
}

async function fetchSummary() {
  if (!filters.company || !filters.bank_account) return;
  loading.value = true;
  error.value = null;
  successMessage.value = null;
  closePanel();
  try {
    summary.value = await getBankReconciliationSummary({ ...filters });
    loaded.value = true;
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

function closePanel() {
  expandedRow.value = null;
  panelMode.value = null;
  matches.value = [];
  selectedMatchKeys.value = new Set();
  previewDoc.value = null;
}

function openPanel(row, mode) {
  if (expandedRow.value === row.name && panelMode.value === mode) { closePanel(); return; }
  expandedRow.value = row.name;
  panelMode.value = mode;
  matches.value = [];
  selectedMatchKeys.value = new Set();
  previewDoc.value = null;
  peForm.reference_number = row.reference_number || "";
  jeForm.reference_number = row.reference_number || "";
  if (mode === "match") fetchMatches(row);
}

async function fetchMatches(row) {
  matchLoading.value = true;
  error.value = null;
  try {
    matches.value = await getBankTransactionMatches({
      bank_transaction_name: row.name,
      document_types: ["payment_entry", "journal_entry", "sales_invoice", "purchase_invoice"],
      from_date: filters.bank_statement_from_date, to_date: filters.bank_statement_to_date,
    });
  } catch (caught) {
    error.value = caught;
  } finally {
    matchLoading.value = false;
  }
}

function toggleMatch(row) {
  const key = `${row.doctype}:${row.name}`;
  const set = new Set(selectedMatchKeys.value);
  if (set.has(key)) set.delete(key); else set.add(key);
  selectedMatchKeys.value = set;
}

async function reconcileSelected(row) {
  if (!selectedMatches.value.length) return;
  if (!window.confirm(`Reconcile ${row.name} against ${selectedMatches.value.length} voucher(s) totalling ${selectedMatchTotal.value.toLocaleString()}? This updates real ERPNext records.`)) return;
  loading.value = true;
  error.value = null;
  try {
    const vouchers = selectedMatches.value.map((m) => ({ payment_doctype: m.doctype, payment_name: m.name, amount: m.paid_amount }));
    await reconcileBankTransaction({ bank_transaction_name: row.name, vouchers });
    successMessage.value = `${row.name} reconciled against ${vouchers.length} voucher(s).`;
    closePanel();
    await fetchSummary();
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

async function unreconcile(row) {
  if (!window.confirm(`Remove all payment links from ${row.name}? This does not delete the linked Payment/Journal Entry, only unlinks it from this bank transaction.`)) return;
  loading.value = true;
  error.value = null;
  try {
    await unreconcileBankTransaction({ bank_transaction_name: row.name });
    successMessage.value = `${row.name} unreconciled.`;
    closePanel();
    await fetchSummary();
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

async function previewPayment(row) {
  loading.value = true;
  error.value = null;
  try {
    previewDoc.value = await previewBankPaymentEntry({ bank_transaction_name: row.name, ...peForm });
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

async function confirmPayment(row) {
  if (!window.confirm(`Create and submit a Payment Entry for ${row.name}? This posts a real, submitted ERPNext document.`)) return;
  loading.value = true;
  error.value = null;
  try {
    await confirmBankPaymentEntry({ bank_transaction_name: row.name, ...peForm });
    successMessage.value = `Payment Entry created and reconciled against ${row.name}.`;
    closePanel();
    await fetchSummary();
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

async function previewJournal(row) {
  loading.value = true;
  error.value = null;
  try {
    previewDoc.value = await previewBankJournalEntry({ bank_transaction_name: row.name, ...jeForm });
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

async function confirmJournal(row) {
  if (!window.confirm(`Create and submit a Journal Entry for ${row.name}? This posts a real, submitted ERPNext document.`)) return;
  loading.value = true;
  error.value = null;
  try {
    await confirmBankJournalEntry({ bank_transaction_name: row.name, ...jeForm });
    successMessage.value = `Journal Entry created and reconciled against ${row.name}.`;
    closePanel();
    await fetchSummary();
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

async function saveReference(row, value) {
  try {
    await updateBankTransactionReference({ bank_transaction_name: row.name, reference_number: value });
    await fetchSummary();
  } catch (caught) {
    error.value = caught;
  }
}

async function autoReconcile() {
  if (!filters.company || !filters.bank_account) return;
  if (!window.confirm("Run ERPNext's automatic best-match reconciliation across all unreconciled transactions for this bank account? This can create clearance-date updates on real records.")) return;
  autoReconciling.value = true;
  error.value = null;
  try {
    await autoReconcileBankTransactions({ ...filters });
    successMessage.value = "Auto reconciliation started. Refresh in a moment to see updated results.";
    window.setTimeout(fetchSummary, 2000);
  } catch (caught) {
    error.value = caught;
  } finally {
    autoReconciling.value = false;
  }
}
</script>

<template>
  <PageContainer>
    <main class="rug-page">
      <nav class="rug-breadcrumbs"><RouterLink to="/home">Home</RouterLink><span>›</span><strong>Bank Reconciliation</strong></nav>
      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Special adapter</span>
          <h1>Bank Reconciliation</h1>
          <p>Match, create or auto-reconcile bank transactions using ERPNext's standard Bank Reconciliation Tool controller. No shadow ledger — every balance and posting comes from ERPNext itself.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Bank reconciliation request failed" :message="error.message" @retry="() => (error = null)" />
      <p v-if="successMessage" class="rug-empty">{{ successMessage }}</p>

      <section class="rug-section-card">
        <div class="rug-form-grid">
          <label>
            Company
            <input v-model="filters.company" list="rug-bank-companies" type="search" autocomplete="off" placeholder="Search company" @input="searchCompany" @focus="searchCompany" />
            <datalist id="rug-bank-companies"><option v-for="c in companyOptions" :key="c.value" :value="c.value">{{ c.label }}</option></datalist>
          </label>
          <label>
            Bank account
            <input v-model="filters.bank_account" list="rug-bank-accounts" type="search" autocomplete="off" placeholder="Search bank account" @input="searchBankAcct" @focus="searchBankAcct" />
            <datalist id="rug-bank-accounts"><option v-for="a in bankAccountOptions" :key="a.value" :value="a.value">{{ a.label }}</option></datalist>
          </label>
          <label>From date<input v-model="filters.bank_statement_from_date" type="date" /></label>
          <label>To date<input v-model="filters.bank_statement_to_date" type="date" /></label>
          <label>Bank statement closing balance<input v-model.number="filters.bank_statement_closing_balance" type="number" step="0.01" /></label>
        </div>
        <div class="rug-banner-actions">
          <button type="button" class="rug-primary" :disabled="!filters.company || !filters.bank_account || loading" @click="fetchSummary">
            {{ loading && !expandedRow ? "Loading…" : loaded ? "Refresh" : "Fetch" }}
          </button>
          <button type="button" class="rug-secondary" :disabled="!filters.company || !filters.bank_account || autoReconciling" @click="autoReconcile">
            {{ autoReconciling ? "Starting…" : "Auto reconcile" }}
          </button>
        </div>
      </section>

      <section v-if="summary" class="rug-list-card">
        <div class="rug-count">
          <span>Ledger balance: <strong>{{ Number(summary.ledger_balance || 0).toLocaleString() }}</strong> {{ summary.account_currency }}</span>
          <span>Statement balance: <strong>{{ Number(summary.bank_statement_closing_balance || 0).toLocaleString() }}</strong></span>
          <span :class="difference === 0 ? '' : 'rug-badge'">Difference: <strong>{{ Number(difference).toLocaleString() }}</strong></span>
        </div>

        <div v-if="!summary.transactions.length" class="rug-empty">No unreconciled bank transactions for this account and date range.</div>
        <div v-else class="rug-table-region">
          <table>
            <thead><tr><th>Date</th><th>Description</th><th>Deposit</th><th>Withdrawal</th><th>Unallocated</th><th>Reference</th><th>Party</th><th></th></tr></thead>
            <tbody>
              <template v-for="row in summary.transactions" :key="row.name">
                <tr>
                  <td>{{ row.date }}</td>
                  <td>{{ row.description }}</td>
                  <td>{{ Number(row.deposit || 0).toLocaleString() }}</td>
                  <td>{{ Number(row.withdrawal || 0).toLocaleString() }}</td>
                  <td>{{ Number(row.unallocated_amount || 0).toLocaleString() }}</td>
                  <td><input type="text" :value="row.reference_number" @change="saveReference(row, $event.target.value)" /></td>
                  <td>{{ row.party || "—" }}</td>
                  <td>
                    <button type="button" @click="openPanel(row, 'match')">Match</button>
                    <button type="button" @click="openPanel(row, 'payment')">+ Payment</button>
                    <button type="button" @click="openPanel(row, 'journal')">+ Journal</button>
                    <button type="button" @click="unreconcile(row)">Unreconcile</button>
                  </td>
                </tr>
                <tr v-if="expandedRow === row.name">
                  <td colspan="8">
                    <div v-if="panelMode === 'match'" class="rug-section-card">
                      <p v-if="matchLoading">Searching for matches…</p>
                      <p v-else-if="!matches.length" class="rug-empty">No candidate Payment Entry, Journal Entry or Invoice found for this amount/party.</p>
                      <div v-else class="rug-table-region">
                        <table>
                          <thead><tr><th></th><th>Type</th><th>Document</th><th>Party</th><th>Amount</th><th>Reference</th></tr></thead>
                          <tbody>
                            <tr v-for="m in matches" :key="`${m.doctype}:${m.name}`">
                              <td><input type="checkbox" :checked="selectedMatchKeys.has(`${m.doctype}:${m.name}`)" @change="toggleMatch(m)" /></td>
                              <td>{{ m.doctype }}</td>
                              <td>{{ m.name }}</td>
                              <td>{{ m.party || "—" }}</td>
                              <td>{{ Number(m.paid_amount || 0).toLocaleString() }}</td>
                              <td>{{ m.reference_no || "—" }}</td>
                            </tr>
                          </tbody>
                        </table>
                        <div class="rug-banner-actions">
                          <button type="button" class="rug-primary" :disabled="!selectedMatches.length || loading" @click="reconcileSelected(row)">
                            {{ loading ? "Reconciling…" : `Reconcile (${selectedMatches.length} selected, ${selectedMatchTotal.toLocaleString()})` }}
                          </button>
                        </div>
                      </div>
                    </div>

                    <div v-else-if="panelMode === 'payment'" class="rug-section-card">
                      <div class="rug-form-grid">
                        <label>Party type
                          <select v-model="peForm.party_type" @change="peForm.party = ''"><option value="Customer">Customer</option><option value="Supplier">Supplier</option><option value="Employee">Employee</option></select>
                        </label>
                        <label>Party
                          <input v-model="peForm.party" list="rug-bank-pe-party" type="search" autocomplete="off" @input="searchPartyFor(peForm)" @focus="searchPartyFor(peForm)" />
                          <datalist id="rug-bank-pe-party"><option v-for="p in partyOptions" :key="p.value" :value="p.value">{{ p.label }}</option></datalist>
                        </label>
                        <label>Reference number<input v-model="peForm.reference_number" type="text" /></label>
                        <label>Reference date<input v-model="peForm.reference_date" type="date" /></label>
                        <label>Posting date<input v-model="peForm.posting_date" type="date" /></label>
                        <label>Mode of payment
                          <input v-model="peForm.mode_of_payment" list="rug-bank-pe-mode" type="search" autocomplete="off" @input="searchMode(peForm)" @focus="searchMode(peForm)" />
                          <datalist id="rug-bank-pe-mode"><option v-for="m in modeOptions" :key="m.value" :value="m.value">{{ m.label }}</option></datalist>
                        </label>
                      </div>
                      <div class="rug-banner-actions">
                        <button type="button" class="rug-secondary" :disabled="!peForm.party || loading" @click="previewPayment(row)">Preview</button>
                        <button type="button" class="rug-primary" :disabled="!previewDoc || loading" @click="confirmPayment(row)">{{ loading ? "Posting…" : "Create + submit" }}</button>
                      </div>
                      <div v-if="previewDoc" class="rug-table-region">
                        <table><tbody>
                          <tr v-for="(value, key) in previewDoc" :key="key"><th>{{ key }}</th><td>{{ value }}</td></tr>
                        </tbody></table>
                      </div>
                    </div>

                    <div v-else-if="panelMode === 'journal'" class="rug-section-card">
                      <div class="rug-form-grid">
                        <label>Journal entry type
                          <select v-model="jeForm.entry_type"><option v-for="t in JE_TYPES" :key="t" :value="t">{{ t }}</option></select>
                        </label>
                        <label>Second account
                          <input v-model="jeForm.second_account" list="rug-bank-je-account" type="search" autocomplete="off" @input="searchJeAccount" @focus="searchJeAccount" />
                          <datalist id="rug-bank-je-account"><option v-for="a in accountOptions" :key="a.value" :value="a.value">{{ a.label }}</option></datalist>
                        </label>
                        <label>Party type (if Receivable/Payable)
                          <select v-model="jeForm.party_type" @change="jeForm.party = ''"><option value="">—</option><option value="Customer">Customer</option><option value="Supplier">Supplier</option></select>
                        </label>
                        <label v-if="jeForm.party_type">Party
                          <input v-model="jeForm.party" list="rug-bank-je-party" type="search" autocomplete="off" @input="searchPartyFor(jeForm)" @focus="searchPartyFor(jeForm)" />
                          <datalist id="rug-bank-je-party"><option v-for="p in partyOptions" :key="p.value" :value="p.value">{{ p.label }}</option></datalist>
                        </label>
                        <label>Reference number<input v-model="jeForm.reference_number" type="text" /></label>
                        <label>Reference date<input v-model="jeForm.reference_date" type="date" /></label>
                        <label>Posting date<input v-model="jeForm.posting_date" type="date" /></label>
                      </div>
                      <div class="rug-banner-actions">
                        <button type="button" class="rug-secondary" :disabled="!jeForm.second_account || loading" @click="previewJournal(row)">Preview</button>
                        <button type="button" class="rug-primary" :disabled="!previewDoc || loading" @click="confirmJournal(row)">{{ loading ? "Posting…" : "Create + submit" }}</button>
                      </div>
                      <p class="rug-empty" v-if="previewDoc">Preview does not run full validation (matches ERPNext's own tool) — balance/party errors surface on create.</p>
                      <div v-if="previewDoc" class="rug-table-region">
                        <table><tbody>
                          <tr v-for="(value, key) in previewDoc" :key="key" v-show="key !== 'accounts'"><th>{{ key }}</th><td>{{ value }}</td></tr>
                        </tbody></table>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </section>

      <section class="rug-warning">
        <strong>Standard ERPNext reconciliation engine</strong>
        <span>This page calls the same get_bank_transactions / get_linked_payments / create_payment_entry_bts / create_journal_entry_bts / reconcile_vouchers / auto_reconcile_vouchers methods the ERPNext Desk client uses. No GL Entry, Bank Transaction allocation or clearance date is computed here directly.</span>
      </section>
    </main>
  </PageContainer>
</template>
