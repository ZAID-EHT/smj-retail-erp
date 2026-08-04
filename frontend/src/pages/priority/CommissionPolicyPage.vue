<script setup>
import { computed, reactive, ref } from "vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import {
  approveCommissionPolicy, getCommissionPolicy, listCommissionPolicies,
  saveCommissionPolicy, simulateCommissionPolicy, suspendCommissionPolicy,
  validateCommissionPolicy,
} from "@/services/commissionAdmin.js";

const list = ref(null);
const form = reactive({ policy: null, options: {}, isNew: true, canManage: false, canApprove: false });
const editing = ref("");
const loading = ref(false);
const saving = ref(false);
const denied = ref(false);
const error = ref("");
const notice = ref("");
const validation = ref(null);
const simulation = ref(null);
const busy = ref("");

async function loadList() {
  loading.value = true;
  error.value = "";
  try {
    list.value = await listCommissionPolicies({});
  } catch (caught) {
    if (caught?.response?.status === 403) denied.value = true;
    else error.value = caught?.message || "Commission policies could not be loaded.";
  } finally {
    loading.value = false;
  }
}

async function open(name) {
  editing.value = name || "new";
  loading.value = true;
  error.value = "";
  validation.value = null;
  simulation.value = null;
  try {
    const result = await getCommissionPolicy(name === "new" ? "" : name);
    form.policy = result.policy;
    form.options = result.options || {};
    form.isNew = result.is_new;
    form.canManage = result.can_manage;
    form.canApprove = result.can_approve;
  } catch (caught) {
    error.value = caught?.message || "That policy could not be loaded.";
  } finally {
    loading.value = false;
  }
}

function backToList() {
  editing.value = "";
  form.policy = null;
  loadList();
}

async function save() {
  saving.value = true;
  error.value = "";
  try {
    const result = await saveCommissionPolicy(form.policy, form.isNew ? "" : form.policy.name);
    form.policy = result.policy;
    form.isNew = false;
    editing.value = result.name;
    notice.value = `Saved ${result.name}.`;
  } catch (caught) {
    error.value = caught?.message || "The policy could not be saved.";
  } finally {
    saving.value = false;
  }
}

async function run(kind) {
  busy.value = kind;
  error.value = "";
  try {
    if (kind === "validate") validation.value = await validateCommissionPolicy(form.policy.name);
    if (kind === "simulate") simulation.value = await simulateCommissionPolicy({ name: form.policy.name });
    if (kind === "approve") {
      const result = await approveCommissionPolicy(form.policy.name);
      form.policy = result.policy;
      notice.value = "Policy approved.";
    }
    if (kind === "suspend") {
      const reason = window.prompt("Why is this policy being suspended?");
      if (!reason) return;
      const result = await suspendCommissionPolicy(form.policy.name, reason);
      form.policy = result.policy;
      notice.value = "Policy suspended.";
    }
  } catch (caught) {
    error.value = caught?.message || "The request could not be completed.";
  } finally {
    busy.value = "";
  }
}

const missingForPosting = computed(() => form.policy?.missing_for_posting || []);
const missingForCalc = computed(() => form.policy?.missing_for_calculation || []);

