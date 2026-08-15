<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import OptionSelect from "@/components/forms/OptionSelect.vue";
import {
  checkWhatsappNumber, createCustomer, findDuplicateCustomers, getCustomer, getPriceCategories,
  previewCustomerId,
} from "@/services/customerQuickEntry.js";
import {
  assignCustomerSalesManager, getCustomerSalesAssignment, listSalesPersons,
  salesPersonAdminUrl, searchSalesManagers,
} from "@/services/salesTeam.js";

/* Phone numbers are held in the one local shape the business uses. The example is
   shown beside every number field, and the server refuses anything else, so the
   WhatsApp uniqueness rule below cannot be sidestepped by typing the same number
   a different way. */
const PHONE_EXAMPLE = "0778754231";
const PHONE_HINT = `Enter the number as ${PHONE_EXAMPLE}.`;

/* Every customer carries a generated ID (CUS00001, CUS00002, ...) in the same
   shape as a Product ID. On a new customer this shows the number the next save
   would take -- a preview, not a reservation, so opening the form does not burn
   an ID. On an edit it shows the one the record already holds. */
const customerId = ref("");

const route = useRoute();
const router = useRouter();
const editName = computed(() => route.params.name || null);

const form = reactive({
  customer_name: "", address: "", city: "", contact_no: "", whatsapp_no: "", same_whatsapp: false,
  accounts_department_no: "", same_accounts_dept: false, transport_detail: "", transport_method: "",
  br_no: "", vat_no: "", business_nature: "", price_category: "Retail Price", payment_type: "Non-Credit",
  credit_limit: null, credit_days: null,
});
const created = ref("");

/* Sales assignment. The customer is assigned by choosing its sales manager --
   the manager identifies the team behind them, which is what still carries the
   commission split -- and the rate is the customer's own when it is filled in. */
const salesManager = ref("");
const commissionRate = ref(null);
const originalManager = ref("");
const originalRate = ref(null);
const managerOptions = ref([]);
const canAssignTeam = ref(false);
const teamPreview = ref(null);

/* The sales person is who handles the customer. It sits beside the manager but is
   not part of the commission split, which stays the manager's team. */
const salesPerson = ref("");
const originalPerson = ref("");
const personOptions = ref([]);
const canManagePersons = ref(false);

async function loadSalesPersons() {
  try {
    const result = await listSalesPersons();
    personOptions.value = result?.sales_persons || [];
    canManagePersons.value = Boolean(result?.can_manage);
  } catch {
    personOptions.value = [];
    canManagePersons.value = false;
  }
}

function manageSalesPersons() {
  window.open(salesPersonAdminUrl(), "_blank", "noopener");
}

// The roster page opens in another tab; pick up anything changed there when this
// tab is looked at again.
function refreshPersonsOnFocus() {
  if (document.visibilityState === "visible") loadSalesPersons();
}

const selectedManager = computed(() =>
  managerOptions.value.find((m) => m.value === salesManager.value) || null);
const assignmentChanged = computed(() =>
  salesManager.value !== originalManager.value
  || salesPerson.value !== originalPerson.value
  || Number(commissionRate.value ?? NaN) !== Number(originalRate.value ?? NaN));

/* The rate follows the manager's team unless the user has typed their own. */
function onManagerChange() {
  teamPreview.value = selectedManager.value;
  if (selectedManager.value && (commissionRate.value === null || commissionRate.value === "")) {
    commissionRate.value = selectedManager.value.commission_rate;
  }
  if (!salesManager.value) teamPreview.value = null;
}

async function loadSalesManagers() {
  try {
    managerOptions.value = (await searchSalesManagers()) || [];
  } catch {
    managerOptions.value = [];
  }
}

async function loadAssignment(name) {
  if (!name) return;
  try {
    const result = await getCustomerSalesAssignment(name);
    canAssignTeam.value = Boolean(result.can_manage);
    salesManager.value = result.sales_manager || "";
    originalManager.value = salesManager.value;
    salesPerson.value = result.sales_person || "";
    originalPerson.value = salesPerson.value;
    commissionRate.value = result.commission_rate ?? null;
    originalRate.value = commissionRate.value;
    teamPreview.value = result.assignment
      ? { team_name: result.assignment.team_name, commission_rate: result.assignment.commission_rate }
      : null;
  } catch { /* an unassigned or unreadable customer simply shows no manager */ }
}

