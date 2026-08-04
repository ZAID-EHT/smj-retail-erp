<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getDecisionCentre } from "@/services/accountantDecisions.js";

const data = ref(null);
const error = ref(null);
const loading = ref(true);
const onlyOutstanding = ref(false);
let controller;

const areas = computed(() => (data.value ? Object.entries(data.value.by_area) : []));
const openingStock = computed(() => data.value?.opening_stock || null);
const commission = computed(() => data.value?.commission || null);

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    data.value = await getDecisionCentre("", controller.signal);
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

function statusClass(status) {
  if (status === "Verified" || status === "Implemented") return "is-good";
  if (status === "Approved" || status === "Approved with Changes") return "is-approved";
  if (status === "Rejected") return "is-bad";
  return "is-pending";
}

function visible(items) {
  return onlyOutstanding.value ? items.filter((i) => i.blocking) : items;
}

function money(value) {
  if (value === null || value === undefined) return "—";
  return Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function print() {
  window.print();
}

onBeforeUnmount(() => controller?.abort());
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page decisions-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Admin</RouterLink><span>›</span><strong>Accountant Decisions</strong>
      </nav>

      <header class="rug-banner rug-banner--gold">
        <div>
          <span class="rug-badge">Accountant decisions only</span>
          <h1>Accountant Decision Centre</h1>
          <p v-if="data">{{ data.summary }}</p>
        </div>
        <div class="rug-banner-actions">
          <label class="decisions-toggle">
            <input v-model="onlyOutstanding" type="checkbox" /> Outstanding only
          </label>
          <button class="rug-button rug-button--secondary" type="button" @click="print">Print</button>
          <button class="rug-primary" type="button" :disabled="loading" @click="load">
            {{ loading ? "…" : "Refresh" }}
          </button>
        </div>
      </header>

      <ErrorState v-if="error" title="Unable to load decisions" :message="error.message" @retry="load" />
      <div v-else-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <template v-else-if="data">
        <p class="decisions-boundary">
          This page records what an accountant decided. It posts nothing. No accounting
          document is created, submitted or paid from here.
        </p>

        <section v-for="[area, items] in areas" :key="area" class="rug-section-card">
          <header>
            <div>
              <h2>{{ area }}</h2>
              <p>{{ visible(items).length }} of {{ items.length }} shown</p>
            </div>
          </header>
          <div v-if="!visible(items).length" class="ru-empty">Nothing outstanding in this area.</div>
          <div v-else class="rug-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Question</th><th>Current value</th><th>Options</th>
                  <th>Status</th><th>Accountant answer</th><th>Evidence</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in visible(items)" :key="item.topic">
                  <td>
                    {{ item.question }}
                    <small class="decisions-why">{{ item.why_it_matters }}</small>
                    <small v-if="item.accounting_impact" class="decisions-impact">
                      Impact: {{ item.accounting_impact }}
                    </small>
                    <small v-if="item.risk" class="decisions-risk">
                      Risk if guessed: {{ item.risk }}
                    </small>
                  </td>
                  <td>
                    <template v-if="item.current_value">
                      {{ item.current_value }}
                      <small class="decisions-why">Current policy value — not a decision.</small>
                    </template>
                    <span v-else class="decisions-unset">not set</span>
                  </td>
                  <td class="decisions-proposal">
                    <ul class="decisions-options">
                      <li v-for="option in item.options" :key="option">{{ option }}</li>
                    </ul>
                  </td>
                  <td>
                    <span class="decisions-pill" :class="statusClass(item.status)">{{ item.status }}</span>
                    <small class="decisions-why">{{ item.verification_state }}</small>
                  </td>
                  <td>
                    <template v-if="item.accountant_answer">
                      <strong>{{ item.accountant_answer }}</strong>
                      <small v-if="item.decision">
                        {{ item.decision.accountant_name }} · {{ item.decision.review_date }}
                      </small>
                      <small v-if="item.effective_date">Effective {{ item.effective_date }}</small>
                    </template>
                    <span v-else class="decisions-unset">no decision recorded</span>
                  </td>
                  <td>
                    <span v-if="item.evidence">{{ item.evidence }}</span>
                    <span v-else class="decisions-unset">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="openingStock" class="rug-section-card">
          <header><div><h2>Opening stock correction</h2><p>Measured position, read-only.</p></div></header>
          <div class="rug-table-wrap">
            <table>
              <tbody>
                <tr><th>Root cause</th><td>{{ openingStock.root_cause }}</td></tr>
                <tr><th>Amount</th><td>{{ money(openingStock.expected_amount) }}</td></tr>
                <tr><th>Debit</th><td>{{ openingStock.debit_account_role }}</td></tr>
                <tr><th>Credit</th><td>{{ openingStock.credit_account_role }}</td></tr>
                <tr><th>Proposed posting date</th><td>{{ openingStock.opening_date }}</td></tr>
                <tr v-if="openingStock.measured"><th>Profit before</th><td>{{ money(openingStock.measured.totals.profit) }}</td></tr>
                <tr v-if="openingStock.measured"><th>Trial balance</th><td>{{ openingStock.measured.totals.balanced ? "Balanced" : "Not balanced" }}</td></tr>
                <tr><th>Stock quantity impact</th><td>{{ openingStock.stock_quantity_impact }}</td></tr>
                <tr><th>Stock valuation impact</th><td>{{ openingStock.stock_valuation_impact }}</td></tr>
                <tr><th>Posting status</th><td><strong>{{ openingStock.posting_status }}</strong></td></tr>
                <tr><th>How it gets posted</th><td>{{ openingStock.submission_route }}</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="commission" class="rug-section-card">
          <header><div><h2>Commission accounting</h2><p>Policy readiness and the posting boundary.</p></div></header>
          <p class="decisions-blocked">{{ commission.posting_boundary }}</p>
          <div class="rug-table-wrap">
            <table>
              <thead><tr><th>Policy</th><th>Status</th><th>Trigger</th><th>Basis</th><th>Expense a/c</th><th>Payable a/c</th></tr></thead>
              <tbody>
                <tr v-if="!commission.policies.length"><td colspan="6">No commission policy exists yet.</td></tr>
                <tr v-for="policy in commission.policies" :key="policy.name">
                  <td>{{ policy.policy_name }}</td>
                  <td>{{ policy.status }}</td>
                  <td>{{ policy.earning_trigger || "— not chosen" }}</td>
                  <td>{{ policy.commission_basis || "— not chosen" }}</td>
                  <td>{{ policy.commission_expense_account || "— not chosen" }}</td>
                  <td>{{ policy.commission_payable_account || "— not chosen" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.decisions-toggle{display:inline-flex;align-items:center;gap:.4rem;font-weight:700;color:#fff}
.decisions-boundary{margin:0 0 1rem;padding:.75rem 1rem;border-radius:.6rem;font-weight:700;background:var(--ref-warning-background);color:var(--ref-warning,#8a6d00)}
.decisions-blocked{margin:0 0 1rem;font-weight:700;color:var(--ref-danger)}
.decisions-pill{display:inline-flex;padding:.25rem .6rem;border-radius:999px;font-weight:800;font-size:.82rem;background:var(--ref-border-colour);white-space:nowrap}
.decisions-pill.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.decisions-pill.is-approved{background:var(--ref-success-background);color:var(--ref-success)}
.decisions-pill.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
.decisions-pill.is-pending{background:var(--ref-warning-background);color:var(--ref-warning,#8a6d00)}
.decisions-why{display:block;color:var(--ref-secondary-text);font-weight:500}
.decisions-impact{display:block;color:var(--ref-secondary-text);font-weight:500;margin-top:.25rem}
.decisions-risk{display:block;color:var(--ref-danger);font-weight:600;margin-top:.25rem}
.decisions-unset{color:var(--ref-secondary-text);font-style:italic}
.decisions-options{margin:0;padding-left:1.1rem}
.decisions-options li{font-size:.85rem}
.decisions-proposal{max-width:16rem}
</style>
