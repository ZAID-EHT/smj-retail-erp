<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { RouterLink } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import { getAccountsWorkspace } from "@/services/managementPages.js";

const data = ref(null);
const loading = ref(true);
const error = ref(null);
let controller = null;

function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  getAccountsWorkspace("", controller.signal)
    .then((result) => { data.value = result; })
    .catch((err) => { if (err.name !== "AbortError") error.value = err; })
    .finally(() => { loading.value = false; });
}
load();
onBeforeUnmount(() => controller?.abort());

const currency = computed(() => data.value?.currency || "");
function format(card) {
  const value = Number(card.value || 0);
  if (card.kind === "currency") {
    const n = new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
    return currency.value ? `${currency.value} ${n}` : n;
  }
  return new Intl.NumberFormat().format(value);
}
</script>

<template>
  <PageContainer>
    <main class="rug-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span><strong>Accounts</strong>
      </nav>

      <header class="rug-banner rug-banner--gold">
        <div>
          <span class="rug-badge">Finance</span>
          <h1>Accounts</h1>
          <p>Receivables, payables, cash and reconciliation for {{ data?.company || "your company" }}.</p>
        </div>
        <button type="button" @click="load">Refresh</button>
      </header>

      <ErrorState v-if="error" title="Unable to load the accounts workspace" :message="error.message" @retry="load" />

      <div v-else-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <section v-else-if="!data?.has_access" class="rug-section-card">
        <div class="rug-empty">
          <h2>No accounting access</h2>
          <p>Your roles do not include permission to view accounting records.</p>
        </div>
      </section>

      <template v-else>
        <p v-if="!data.shows_financials" class="smj-accounts-note" role="status">
          Showing record counts only. Monetary totals require an accounting role.
        </p>

        <section v-for="section in data.sections" :key="section.key" class="rug-section-card smj-accounts-section">
          <header><h2>{{ section.title }}</h2></header>

          <div v-if="section.cards?.length" class="smj-accounts-cards">
            <article v-for="card in section.cards" :key="card.label" :class="['smj-accounts-card', card.tone === 'danger' && 'is-danger']">
              <small>{{ card.label }}</small>
              <strong>{{ format(card) }}</strong>
            </article>
          </div>

          <ul v-if="section.links?.length" class="smj-accounts-links">
            <li v-for="link in section.links" :key="link.path">
              <RouterLink :to="link.path">{{ link.label }}</RouterLink>
            </li>
          </ul>
        </section>
      </template>
    </main>
  </PageContainer>
</template>
