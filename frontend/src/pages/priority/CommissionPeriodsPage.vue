<script setup>
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import {
  approveCommissionAdjustment, approveCommissionPeriod, cancelCommissionPeriod,
  createCommissionPeriod, getCommissionPeriod, getPeriodApprovalChecks,
  listCommissionPeriods, listCommissionStatements, prepareCommissionPayout,
  prepareCommissionPeriod, rejectCommissionAdjustment, reopenCommissionPeriod,
  requestCommissionAdjustment, resolveCommissionException, reviewCommissionPeriod,
  submitPeriodForReview, validateCommissionPayout,
} from "@/services/commissionAdmin.js";
import { listCommissionPolicies } from "@/services/commissionAdmin.js";

const route = useRoute();
const router = useRouter();
const opened = computed(() => route.query.period || "");

const list = ref(null);
const detail = ref(null);
const statements = ref(null);
const payout = ref(null);
const checks = ref(null);
const policies = ref([]);
const tab = ref("rows");
const loading = ref(false);
const busy = ref("");
const denied = ref(false);
const error = ref("");
const notice = ref("");

const draft = reactive({ company: "", policy: "", from_date: "", to_date: "" });
const adjustment = reactive({ sales_person: "", adjustment_type: "Bonus", amount: 0, reason: "" });

// A late response for a period the user has already navigated away from must
// never overwrite what is on screen.
let token = 0;

async function loadList() {
  const mine = ++token;
  loading.value = true;
  error.value = "";
  try {
    const [periods, policyList] = await Promise.all([
      listCommissionPeriods({}), listCommissionPolicies({ status: "Active" }),
    ]);
    if (mine !== token) return;
    list.value = periods;
    policies.value = policyList.rows || [];
    if (!draft.company && periods.companies?.length) draft.company = periods.companies[0];
  } catch (caught) {
    if (mine !== token) return;
    if (caught?.response?.status === 403) denied.value = true;
    else error.value = caught?.message || "Commission periods could not be loaded.";
  } finally {
    if (mine === token) loading.value = false;
  }
}

async function loadDetail(name) {
  const mine = ++token;
  loading.value = true;
  error.value = "";
  statements.value = null;
  payout.value = null;
  checks.value = null;
  try {
    const data = await getCommissionPeriod(name);
    if (mine !== token) return;
    detail.value = data;
  } catch (caught) {
    if (mine !== token) return;
    error.value = caught?.message || "That period could not be loaded.";
  } finally {
    if (mine === token) loading.value = false;
  }
}

function refresh() {
  if (opened.value) loadDetail(opened.value);
  else loadList();
}
refresh();

function open(name) { router.push({ path: route.path, query: { period: name } }); }
function back() { router.push({ path: route.path }); }

async function act(kind, fn, successMessage) {
  busy.value = kind;
  error.value = "";
  try {
    await fn();
    notice.value = successMessage;
    await loadDetail(opened.value);
  } catch (caught) {
    error.value = caught?.message || "The request could not be completed.";
  } finally {
    busy.value = "";
  }
}

const create = () => act("create", async () => {
  const result = await createCommissionPeriod({ ...draft });
  open(result.name);
}, "Period opened.");

const prepare = () => act("prepare", () => prepareCommissionPeriod(opened.value), "Period prepared.");
const forReview = () => act("review", () => submitPeriodForReview(opened.value), "Sent for review.");
const review = () => act("reviewed", () => reviewCommissionPeriod(opened.value), "Reviewed.");
const approve = () => act("approve", () => approveCommissionPeriod(opened.value), "Approved.");

