<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { createCompany, getSetupOptions, getSetupStatus } from "@/services/setupWizard.js";

const router = useRouter();
const status = ref(null);
const options = ref(null);
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, creating: false });
const form = reactive({
  company_name: "", abbr: "", default_currency: "LKR", country: "Sri Lanka", chart_of_accounts: "Standard",
});

async function init() {
  loading.init = true;
  error.value = null;
  try {
    status.value = await getSetupStatus();
    if (status.value.can_create_company) {
      try { options.value = await getSetupOptions(); } catch { options.value = null; }
    }
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.init = false;
  }
}

async function submit() {
  loading.creating = true;
  error.value = null;
  notice.value = null;
  try {
    const result = await createCompany({ ...form });
    notice.value = `Company "${result.company}" created with its Chart of Accounts and default warehouses.`;
    status.value = await getSetupStatus();
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.creating = false;
  }
}

onBeforeUnmount(() => {});
init();
</script>

<template>
  <PageContainer>
    <main class="rug-page setup-page">
      <header class="rug-banner rug-banner--blue">
        <div>
          <span class="rug-badge">First-time setup</span>
          <h1>Set up your business</h1>
          <p>Create your company and its accounting foundation. ERPNext builds the Chart of Accounts, cost center and default warehouses for you.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Setup error" :message="error.message" @retry="init" />
      <p v-if="notice" class="setup-notice" role="status">{{ notice }}</p>
      <div v-if="loading.init" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>

      <template v-else-if="status">
        <section class="rug-section-card">
          <header><div><h2>Setup checklist</h2><p>{{ status.setup_required ? "No company exists yet — create one to begin." : "Your company is configured." }}</p></div></header>
          <ul class="setup-checklist">
            <li v-for="item in status.checklist" :key="item.item" :class="{ 'is-done': item.done }">
              <span class="setup-check" :class="{ 'is-done': item.done }">{{ item.done ? "✓" : "○" }}</span>
              <span>{{ item.item }}<small v-if="item.count != null"> ({{ item.count }})</small></span>
            </li>
          </ul>
          <p v-if="status.ready_for_transactions" class="setup-ready">Ready for transactions.</p>
        </section>

        <section v-if="status.setup_required && status.can_create_company" class="rug-section-card">
          <header><div><h2>Create company</h2><p>The essentials — you can refine details afterwards in Administration.</p></div></header>
          <form class="rug-form-grid" @submit.prevent="submit">
            <label><span>Company name *</span><input v-model="form.company_name" type="text" required /></label>
            <label><span>Abbreviation</span><input v-model="form.abbr" type="text" maxlength="10" placeholder="auto" /></label>
            <label><span>Default currency</span>
              <input v-model="form.default_currency" list="setup-currencies" type="text" />
              <datalist id="setup-currencies"><option v-for="c in (options?.currencies || [])" :key="c" :value="c" /></datalist>
            </label>
            <label><span>Country</span>
              <input v-model="form.country" list="setup-countries" type="text" />
              <datalist id="setup-countries"><option v-for="c in (options?.countries || [])" :key="c" :value="c" /></datalist>
            </label>
            <label><span>Chart of Accounts</span>
              <select v-model="form.chart_of_accounts"><option v-for="t in (options?.coa_templates || ['Standard'])" :key="t" :value="t">{{ t }}</option></select>
            </label>
            <div class="setup-actions">
              <button class="rug-primary" type="submit" :disabled="loading.creating || !form.company_name">{{ loading.creating ? "Creating…" : "Create company" }}</button>
            </div>
          </form>
        </section>

        <section v-else-if="status.setup_required && !status.can_create_company" class="rug-section-card">
          <p class="ru-empty">A System Manager must complete first-time setup. Please ask an administrator.</p>
        </section>

        <section v-else class="rug-section-card">
          <header><div><h2>Next steps</h2></div></header>
          <div class="setup-links">
            <RouterLink class="rug-primary" to="/admin/companies">Manage companies</RouterLink>
            <RouterLink class="rug-button rug-button--secondary" to="/admin/data">Import opening data</RouterLink>
            <RouterLink class="rug-button rug-button--secondary" to="/home">Go to dashboard</RouterLink>
          </div>
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.setup-page label{display:grid;gap:.4rem;font-weight:700}
.setup-page label :is(input,select){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.setup-checklist{list-style:none;margin:0;padding:0;display:grid;gap:.5rem}
.setup-checklist li{display:flex;align-items:center;gap:.6rem;font-weight:700}
.setup-check{display:inline-flex;width:26px;height:26px;align-items:center;justify-content:center;border-radius:999px;background:var(--ref-border-colour);font-weight:900}
.setup-check.is-done{background:var(--ref-success-background);color:var(--ref-success)}
.setup-ready{color:var(--ref-success);font-weight:800}
.setup-actions,.setup-links{display:flex;flex-wrap:wrap;gap:.6rem;align-items:end}
.setup-links a{min-height:44px;display:inline-flex;align-items:center;padding:0 1rem;border-radius:.65rem;text-decoration:none}
.setup-notice{padding:.7rem 1rem;border-radius:.7rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
</style>
