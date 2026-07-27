<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { createCustomer, findDuplicateCustomers, getCustomer } from "@/services/customerQuickEntry.js";

const route = useRoute();
const router = useRouter();
const editName = computed(() => route.params.name || null);

const form = reactive({
  customer_name: "", address: "", city: "", contact_no: "", whatsapp_no: "", same_whatsapp: false,
  accounts_department_no: "", transport_detail: "", transport_method: "", br_no: "",
  business_nature: "", price_category: "Retail Price List", payment_type: "Non-Credit",
  credit_limit: null, credit_days: null,
});
const created = ref("");
const priceLists = ref([]);
const duplicates = ref([]);
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, saving: false });
let dupTimer;

const isCredit = computed(() => form.payment_type === "Credit");
const transportMethods = ["Customer Pickup", "Company Delivery", "Own Vehicle", "Courier", "Third-Party Transport", "Other"];
const businessNatures = ["Retailer", "Wholesaler", "Department Store", "Contractor", "Hotel", "Office", "Distributor", "Other"];

watch(() => form.same_whatsapp, (v) => { if (v) form.whatsapp_no = form.contact_no; });
watch(() => form.contact_no, (v) => { if (form.same_whatsapp) form.whatsapp_no = v; });
watch(() => form.customer_name, (v) => {
  if (editName.value || !v) { duplicates.value = []; return; }
  window.clearTimeout(dupTimer);
  dupTimer = window.setTimeout(async () => {
    try { duplicates.value = (await findDuplicateCustomers(v))?.candidates || []; } catch { duplicates.value = []; }
  }, 300);
});

async function loadPriceLists() {
  try {
    const r = await fetch("/api/method/my_store_ui.quick_entry.options.search?kind=price_list", { credentials: "same-origin", cache: "no-store" });
    const p = await r.json().catch(() => ({}));
    priceLists.value = p?.message?.options || ["Retail Price List"];
  } catch { priceLists.value = ["Retail Price List"]; }
}

async function init() {
  loading.init = true;
  await loadPriceLists();
  if (editName.value) {
    try {
      const c = await getCustomer(editName.value);
      Object.assign(form, {
        customer_name: c.customer_name, address: c.address || "", city: c.city || "",
        contact_no: c.contact_no || "", whatsapp_no: c.whatsapp_no || "",
        accounts_department_no: c.accounts_department_no || "", transport_detail: c.transport_detail || "",
        transport_method: c.transport_method || "", br_no: c.br_no || "", business_nature: c.business_nature || "",
        price_category: c.price_category || "Retail Price List", payment_type: c.payment_type || "Non-Credit",
        credit_limit: c.credit_limit, credit_days: c.credit_days,
      });
      created.value = c.created;
    } catch (caught) { error.value = caught; }
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
    notice.value = `Saved ${result.customer}.`;
    router.push(`/sales/customers/${encodeURIComponent(result.name)}`).catch(() => {});
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

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
            <label><span>Customer *</span><input v-model="form.customer_name" type="text" required /></label>
            <label><span>BR No</span><input v-model="form.br_no" type="text" /></label>
            <label><span>Business Nature</span>
              <select v-model="form.business_nature"><option value="">Select…</option><option v-for="b in businessNatures" :key="b" :value="b">{{ b }}</option></select>
            </label>
            <label><span>Created Date</span><input :value="editName ? created : 'On save'" type="text" readonly /></label>
          </div>
          <p v-if="duplicates.length" class="cqf-dup">⚠ Similar customers exist: {{ duplicates.map((d) => d.customer_name).join(', ') }}</p>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Contact and Address</h2></div></header>
          <div class="rug-form-grid">
            <label class="cqf-wide"><span>Address</span><input v-model="form.address" type="text" placeholder="Address line" /></label>
            <label><span>City</span><input v-model="form.city" type="text" /></label>
            <label><span>Contact No</span><input v-model="form.contact_no" type="tel" /></label>
            <label><span>WhatsApp No</span>
              <input v-model="form.whatsapp_no" :disabled="form.same_whatsapp" type="tel" />
              <small><label class="cqf-inline"><input v-model="form.same_whatsapp" type="checkbox" /> Same as Contact No</label></small>
            </label>
            <label><span>Account Dept No</span><input v-model="form.accounts_department_no" type="tel" /></label>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Delivery Information</h2></div></header>
          <div class="rug-form-grid">
            <label><span>Transport Method</span>
              <select v-model="form.transport_method"><option value="">Select…</option><option v-for="t in transportMethods" :key="t" :value="t">{{ t }}</option></select>
            </label>
            <label class="cqf-wide"><span>Transport Detail</span><input v-model="form.transport_detail" type="text" /></label>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Pricing and Credit</h2></div></header>
          <div class="rug-form-grid">
            <label><span>Price Category</span>
              <select v-model="form.price_category"><option v-for="p in priceLists" :key="p" :value="p">{{ p }}</option></select>
            </label>
            <label><span>Payment Type</span>
              <select v-model="form.payment_type"><option value="Non-Credit">Non-Credit</option><option value="Credit">Credit</option></select>
            </label>
            <label v-if="isCredit"><span>Credit Limit (LKR) *</span><input v-model.number="form.credit_limit" type="number" min="0" step="any" :required="isCredit" /></label>
            <label v-if="isCredit"><span>Credit Days *</span><input v-model.number="form.credit_days" type="number" min="0" step="1" :required="isCredit" /></label>
          </div>
          <p v-if="!isCredit" class="cqf-hint">Non-Credit: payment is required before dispatch (existing manager overrides remain).</p>
        </section>

        <footer class="cqf-actions">
          <button type="button" class="rug-button rug-button--secondary" @click="router.back()">Cancel</button>
          <button type="submit" class="rug-primary" :disabled="loading.saving || !form.customer_name">{{ loading.saving ? "Saving…" : "Save Customer" }}</button>
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
</style>
