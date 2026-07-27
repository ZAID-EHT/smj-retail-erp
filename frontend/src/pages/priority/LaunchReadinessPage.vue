<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getLaunchReadiness } from "@/services/launchReadiness.js";

const data = ref(null);
const error = ref(null);
const loading = ref(true);
const onlyBlockers = ref(false);
let controller;

const categories = computed(() => (data.value ? Object.entries(data.value.by_category) : []));

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    data.value = await getLaunchReadiness(controller.signal);
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

function statusClass(status) {
  if (status === "Verified" || status === "Complete") return "is-good";
  if (status === "Failed") return "is-bad";
  return "is-pending";
}

function visible(items) {
  return onlyBlockers.value ? items.filter((i) => i.blocker) : items;
}

function print() {
  window.print();
}

onBeforeUnmount(() => controller?.abort());
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page readiness-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/admin">Admin</RouterLink><span>›</span><strong>Launch Readiness</strong></nav>
      <header class="rug-banner rug-banner--gold">
        <div>
          <span class="rug-badge">Truthful go-live checklist</span>
          <h1>Launch Readiness</h1>
          <p v-if="data">{{ data.summary }}</p>
        </div>
        <div class="rug-banner-actions">
          <label class="readiness-toggle"><input v-model="onlyBlockers" type="checkbox" /> Blockers only</label>
          <button class="rug-button rug-button--secondary" type="button" @click="print">Print</button>
          <button class="rug-primary" type="button" :disabled="loading" @click="load">{{ loading ? "…" : "Refresh" }}</button>
        </div>
      </header>

      <ErrorState v-if="error" title="Unable to load readiness" :message="error.message" @retry="load" />
      <div v-else-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <template v-else-if="data">
        <section v-for="[cat, items] in categories" :key="cat" class="rug-section-card">
          <header><div><h2>{{ cat }}</h2></div></header>
          <div v-if="!visible(items).length" class="ru-empty">No items to show.</div>
          <div v-else class="rug-table-wrap">
            <table>
              <thead><tr><th>Item</th><th>Status</th><th>Owner</th><th>Action</th></tr></thead>
              <tbody>
                <tr v-for="item in visible(items)" :key="item.name">
                  <td>{{ item.name }}<small v-if="item.risk" class="readiness-risk"> — {{ item.risk }}</small></td>
                  <td><span class="readiness-pill" :class="statusClass(item.status)">{{ item.status }}</span></td>
                  <td>{{ item.owner || "—" }}</td>
                  <td>
                    <RouterLink v-if="item.route" :to="item.route">{{ item.action || "Open" }}</RouterLink>
                    <span v-else>{{ item.action || "—" }}</span>
                    <small v-if="item.doc" class="readiness-doc"> ({{ item.doc.split('/').pop() }})</small>
                  </td>
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
.readiness-toggle{display:inline-flex;align-items:center;gap:.4rem;font-weight:700;color:#fff}
.readiness-pill{display:inline-flex;padding:.25rem .6rem;border-radius:999px;font-weight:800;font-size:.82rem;background:var(--ref-border-colour)}
.readiness-pill.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.readiness-pill.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
.readiness-pill.is-pending{background:var(--ref-warning-background);color:var(--ref-warning,#8a6d00)}
.readiness-risk{color:var(--ref-danger);font-weight:600}
.readiness-doc{color:var(--ref-secondary-text)}
</style>