const priceCategories = ref([]);
const duplicates = ref([]);
// The verdict on the typed WhatsApp number: whether it is well-formed and whether
// another customer already holds it.
const whatsappCheck = ref(null);
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, saving: false });
let dupTimer;
let whatsappTimer;

const whatsappBlocked = computed(() =>
  Boolean(whatsappCheck.value && (whatsappCheck.value.duplicate || whatsappCheck.value.valid === false)));

const isCredit = computed(() => form.payment_type === "Credit");

watch(() => form.same_whatsapp, (v) => { if (v) form.whatsapp_no = form.contact_no; });
watch(() => form.same_accounts_dept, (v) => { if (v) form.accounts_department_no = form.contact_no; });
watch(() => form.contact_no, (v) => {
  if (form.same_whatsapp) form.whatsapp_no = v;
  if (form.same_accounts_dept) form.accounts_department_no = v;
});
watch(() => form.customer_name, (v) => {
  if (editName.value || !v) { duplicates.value = []; return; }
  window.clearTimeout(dupTimer);
  dupTimer = window.setTimeout(async () => {
    try { duplicates.value = (await findDuplicateCustomers(v))?.candidates || []; } catch { duplicates.value = []; }
  }, 300);
});

/* Only the WhatsApp number has to be unique -- it is the channel the business
   messages the customer on, so two customers sharing one would send the wrong
   person the wrong message. Contact No and Account Dept No are free to repeat.

   Asked while typing so the answer arrives before the save is attempted; the save
   enforces the same rule regardless, so a number taken in between is still caught. */
watch(() => form.whatsapp_no, (v) => {
  window.clearTimeout(whatsappTimer);
  if (!v || !v.trim()) { whatsappCheck.value = null; return; }
  whatsappTimer = window.setTimeout(async () => {
    try { whatsappCheck.value = await checkWhatsappNumber(v, editName.value); }
    catch { whatsappCheck.value = null; }
  }, 350);
});

async function loadPriceCategories() {
  try {
    const result = await getPriceCategories();
    priceCategories.value = result?.categories || [];
    if (!editName.value && result?.default) form.price_category = result.default;
  } catch {
    // The three categories are fixed, so a failed lookup falls back to them
    // rather than leaving the user with an empty required dropdown.
    priceCategories.value = [
      { label: "Wholesale Price", available: true },
      { label: "Department Price", available: true },
      { label: "Retail Price", available: true },
    ];
  }
}

async function init() {
  loading.init = true;
  await Promise.all([loadPriceCategories(), loadSalesManagers(), loadSalesPersons()]);
  if (editName.value) {
    try {
      await loadAssignment(editName.value);
      const c = await getCustomer(editName.value);
      Object.assign(form, {
        customer_name: c.customer_name, address: c.address || "", city: c.city || "",
        contact_no: c.contact_no || "", whatsapp_no: c.whatsapp_no || "",
        accounts_department_no: c.accounts_department_no || "", transport_detail: c.transport_detail || "",
        transport_method: c.transport_method || "", br_no: c.br_no || "", vat_no: c.vat_no || "",
        business_nature: c.business_nature || "",
        price_category: c.price_category || "Retail Price", payment_type: c.payment_type || "Non-Credit",
        credit_limit: c.credit_limit, credit_days: c.credit_days,
      });
      created.value = c.created;
      customerId.value = editName.value;
    } catch (caught) { error.value = caught; }
  } else {
    try {
      customerId.value = (await previewCustomerId())?.customer_id || "";
    } catch { customerId.value = ""; }
  }
  loading.init = false;
}

