<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getEmailOverview, getNotificationCoverage } from "@/services/emailAdmin.js";

const overview = ref(null);
const coverage = ref(null);
const error = ref(null);
const loading = reactive({ all: true });
let controller;

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.all = true;
  error.value = null;
  try {
    const [o, c] = await Promise.all([getEmailOverview(controller.signal), getNotificationCoverage(controller.signal)]);
    overview.value = o;
    coverage.value = c;
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.all = false;
  }
}

onBeforeUnmount(() => controller?.abort());
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page email-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Admin</RouterLink><span>›</span><strong>Email &amp; Notifications</strong>
      </nav>
      <header class="rug-banner rug-banner--gold">
        <div>
          <span class="rug-badge">Delivery status &amp; templates</span>
          <h1>Email &amp; Notifications</h1>
          <p>Whether email can actually be delivered, and the templates and notifications that would be used. Credentials are never shown.</p>
        </div>
        <div class="rug-banner-actions"><button class="rug-primary" type="button" :disabled="loading.all" @click="load">{{ loading.all ? "Refreshing…" : "Refresh" }}</button></div>
      </header>

      <ErrorState v-if="error" title="Unable to load email status" :message="error.message" @retry="load" />
      <div v-else-if="loading.all" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>

      <template v-else-if="overview">
        <section class="rug-section-card">
          <header><div><h2>Delivery status</h2></div></header>
          <p class="email-status" :class="overview.delivery.can_send_welcome_email ? 'is-good' : 'is-bad'">
            {{ overview.delivery.can_send_welcome_email ? "Email delivery is available." : overview.delivery.message }}
          </p>
          <dl class="email-facts">
            <div><dt>Outgoing account configured</dt><dd>{{ overview.delivery.outgoing_configured ? "Yes" : "No" }}</dd></div>
            <div><dt>Outgoing enabled</dt><dd>{{ overview.delivery.outgoing_enabled ? "Yes" : "No" }}</dd></div>
            <div><dt>Default outgoing account</dt><dd>{{ overview.delivery.default_outgoing_account || "None" }}</dd></div>
            <div><dt>Queue (7d) sent / failed</dt><dd>{{ overview.queue.available ? `${overview.queue.sent} / ${overview.queue.error}` : "n/a" }}</dd></div>
          </dl>
          <p v-if="!overview.delivery.can_send_welcome_email" class="email-note">
            Configuring an outgoing Email Account with real SMTP credentials is an external administrator/server step — see the Email Setup guide. Until then, onboarding uses administrator-set passwords.
          </p>
        </section>

        <section v-if="coverage" class="rug-section-card">
          <header><div><h2>Notification coverage</h2><p>Which wholesale events have an enabled notification.</p></div></header>
          <div class="rug-table-wrap">
            <table><thead><tr><th>Event</th><th>Notification</th></tr></thead>
              <tbody><tr v-for="row in coverage.coverage" :key="row.event">
                <td>{{ row.event }}</td>
                <td><span class="email-pill" :class="row.has_enabled_notification ? 'is-good' : 'is-bad'">{{ row.has_enabled_notification ? "Enabled" : "None" }}</span></td>
              </tr></tbody>
            </table>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Email templates</h2><p>{{ overview.templates.length }} template(s).</p></div></header>
          <div v-if="overview.templates.length" class="rug-table-wrap">
            <table><thead><tr><th>Name</th><th>Subject</th></tr></thead>
              <tbody><tr v-for="t in overview.templates" :key="t.name"><td>{{ t.name }}</td><td>{{ t.subject }}</td></tr></tbody>
            </table>
          </div>
          <p v-else class="ru-empty">No email templates defined.</p>
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.email-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem}
.email-facts dt{font-size:.85rem;color:var(--ref-secondary-text);font-weight:700}
.email-facts dd{margin:.25rem 0 0;font-weight:800}
.email-status{padding:.75rem 1rem;border-radius:.7rem;font-weight:800}
.email-status.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.email-status.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
.email-pill{display:inline-flex;padding:.25rem .6rem;border-radius:999px;font-weight:800;font-size:.85rem;background:var(--ref-border-colour)}
.email-pill.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.email-pill.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
.email-note{color:var(--ref-secondary-text);font-style:italic}
</style>
