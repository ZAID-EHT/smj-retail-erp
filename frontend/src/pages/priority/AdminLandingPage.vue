<script setup>
import { onBeforeUnmount, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getAdminLanding } from "@/services/adminLanding.js";

const data = ref(null);
const error = ref(null);
const loading = ref(true);
let controller;

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    data.value = await getAdminLanding(controller.signal);
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

onBeforeUnmount(() => controller?.abort());
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page admin-landing">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><strong>Administration</strong></nav>
      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">System administration</span>
          <h1>Administration</h1>
          <p>Everything an administrator manages, in one place. Cards you cannot access are hidden.</p>
        </div>
        <div class="rug-banner-actions">
          <button class="rug-primary" type="button" :disabled="loading" @click="load">{{ loading ? "Refreshing…" : "Refresh" }}</button>
        </div>
      </header>

      <ErrorState v-if="error" title="Unable to load administration" :message="error.message" @retry="load" />
      <div v-else-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <template v-else-if="data">
        <p v-if="!data.cards.length" class="ru-empty">You do not have access to any administration areas.</p>
        <section v-else class="admin-grid">
          <article v-for="card in data.cards" :key="card.key" class="admin-card">
            <header>
              <h2>{{ card.title }}</h2>
              <span v-if="card.warnings" class="admin-warn" :title="`${card.warnings} warning(s)`">⚠ {{ card.warnings }}</span>
            </header>
            <p class="admin-desc">{{ card.description }}</p>
            <p class="admin-status" :class="card.status_ok ? 'is-good' : 'is-bad'">{{ card.status }}</p>
            <footer>
              <RouterLink class="rug-primary" :to="card.route">Open</RouterLink>
              <RouterLink v-if="card.secondary_route" class="rug-button rug-button--secondary" :to="card.secondary_route">More</RouterLink>
            </footer>
          </article>
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.admin-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}
.admin-card{display:flex;flex-direction:column;gap:.5rem;padding:1.1rem;border:1px solid var(--ref-border-colour);border-radius:1rem;background:var(--ref-card-background)}
.admin-card header{display:flex;align-items:center;justify-content:space-between;gap:.5rem}
.admin-card h2{margin:0;font-size:1.1rem}
.admin-desc{color:var(--ref-secondary-text);flex:1}
.admin-status{margin:0;font-weight:800;font-size:.9rem}
.admin-status.is-good{color:var(--ref-success)}
.admin-status.is-bad{color:var(--ref-danger)}
.admin-warn{color:var(--ref-danger);font-weight:800}
.admin-card footer{display:flex;gap:.5rem;flex-wrap:wrap}
.admin-card footer a{min-height:40px;display:inline-flex;align-items:center;padding:0 .9rem;border-radius:.6rem;text-decoration:none}
</style>