async function save() {
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const payload = { ...form };
    if (!isCredit.value) { payload.credit_limit = 0; payload.credit_days = 0; }
    const result = await createCustomer(payload, editName.value);
    // The assignment is a separate, permission-gated call so a user without the
    // right to reassign can still save the rest of the customer.
    if (canAssignTeam.value && assignmentChanged.value) {
      await assignCustomerSalesManager(result.name, {
        salesManager: salesManager.value,
        team: selectedManager.value?.team,
        commissionRate: commissionRate.value,
        salesPerson: salesPerson.value,
      });
      originalManager.value = salesManager.value;
      originalRate.value = commissionRate.value;
      originalPerson.value = salesPerson.value;
    }
    notice.value = `Saved ${result.customer}.`;
    router.push(`/sales/customers/${encodeURIComponent(result.name)}`).catch(() => {});
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

onMounted(() => document.addEventListener("visibilitychange", refreshPersonsOnFocus));
onBeforeUnmount(() => {
  document.removeEventListener("visibilitychange", refreshPersonsOnFocus);
  window.clearTimeout(dupTimer);
  window.clearTimeout(whatsappTimer);
});
init();
</script>

<template>
  <PageContainer>
    <main class="rug-page cqf-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/sales/customers">Customers</RouterLink><span>›</span><strong>{{ editName ? "Edit Customer" : "New Customer" }}</strong></nav>
      <header class="rug-banner rug-banner--green">
        <div>
          <span class="rug-badge">Customer quick-create</span>
          <h1>{{ editName ? "Edit Customer" : "New Customer" }}</h1>
          <p>Address and contact are saved as standard linked records; Price Category drives customer pricing.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Could not save customer" :message="error.message" @retry="init" />
      <p v-if="notice" class="cqf-notice" role="status">{{ notice }}</p>
      <div v-if="loading.init" class="rug-skeleton"><i v-for="n in 5" :key="n" /></div>

      <form v-else class="cqf-form" @submit.prevent="save">
        <section class="rug-section-card">
          <header><div><h2>Customer Information</h2></div></header>
          <div class="rug-form-grid">
            <label><span>Customer ID</span>
              <input :value="customerId || 'Auto-generated on save'" type="text" readonly class="is-calculated" tabindex="-1" />
              <small v-if="!editName">Preview of the next ID. Settled when the customer is saved.</small>
            </label>
            <label><span>Customer *</span><input v-model="form.customer_name" type="text" required /></label>
            <label><span>BR No</span><input v-model="form.br_no" type="text" /></label>
            <label><span>VAT No</span><input v-model="form.vat_no" type="text" /></label>
            <OptionSelect v-model="form.business_nature" option-type="Business Nature" label="Business Nature" />
            <label><span>Created Date</span><input :value="editName ? created : 'On save'" type="text" readonly /></label>
          </div>
          <p v-if="duplicates.length" class="cqf-dup">⚠ Similar customers exist: {{ duplicates.map((d) => d.customer_name).join(', ') }}</p>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Contact and Address</h2></div></header>
          <div class="rug-form-grid">
            <label class="cqf-wide"><span>Address</span><input v-model="form.address" type="text" placeholder="Address line" /></label>
            <OptionSelect v-model="form.city" option-type="City" label="City" searchable placeholder="Type to search a city…" />
            <label><span>Contact No</span>
              <input v-model="form.contact_no" type="tel" :placeholder="PHONE_EXAMPLE" />
              <small>{{ PHONE_HINT }}</small>
            </label>
            <label><span>WhatsApp No</span>
              <input
                v-model="form.whatsapp_no"
                :disabled="form.same_whatsapp"
                :class="{ 'cqf-input--bad': whatsappBlocked }"
                type="tel"
                :placeholder="PHONE_EXAMPLE"
              />
              <small><label class="cqf-inline"><input v-model="form.same_whatsapp" type="checkbox" /> Same as Contact No</label></small>
              <small v-if="whatsappCheck?.duplicate" class="cqf-bad" role="alert">
                ⚠ Duplicate number — {{ whatsappCheck.customer_name }} already uses this WhatsApp number.
              </small>
              <small v-else-if="whatsappCheck && whatsappCheck.valid === false" class="cqf-bad" role="alert">
                ⚠ {{ PHONE_HINT }}
              </small>
              <small v-else>{{ PHONE_HINT }} Each customer needs its own WhatsApp number.</small>
            </label>
            <label><span>Account Dept No</span>
              <input v-model="form.accounts_department_no" :disabled="form.same_accounts_dept" type="tel" :placeholder="PHONE_EXAMPLE" />
              <small><label class="cqf-inline"><input v-model="form.same_accounts_dept" type="checkbox" /> Same as Contact No</label></small>
              <small>{{ PHONE_HINT }}</small>
            </label>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Delivery Information</h2></div></header>
          <div class="rug-form-grid">
            <OptionSelect v-model="form.transport_method" option-type="Transport Method" label="Transport Method" />
            <label class="cqf-wide"><span>Transport Detail</span><input v-model="form.transport_detail" type="text" /></label>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Pricing and Credit</h2><p>Price Category is the price entered against each product.</p></div></header>
          <div class="rug-form-grid">
            <label><span>Price Category</span>
              <select v-model="form.price_category">
                <option v-for="p in priceCategories" :key="p.label" :value="p.label" :disabled="p.available === false">
                  {{ p.label }}{{ p.available === false ? " (not set up)" : "" }}
                </option>
              </select>
            </label>
            <label><span>Payment Type</span>
              <select v-model="form.payment_type"><option value="Non-Credit">Non-Credit</option><option value="Credit">Credit</option></select>
            </label>
            <label v-if="isCredit"><span>Credit Limit (LKR) *</span><input v-model.number="form.credit_limit" type="number" min="0" step="any" :required="isCredit" /></label>
            <label v-if="isCredit"><span>Credit Days *</span><input v-model.number="form.credit_days" type="number" min="0" step="1" :required="isCredit" /></label>
          </div>
          <p v-if="!isCredit" class="cqf-hint">Non-Credit: payment is required before dispatch (existing manager overrides remain).</p>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Sales Assignment</h2><p>The sales manager whose commission split applies to this customer's new transactions, and the sales person who handles it.</p></div></header>
          <div class="rug-form-grid">
            <label><span>Assigned Sales Manager</span>
              <select v-model="salesManager" :disabled="!canAssignTeam" @change="onManagerChange">
                <option value="">No sales manager</option>
                <option v-for="m in managerOptions" :key="m.team" :value="m.value">
                  {{ m.label }} — {{ m.team_name }}
                </option>
              </select>
            </label>
            <label><span class="cqf-label-row">Assign Sales Person
              <button
                v-if="canManagePersons"
                type="button"
                class="cqf-manage"
                title="Add, edit or delete sales people"
                @click="manageSalesPersons"
              >Add / edit / delete</button>
            </span>
              <select v-model="salesPerson" :disabled="!canAssignTeam">
                <option value="">No sales person</option>
                <option v-for="p in personOptions" :key="p.name" :value="p.name">{{ p.sales_person_name }}</option>
              </select>
              <small v-if="!personOptions.length">Nobody is on the sales roster yet.</small>
              <small v-else>Who handles this customer. The commission split still follows the sales manager's team.</small>
            </label>
            <label><span>Commission Rate (%)</span>
              <input
                v-model.number="commissionRate"
                :disabled="!canAssignTeam"
                type="number"
                min="0"
                max="100"
                step="any"
                placeholder="Team rate"
              />
              <small v-if="teamPreview">Team default {{ Number(teamPreview.commission_rate || 0) }}%. Clear to follow it.</small>
            </label>
          </div>

          <p v-if="!canAssignTeam" class="cqf-hint">Only a Sales Manager or System Manager can change this assignment.</p>
          <p v-else-if="!managerOptions.length" class="cqf-hint">No active sales team has a manager yet, so there is nobody to assign.</p>

          <p v-if="assignmentChanged" class="cqf-hint cqf-hint--warn" role="status">
            Changing the sales assignment affects new transactions only. Documents already raised keep the team they were created with.
          </p>
        </section>

        <footer class="cqf-actions">
          <button type="button" class="rug-button rug-button--secondary" @click="router.back()">Cancel</button>
          <button type="submit" class="rug-primary" :disabled="loading.saving || !form.customer_name || whatsappBlocked">{{ loading.saving ? "Saving…" : "Save Customer" }}</button>
        </footer>
      </form>
    </main>
  </PageContainer>
</template>

<style scoped>
.cqf-form label{display:grid;gap:.35rem;font-weight:700}
.cqf-form label :is(input,select){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.cqf-form label input[readonly]{opacity:.7;font-style:italic}
.cqf-form label small{font-weight:500;color:var(--ref-secondary-text)}
.cqf-inline{display:inline-flex;align-items:center;gap:.35rem;font-weight:500}
.cqf-inline input{min-height:20px;width:18px}
.cqf-wide{grid-column:1/-1}
.cqf-actions{display:flex;justify-content:flex-end;gap:.6rem;padding-top:1rem}
.cqf-notice{padding:.6rem 1rem;border-radius:.6rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
.cqf-dup{color:var(--ref-danger);font-weight:700}
.cqf-hint{color:var(--ref-secondary-text)}
.cqf-bad{color:var(--ref-danger);font-weight:700}
.cqf-form label input.cqf-input--bad{border-color:var(--ref-danger)}
.cqf-label-row{display:flex;align-items:center;justify-content:space-between;gap:.5rem}
.cqf-manage{border:1px solid var(--ref-border-colour);border-radius:.5rem;background:transparent;color:var(--ref-accent, var(--ref-primary-text));font-size:.72rem;font-weight:700;padding:.15rem .5rem;cursor:pointer}
.cqf-manage:hover{background:var(--ref-card-background)}
</style>