function reopen() {
  const reason = window.prompt("Why is this period being reopened?");
  if (!reason) return;
  act("reopen", () => reopenCommissionPeriod(opened.value, reason), "Reopened.");
}
function cancel() {
  const reason = window.prompt("Why is this period being cancelled?");
  if (!reason) return;
  act("cancel", () => cancelCommissionPeriod(opened.value, reason), "Cancelled.");
}
function resolve(row, resolution) {
  const note = window.prompt(`Note for ${resolution.toLowerCase()}ing this exception`) || "";
  if (resolution === "Waived" && !note) return;
  act("exception", () => resolveCommissionException(opened.value, row.idx, resolution, note),
    "Exception updated.");
}

async function loadChecks() {
  busy.value = "checks";
  try {
    checks.value = await getPeriodApprovalChecks(opened.value);
  } catch (caught) {
    error.value = caught?.message || "The checks could not be loaded.";
  } finally {
    busy.value = "";
  }
}

async function loadStatements() {
  busy.value = "statements";
  try {
    statements.value = await listCommissionStatements({ period: opened.value });
  } catch (caught) {
    error.value = caught?.message || "Statements could not be loaded.";
  } finally {
    busy.value = "";
  }
}

async function buildPayout() {
  busy.value = "payout";
  error.value = "";
  try {
    const prepared = await prepareCommissionPayout(opened.value);
    payout.value = (await validateCommissionPayout(prepared.name)).payout;
    await loadDetail(opened.value);
  } catch (caught) {
    error.value = caught?.message || "The payout could not be prepared.";
  } finally {
    busy.value = "";
  }
}

const addAdjustment = () => act("adjustment", async () => {
  await requestCommissionAdjustment({ period: opened.value, ...adjustment });
  adjustment.amount = 0;
  adjustment.reason = "";
}, "Adjustment requested.");

const decide = (name, approveIt) => act("decide", () => (approveIt
  ? approveCommissionAdjustment(name)
  : rejectCommissionAdjustment(name, window.prompt("Why is it rejected?") || "Rejected")),
"Adjustment updated.");

const period = computed(() => detail.value?.period);
const members = computed(() => {
  const seen = new Map();
  (period.value?.details || []).forEach((r) => seen.set(r.sales_person, r.sales_person_name));
  return [...seen].map(([value, label]) => ({ value, label }));
});