function money(value) {
  return Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

loadList();
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="denied" />
    <main v-else class="rug-page smj-policy">
      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Admin</span>
          <h1>Commission Policy</h1>
          <p>
            When commission is earned, on what, at what rate, and into which accounts.
            Nothing here has a default — an unanswered question keeps the policy incomplete.
          </p>
        </div>
        <div class="rug-banner-actions">
          <button v-if="!editing && list?.can_manage" type="button" class="rug-primary"
                  data-test="policy-new" @click="open('new')">New Policy</button>
          <button v-if="editing" type="button" @click="backToList">Back to list</button>
        </div>
      </header>

      <p v-if="notice" class="smj-sales-notice" role="status">{{ notice }}</p>
      <p v-if="error" class="smj-team-card__warning" role="alert">{{ error }}</p>

      <!-- ------------------------------- LIST ------------------------------- -->
      <section v-if="!editing" class="rug-section-card">
        <div v-if="loading" class="smj-team-card__state" role="status">Loading policies…</div>
        <div v-else-if="!list?.rows?.length" class="smj-team-card__state">
          No commission policy exists yet. Commission is calculated and reported, but
          nothing can be paid until a policy states the terms.
        </div>
        <div v-else class="smj-table-scroll">
          <table class="rug-table" data-test="policy-table">
            <thead>
              <tr>
                <th>Policy</th><th>Company</th><th>Status</th><th>Earned On</th>
                <th>Basis</th><th>Rate Source</th><th>Can Pay</th><th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in list.rows" :key="row.name">
                <td>{{ row.policy_name }}</td>
                <td>{{ row.company }}</td>
                <td><span class="smj-pill" :data-status="row.status">{{ row.status }}</span></td>
                <td>{{ row.earning_trigger || "—" }}</td>
                <td>{{ row.commission_basis || "—" }}</td>
                <td>{{ row.rate_source || "—" }}</td>
                <td>{{ row.may_post ? "Yes" : "No" }}</td>
                <td><button type="button" @click="open(row.name)">Open</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ------------------------------- FORM ------------------------------- -->
      <template v-else-if="form.policy">
        <section class="rug-section-card">
          <header><h2>Terms</h2></header>
          <div class="rug-form-grid">
            <label><span>Policy Name</span>
              <input v-model="form.policy.policy_name" :disabled="!form.canManage" />
            </label>
            <label><span>Company</span>
              <select v-model="form.policy.company" :disabled="!form.canManage">
                <option value="">Select</option>
                <option v-for="c in form.options.companies || []" :key="c" :value="c">{{ c }}</option>
              </select>
            </label>
            <label><span>Effective From</span>
              <input v-model="form.policy.effective_from" type="date" :disabled="!form.canManage" />
            </label>
            <label><span>Effective To</span>
              <input v-model="form.policy.effective_to" type="date" :disabled="!form.canManage" />
            </label>
            <label><span>Commission Is Earned On</span>
              <select v-model="form.policy.earning_trigger" :disabled="!form.canManage"
                      data-test="policy-trigger">
                <option value="">Not chosen</option>
                <option v-for="o in form.options.earning_trigger || []" :key="o" :value="o">{{ o }}</option>
              </select>
            </label>
            <label><span>Commission Basis</span>
              <select v-model="form.policy.commission_basis" :disabled="!form.canManage">
                <option value="">Not chosen</option>
                <option v-for="o in form.options.commission_basis || []" :key="o" :value="o">{{ o }}</option>
              </select>
            </label>
            <label><span>Rate Source</span>
              <select v-model="form.policy.rate_source" :disabled="!form.canManage">
                <option value="">Not chosen</option>
                <option v-for="o in form.options.rate_source || []" :key="o" :value="o">{{ o }}</option>
              </select>
            </label>
            <label v-if="form.policy.rate_source === 'Fixed Policy Rate'"><span>Fixed Rate %</span>
              <input v-model.number="form.policy.fixed_rate" type="number" step="any"
                     :disabled="!form.canManage" />
            </label>
            <label><span>Payout Cycle</span>
              <select v-model="form.policy.payout_cycle" :disabled="!form.canManage">
                <option value="">Not chosen</option>
                <option v-for="o in form.options.payout_cycle || []" :key="o" :value="o">{{ o }}</option>
              </select>
            </label>
            <label><span>Withholding</span>
              <select v-model="form.policy.withholding_mode" :disabled="!form.canManage">
                <option value="">Not chosen</option>
                <option v-for="o in form.options.withholding_mode || []" :key="o" :value="o">{{ o }}</option>
              </select>
            </label>
            <label v-if="form.policy.withholding_mode === 'Fixed Percentage'"><span>Withholding %</span>
              <input v-model.number="form.policy.withholding_percentage" type="number" step="any"
                     :disabled="!form.canManage" />
            </label>
            <label><span>Returns and Clawbacks</span>
              <select v-model="form.policy.returns_rule" :disabled="!form.canManage">
                <option value="">Not chosen</option>
                <option v-for="o in form.options.returns_rule || []" :key="o" :value="o">{{ o }}</option>
              </select>
            </label>
          </div>
        </section>

        <section class="rug-section-card">
          <header>
            <h2>Accounting</h2>
            <p>Required before anything can be posted. Not required to calculate.</p>
          </header>
          <div class="rug-form-grid">
            <label><span>Accounting Document</span>
              <select v-model="form.policy.accounting_document_type" :disabled="!form.canManage">
                <option value="">Not chosen</option>
                <option v-for="o in form.options.accounting_document_type || []" :key="o" :value="o">{{ o }}</option>
              </select>
            </label>
            <label><span>Payee Party Type</span>
              <select v-model="form.policy.payee_party_type" :disabled="!form.canManage">
                <option value="">Not chosen</option>
                <option v-for="o in form.options.payee_party_type || []" :key="o" :value="o">{{ o }}</option>
              </select>
            </label>
            <label><span>Commission Expense Account</span>
              <input v-model="form.policy.commission_expense_account" :disabled="!form.canManage" />
            </label>
            <label><span>Commission Payable Account</span>
              <input v-model="form.policy.commission_payable_account" :disabled="!form.canManage" />
            </label>
            <label><span>Cost Center</span>
              <input v-model="form.policy.cost_center" :disabled="!form.canManage" />
            </label>
            <label><span>Accountant Approval Reference</span>
              <input v-model="form.policy.accountant_approval_reference" :disabled="!form.canManage" />
            </label>
          </div>

          <p v-if="missingForCalc.length" class="smj-team-card__warning" data-test="policy-missing">
            Still unanswered: {{ missingForCalc.join(", ") }}. The policy cannot be approved.
          </p>
          <p v-else-if="missingForPosting.length" class="smj-team-card__warning"
             data-test="policy-posting-blocked">
            Commission can be calculated and reported. <strong>Posting is blocked</strong>
            until an accountant settles: {{ missingForPosting.join(", ") }}.
          </p>
        </section>

        <section class="rug-section-card">
          <header><h2>Thresholds</h2></header>
          <div class="rug-form-grid">
            <label><span>Minimum Payout Amount</span>
              <input v-model.number="form.policy.minimum_payout_amount" type="number" step="any"
                     :disabled="!form.canManage" />
            </label>
            <label><span>Carry Forward Below Minimum</span>
              <input v-model="form.policy.carry_forward_small_balance" type="checkbox"
                     :disabled="!form.canManage" />
            </label>
            <label><span>Manual Approval Threshold</span>
              <input v-model.number="form.policy.manual_approval_threshold" type="number" step="any"
                     :disabled="!form.canManage" />
            </label>
            <label><span>Maximum Negative Carry Forward</span>
              <input v-model.number="form.policy.maximum_negative_carry_forward" type="number"
                     step="any" :disabled="!form.canManage" />
            </label>
            <label><span>Enabled</span>
              <input v-model="form.policy.enabled" type="checkbox" :disabled="!form.canManage" />
            </label>
          </div>
        </section>

        <section v-if="validation" class="rug-section-card">
          <header><h2>Validation</h2></header>
          <ul class="smj-issue-list">
            <li v-for="(issue, i) in validation.issues" :key="i" :data-severity="issue.severity">
              <strong>{{ issue.severity }}</strong>
              <span>{{ issue.message }}</span>
              <em>{{ issue.owner }}</em>
            </li>
            <li v-if="!validation.issues.length"><span>No issues.</span></li>
          </ul>
        </section>

        <section v-if="simulation" class="rug-section-card">
          <header>
            <h2>Simulation</h2>
            <p>Run over real historical invoices. Nothing was written.</p>
          </header>
          <div class="smj-commissions__totals">
            <span>Lines <strong>{{ simulation.totals.lines }}</strong></span>
            <span>Gross <strong>{{ money(simulation.totals.gross_commission) }}</strong></span>
            <span>Withholding <strong>{{ money(simulation.totals.withholding) }}</strong></span>
            <span>Net <strong data-test="sim-net">{{ money(simulation.totals.net_commission) }}</strong></span>
            <span>Persisted <strong>{{ simulation.persisted ? "yes" : "no" }}</strong></span>
          </div>
          <p v-if="simulation.exceptions.length" class="smj-team-card__warning">
            {{ simulation.exceptions.length }} exception(s) would block this policy.
          </p>
        </section>

        <footer class="smj-form-actions">
          <button v-if="form.canManage" type="button" class="rug-primary" :disabled="saving"
                  data-test="policy-save" @click="save">
            {{ saving ? "Saving…" : "Save Policy" }}
          </button>
          <button v-if="!form.isNew" type="button" :disabled="busy === 'validate'"
                  data-test="policy-validate" @click="run('validate')">Validate</button>
          <button v-if="!form.isNew" type="button" :disabled="busy === 'simulate'"
                  data-test="policy-simulate" @click="run('simulate')">Simulate</button>
          <button v-if="!form.isNew && form.canApprove && !missingForCalc.length" type="button"
                  data-test="policy-approve" @click="run('approve')">Approve</button>
          <button v-if="!form.isNew && form.canManage" type="button" @click="run('suspend')">
            Suspend
          </button>
        </footer>
      </template>
    </main>
  </PageContainer>
</template>
