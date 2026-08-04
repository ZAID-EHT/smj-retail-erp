<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getProductionConfiguration } from "@/services/productionConfiguration.js";

const data = ref(null);
const error = ref(null);
const loading = ref(true);
const problemsOnly = ref(false);
let controller;

const groups = computed(() => (data.value ? Object.entries(data.value.by_group) : []));

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    data.value = await getProductionConfiguration(controller.signal);
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

function statusClass(status) {
  if (status === "Pass") return "is-good";
  if (status === "Fail") return "is-bad";
  if (status === "Warning") return "is-warn";
  if (status === "External") return "is-external";
  return "is-na";
}

function visible(items) {
  return problemsOnly.value
    ? items.filter((i) => i.status === "Fail" || i.status === "Warning")
    : items;
}

function print() {
  window.print();
}

onBeforeUnmount(() => controller?.abort());
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page config-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Admin</RouterLink><span>›</span>
        <RouterLink to="/admin/readiness">Launch Readiness</RouterLink><span>›</span>
        <strong>Production Configuration</strong>
      </nav>

      <header class="rug-banner rug-banner--gold">
        <div>
          <span class="rug-badge">Configuration check</span>
          <h1>Production Configuration</h1>
          <p v-if="data">{{ data.summary }}</p>
        </div>
        <div class="rug-banner-actions">
          <label class="config-toggle">
            <input v-model="problemsOnly" type="checkbox" /> Problems only
          </label>
          <button class="rug-button rug-button--secondary" type="button" @click="print">Print</button>
          <button class="rug-primary" type="button" :disabled="loading" @click="load">
            {{ loading ? "…" : "Re-check" }}
          </button>
        </div>
      </header>

      <ErrorState v-if="error" title="Unable to run configuration checks" :message="error.message" @retry="load" />
      <div v-else-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <template v-else-if="data">
        <p v-if="!data.production_ready" class="config-verdict">
          This site is not production-ready.
          <template v-if="data.failing.length">
            {{ data.failing.length }} check(s) failing.
          </template>
          <template v-if="data.counts.External">
            {{ data.counts.External }} item(s) depend on someone outside this system
            and cannot be confirmed here.
          </template>
        </p>

        <section v-for="[group, items] in groups" :key="group" class="rug-section-card">
          <header><div><h2>{{ group }}</h2></div></header>
          <div v-if="!visible(items).length" class="ru-empty">Nothing to show.</div>
          <div v-else class="rug-table-wrap">
            <table>
              <thead><tr><th>Check</th><th>Status</th><th>Detail</th><th>Owner</th></tr></thead>
              <tbody>
                <tr v-for="item in visible(items)" :key="item.name">
                  <td>{{ item.name }}</td>
                  <td><span class="config-pill" :class="statusClass(item.status)">{{ item.status }}</span></td>
                  <td>
                    {{ item.detail }}
                    <small v-if="item.action" class="config-action">{{ item.action }}</small>
                  </td>
                  <td>{{ item.owner || "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <p class="config-note">
          External items are not failures. They are steps nobody inside this system can
          perform or confirm, so the page reports them as unknown rather than guessing.
        </p>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.config-toggle{display:inline-flex;align-items:center;gap:.4rem;font-weight:700;color:#fff}
.config-verdict{margin:0 0 1rem;padding:.75rem 1rem;border-radius:.6rem;font-weight:700;background:var(--ref-warning-background);color:var(--ref-danger)}
.config-pill{display:inline-flex;padding:.25rem .6rem;border-radius:999px;font-weight:800;font-size:.82rem;background:var(--ref-border-colour);white-space:nowrap}
.config-pill.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.config-pill.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
.config-pill.is-warn{background:var(--ref-warning-background);color:var(--ref-warning,#8a6d00)}
.config-pill.is-external{background:var(--ref-border-colour);color:var(--ref-secondary-text)}
.config-pill.is-na{background:var(--ref-border-colour);color:var(--ref-secondary-text)}
.config-action{display:block;color:var(--ref-secondary-text);font-weight:500}
.config-note{margin-top:1rem;color:var(--ref-secondary-text)}
</style>