function money(value) {
  return Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function pct(value) {
  const n = Number(value || 0);
  return `${Number.isInteger(n) ? n : n.toFixed(2)}%`;
}
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="denied" />
    <main v-else class="rug-page smj-periods">
      <header class="rug-banner rug-banner--green">
        <div>
          <span class="rug-badge">Sales</span>
          <h1>{{ opened ? `Commission Period ${opened}` : "Commission Periods" }}</h1>
          <p>Prepare, review and approve a closing. Payout preparation stops before posting.</p>
        </div>
        <div class="rug-banner-actions">
          <button v-if="opened" type="button" @click="back">Back to list</button>
          <button v-else type="button" @click="loadList">Refresh</button>
        </div>
      </header>

      <p v-if="notice" class="smj-sales-notice" role="status">{{ notice }}</p>
      <p v-if="error" class="smj-team-card__warning" role="alert">{{ error }}</p>

      <!-- ------------------------------- LIST ------------------------------- -->
      <template v-if="!opened">
        <section v-if="list?.can_prepare" class="rug-section-card">
          <header><h2>Open a period</h2></header>
          <div class="rug-form-grid">
            <label><span>Company</span>
              <select v-model="draft.company">
                <option v-for="c in list.companies || []" :key="c" :value="c">{{ c }}</option>
              </select>
            </label>
            <label><span>Policy</span>
              <select v-model="draft.policy" data-test="period-policy">
                <option value="">Select an active policy</option>
                <option v-for="p in policies" :key="p.name" :value="p.name">{{ p.policy_name }}</option>
              </select>
            </label>
            <label><span>From</span><input v-model="draft.from_date" type="date" /></label>
            <label><span>To</span><input v-model="draft.to_date" type="date" /></label>
          </div>
          <p v-if="!policies.length" class="smj-team-card__warning">
            No active commission policy exists, so no period can be opened.
          </p>
          <div class="smj-form-actions">
            <button type="button" class="rug-primary" data-test="period-create"
                    :disabled="busy === 'create' || !draft.policy" @click="create">
              Open Period
            </button>
          </div>
        </section>

        <section class="rug-section-card">
          <div v-if="loading" class="smj-team-card__state" role="status">Loading periods…</div>
          <div v-else-if="!list?.rows?.length" class="smj-team-card__state">
            No commission period has been opened yet.
          </div>
          <div v-else class="smj-table-scroll">
            <table class="rug-table" data-test="period-table">
              <thead>
                <tr>
                  <th>Period</th><th>Company</th><th>From</th><th>To</th><th>Status</th>
                  <th class="is-num">Gross</th><th class="is-num">Reversals</th>
                  <th class="is-num">Net Payable</th><th class="is-num">Paid</th>
                  <th class="is-num">Outstanding</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in list.rows" :key="row.name">
                  <td>{{ row.name }}</td><td>{{ row.company }}</td>
                  <td>{{ row.from_date }}</td><td>{{ row.to_date }}</td>
                  <td><span class="smj-pill" :data-status="row.status">{{ row.status }}</span></td>
                  <td class="is-num">{{ money(row.gross_commission) }}</td>
                  <td class="is-num">{{ money(row.reversals) }}</td>
                  <td class="is-num"><strong>{{ money(row.net_payable) }}</strong></td>
                  <td class="is-num">{{ money(row.paid_amount) }}</td>
                  <td class="is-num">{{ money(row.outstanding) }}</td>
                  <td><button type="button" @click="open(row.name)">Open</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <!-- ------------------------------ DETAIL ------------------------------ -->
      <template v-else-if="period">
        <section class="rug-section-card smj-commissions__totals" data-test="period-totals">
          <span>Status <strong>{{ period.status }}</strong></span>
          <span>Gross <strong>{{ money(period.gross_commission) }}</strong></span>
          <span>Reversals <strong>{{ money(period.reversals) }}</strong></span>
          <span>Withholding <strong>{{ money(period.withholding) }}</strong></span>
          <span>Adjustments <strong>{{ money(period.adjustments) }}</strong></span>
          <span>Net payable <strong data-test="period-net">{{ money(period.net_payable) }}</strong></span>
          <span>Paid <strong>{{ money(period.paid_amount) }}</strong></span>
          <span>Outstanding <strong>{{ money(period.outstanding) }}</strong></span>
        </section>

        <section class="rug-section-card">
          <div class="smj-form-actions">
            <button v-if="detail.can_prepare" type="button" data-test="period-prepare"
                    :disabled="busy === 'prepare'" @click="prepare">Prepare</button>
            <button v-if="period.status === 'Prepared' || period.status === 'Reopened'"
                    type="button" @click="forReview">Send for review</button>
            <button v-if="period.status === 'Under Review' && detail.can_review" type="button"
                    @click="review">Mark reviewed</button>
            <button v-if="period.status === 'Under Review' && detail.can_approve" type="button"
                    class="rug-primary" data-test="period-approve" @click="approve">Approve</button>
            <button v-if="period.status === 'Approved' && detail.can_approve" type="button"
                    @click="reopen">Reopen</button>
            <button v-if="detail.can_approve && period.status !== 'Cancelled'" type="button"
                    @click="cancel">Cancel</button>
            <button type="button" data-test="period-checks" @click="loadChecks">Approval checks</button>
          </div>
          <p v-if="detail.blocking_exceptions" class="smj-team-card__warning"
             data-test="period-blocked">
            {{ detail.blocking_exceptions }} blocking exception(s) must be resolved before approval.
          </p>
        </section>

        <section v-if="checks" class="rug-section-card">
          <header><h2>Approval checks</h2></header>
          <ul class="smj-issue-list" data-test="period-check-list">
            <li v-for="(c, i) in checks.checks" :key="i" :data-severity="c.passed ? 'ok' : 'Blocking'">
              <strong>{{ c.passed ? "PASS" : "FAIL" }}</strong>
              <span>{{ c.check }}</span>
              <em>{{ c.detail }}</em>
            </li>
          </ul>
        </section>

        <nav class="smj-tabs" role="tablist">
          <button type="button" :aria-selected="tab === 'rows'" @click="tab = 'rows'">
            Rows ({{ period.details.length }})
          </button>
          <button type="button" :aria-selected="tab === 'exceptions'" @click="tab = 'exceptions'">
            Exceptions ({{ period.exceptions.length }})
          </button>
          <button type="button" :aria-selected="tab === 'adjustments'" @click="tab = 'adjustments'">
            Adjustments ({{ detail.adjustments.length }})
          </button>
          <button type="button" :aria-selected="tab === 'statements'"
                  @click="tab = 'statements'; loadStatements()">Statements</button>
          <button type="button" :aria-selected="tab === 'payout'"
                  @click="tab = 'payout'">Payout</button>
        </nav>

        <section v-if="tab === 'rows'" class="rug-section-card">
          <div v-if="!period.details.length" class="smj-team-card__state">
            Nothing prepared yet.
          </div>
          <div v-else class="smj-table-scroll">
            <table class="rug-table smj-commissions__table" data-test="period-rows">
              <thead>
                <tr>
                  <th>Date</th><th>Member</th><th>Role</th><th>Customer</th><th>Invoice</th>
                  <th class="is-num">Basis</th><th class="is-num">Rate</th>
                  <th class="is-num">Alloc</th><th class="is-num">Gross</th>
                  <th class="is-num">Reversal</th><th class="is-num">Withheld</th>
                  <th class="is-num">Adjust</th><th class="is-num">Net</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(r, i) in period.details" :key="i" :class="r.is_return && 'is-return'">
                  <td>{{ r.eligibility_date }}</td>
                  <td>{{ r.sales_person_name }}</td><td>{{ r.team_role }}</td>
                  <td>{{ r.customer }}</td><td>{{ r.sales_invoice }}</td>
                  <td class="is-num">{{ money(r.eligible_basis) }}</td>
                  <td class="is-num">{{ pct(r.commission_rate) }}</td>
                  <td class="is-num">{{ pct(r.allocation_percentage) }}</td>
                  <td class="is-num">{{ money(r.gross_commission) }}</td>
                  <td class="is-num">{{ money(r.return_reversal) }}</td>
                  <td class="is-num">{{ money(r.withholding) }}</td>
                  <td class="is-num">{{ money(r.adjustment) }}</td>
                  <td class="is-num"><strong>{{ money(r.net_commission) }}</strong></td>
                  <td>{{ r.row_status }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="tab === 'exceptions'" class="rug-section-card">
          <div v-if="!period.exceptions.length" class="smj-team-card__state">
            No exceptions. Nothing is being silently skipped.
          </div>
          <div v-else class="smj-table-scroll">
            <table class="rug-table" data-test="period-exceptions">
              <thead>
                <tr><th>Exception</th><th>Severity</th><th>Source</th><th>Owner</th>
                  <th>Action</th><th>Resolution</th><th></th></tr>
              </thead>
              <tbody>
                <tr v-for="row in period.exceptions" :key="row.idx">
                  <td>{{ row.exception_type }}</td>
                  <td><span class="smj-pill" :data-status="row.severity">{{ row.severity }}</span></td>
                  <td>{{ row.source_name }}</td>
                  <td>{{ row.owner_role }}</td>
                  <td>{{ row.recommended_action }}</td>
                  <td>{{ row.resolution_status }}<small v-if="row.resolved_by"> — {{ row.resolved_by }}</small></td>
                  <td>
                    <button v-if="row.resolution_status === 'Open'" type="button"
                            @click="resolve(row, 'Resolved')">Resolve</button>
                    <button v-if="row.resolution_status === 'Open'" type="button"
                            @click="resolve(row, 'Waived')">Waive</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="tab === 'adjustments'" class="rug-section-card">
          <header><h2>Adjustments</h2><p>Never touches an invoice.</p></header>
          <div v-if="detail.can_request_adjustment" class="rug-form-grid">
            <label><span>Member</span>
              <select v-model="adjustment.sales_person" data-test="adjustment-member">
                <option value="">Select</option>
                <option v-for="m in members" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </label>
            <label><span>Type</span>
              <select v-model="adjustment.adjustment_type">
                <option>Bonus</option><option>Deduction</option><option>Correction</option>
                <option>Carry Forward</option><option>Return Clawback</option><option>Rounding</option>
              </select>
            </label>
            <label><span>Amount</span>
              <input v-model.number="adjustment.amount" type="number" step="any" />
            </label>
            <label><span>Reason</span><input v-model="adjustment.reason" /></label>
          </div>
          <div v-if="detail.can_request_adjustment" class="smj-form-actions">
            <button type="button" data-test="adjustment-request"
                    :disabled="!adjustment.sales_person || !adjustment.reason"
                    @click="addAdjustment">Request adjustment</button>
          </div>
          <div v-if="detail.adjustments.length" class="smj-table-scroll">
            <table class="rug-table" data-test="adjustment-table">
              <thead><tr><th>Member</th><th>Type</th><th class="is-num">Amount</th><th>Reason</th>
                <th>Status</th><th>Requested By</th><th></th></tr></thead>
              <tbody>
                <tr v-for="row in detail.adjustments" :key="row.name">
                  <td>{{ row.sales_person }}</td><td>{{ row.adjustment_type }}</td>
                  <td class="is-num">{{ money(row.amount) }}</td><td>{{ row.reason }}</td>
                  <td>{{ row.status }}</td><td>{{ row.requested_by }}</td>
                  <td>
                    <template v-if="row.status === 'Requested' && detail.can_approve_adjustment">
                      <button type="button" @click="decide(row.name, true)">Approve</button>
                      <button type="button" @click="decide(row.name, false)">Reject</button>
                    </template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="tab === 'statements'" class="rug-section-card">
          <div v-if="busy === 'statements'" class="smj-team-card__state" role="status">Loading…</div>
          <div v-else-if="!statements?.statements?.length" class="smj-team-card__state">
            No statements for this period.
          </div>
          <template v-else>
            <p v-if="statements.restricted" class="smj-commissions__scope">
              You are seeing your own statement only.
            </p>
            <article v-for="s in statements.statements" :key="s.sales_person"
                     class="smj-statement" data-test="statement">
              <header>
                <strong>{{ s.sales_person_name }}</strong>
                <span>{{ s.team_role }} — {{ s.sales_team }}</span>
              </header>
              <div class="smj-commissions__totals">
                <span>Opening carry-forward <strong>{{ money(s.opening_carry_forward) }}</strong></span>
                <span>Gross <strong>{{ money(s.gross_commission) }}</strong></span>
                <span>Reversals <strong>{{ money(s.return_reversal) }}</strong></span>
                <span>Withholding <strong>{{ money(s.withholding) }}</strong></span>
                <span>Adjustments <strong>{{ money(s.adjustments) }}</strong></span>
                <span>Net payable <strong>{{ money(s.net_payable) }}</strong></span>
                <span>Paid <strong>{{ money(s.paid_amount) }}</strong></span>
                <span>Outstanding <strong>{{ money(s.outstanding) }}</strong></span>
                <span>Closing carry-forward <strong>{{ money(s.closing_carry_forward) }}</strong></span>
              </div>
              <div class="smj-table-scroll">
                <table class="rug-table">
                  <thead><tr><th>Date</th><th>Customer</th><th>Invoice</th>
                    <th class="is-num">Base</th><th class="is-num">Rate</th>
                    <th class="is-num">Alloc</th><th class="is-num">Gross</th>
                    <th class="is-num">Reversal</th><th class="is-num">Net</th></tr></thead>
                  <tbody>
                    <tr v-for="(t, i) in s.transactions" :key="i">
                      <td>{{ t.date }}</td><td>{{ t.customer }}</td><td>{{ t.sales_invoice }}</td>
                      <td class="is-num">{{ money(t.eligible_basis) }}</td>
                      <td class="is-num">{{ pct(t.commission_rate) }}</td>
                      <td class="is-num">{{ pct(t.allocation_percentage) }}</td>
                      <td class="is-num">{{ money(t.gross_commission) }}</td>
                      <td class="is-num">{{ money(t.return_reversal) }}</td>
                      <td class="is-num">{{ money(t.net_commission) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </article>
          </template>
        </section>

        <section v-if="tab === 'payout'" class="rug-section-card">
          <header>
            <h2>Payout preparation</h2>
            <p>Grouping, validation and a proposed accounting entry. Nothing is posted.</p>
          </header>
          <div class="smj-form-actions">
            <button type="button" class="rug-primary" data-test="payout-prepare"
                    :disabled="busy === 'payout' || period.status === 'Draft'"
                    @click="buildPayout">Prepare payout</button>
          </div>
          <template v-if="payout">
            <p class="smj-team-card__warning" data-test="payout-blocked">
              {{ payout.posting_blocked_reason }}
            </p>
            <div class="smj-table-scroll">
              <table class="rug-table" data-test="payout-lines">
                <thead><tr><th>Member</th><th>Party</th><th class="is-num">Gross</th>
                  <th class="is-num">Withheld</th><th class="is-num">Adjust</th>
                  <th class="is-num">Carry In</th><th class="is-num">Net</th>
                  <th class="is-num">Carry Out</th><th>Validation</th></tr></thead>
                <tbody>
                  <tr v-for="(l, i) in payout.lines" :key="i">
                    <td>{{ l.sales_person_name }}</td>
                    <td>{{ l.party || "—" }}</td>
                    <td class="is-num">{{ money(l.gross_commission) }}</td>
                    <td class="is-num">{{ money(l.withholding) }}</td>
                    <td class="is-num">{{ money(l.adjustments) }}</td>
                    <td class="is-num">{{ money(l.carry_forward_in) }}</td>
                    <td class="is-num"><strong>{{ money(l.net_payable) }}</strong></td>
                    <td class="is-num">{{ money(l.carry_forward_out) }}</td>
                    <td>
                      <span class="smj-pill" :data-status="l.validation_status">
                        {{ l.validation_status }}</span>
                      <small>{{ l.validation_note }}</small>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <h3>Proposed accounting</h3>
            <div class="smj-commissions__totals" data-test="accounting-preview">
              <span>Document <strong>{{ payout.accounting_preview.proposed_document_type || "not chosen" }}</strong></span>
              <span>Entries <strong>{{ payout.accounting_preview.entry_count }}</strong></span>
              <span>Total <strong>{{ money(payout.accounting_preview.total) }}</strong></span>
              <span>Would post <strong>{{ payout.accounting_preview.would_post ? "yes" : "no" }}</strong></span>
            </div>
            <div v-if="payout.accounting_preview.entries?.length" class="smj-table-scroll">
              <table class="rug-table">
                <thead><tr><th>Party</th><th>Debit</th><th>Credit</th>
                  <th class="is-num">Amount</th><th>Cost Center</th></tr></thead>
                <tbody>
                  <tr v-for="(e, i) in payout.accounting_preview.entries" :key="i">
                    <td>{{ e.party || "—" }}</td><td>{{ e.debit_account || "—" }}</td>
                    <td>{{ e.credit_account || "—" }}</td>
                    <td class="is-num">{{ money(e.amount) }}</td>
                    <td>{{ e.cost_center || "—" }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </section>
      </template>
    </main>
  </PageContainer>
</template>
