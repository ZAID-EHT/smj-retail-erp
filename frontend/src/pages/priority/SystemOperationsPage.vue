<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  getBackupStatus,
  getErrorLogSummary,
  getReadiness,
  getSystemHealth,
} from "@/services/systemOperations.js";

const health = ref(null);
const readiness = ref(null);
const backups = ref(null);
const errors = ref(null);
const error = ref(null);
const loading = reactive({ all: true });
let controller;

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.all = true;
  error.value = null;
  try {
    const [h, r, b, e] = await Promise.all([
      getSystemHealth(controller.signal),
      getReadiness(controller.signal),
      getBackupStatus(controller.signal),
      getErrorLogSummary(controller.signal),
    ]);
    health.value = h;
    readiness.value = r;
    backups.value = b;
    errors.value = e;
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.all = false;
  }
}

function ok(value) {
  return value ? "is-good" : "is-bad";
}

onBeforeUnmount(() => controller?.abort());
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page sysops-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Admin</RouterLink><span>›</span><strong>System Operations</strong>
      </nav>
      <header class="rug-banner rug-banner--dark-blue">
        <div>
          <span class="rug-badge">Read-only operational status</span>
          <h1>System Operations</h1>
          <p>Fixed-purpose health, readiness and backup status. No shell access, no credentials, no restore from the web.</p>
        </div>
        <div class="rug-banner-actions">
          <button class="rug-primary" type="button" :disabled="loading.all" @click="load">{{ loading.all ? "Refreshing…" : "Refresh" }}</button>
        </div>
      </header>

      <ErrorState v-if="error" title="Unable to load system status" :message="error.message" @retry="load" />
      <div v-else-if="loading.all" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <template v-else>
        <section v-if="health" class="rug-section-card">
          <header><div><h2>Health</h2><p>Core services and error trend.</p></div></header>
          <dl class="sysops-facts">
            <div><dt>Database</dt><dd><span class="sysops-pill" :class="ok(health.database.connected)">{{ health.database.connected ? "Connected" : "Down" }}</span></dd></div>
            <div><dt>Cache (Redis)</dt><dd><span class="sysops-pill" :class="ok(health.cache_redis.connected)">{{ health.cache_redis.connected ? "Connected" : "Down" }}</span></dd></div>
            <div><dt>Scheduler</dt><dd><span class="sysops-pill" :class="ok(health.scheduler.enabled)">{{ health.scheduler.enabled ? "Enabled" : "Disabled" }}</span></dd></div>
            <div><dt>Errors (24h)</dt><dd>{{ health.errors.last_24h }} <small>({{ health.errors.trend }})</small></dd></div>
            <div><dt>Failed jobs</dt><dd>{{ health.background_jobs.failed < 0 ? "n/a" : health.background_jobs.failed }}</dd></div>
          </dl>
        </section>

        <section v-if="readiness" class="rug-section-card">
          <header><div><h2>Production readiness</h2><p>Configuration flags and installed versions.</p></div></header>
          <dl class="sysops-facts">
            <div><dt>Developer mode</dt><dd><span class="sysops-pill" :class="ok(!readiness.developer_mode)">{{ readiness.developer_mode ? "ON (not for prod)" : "Off" }}</span></dd></div>
            <div><dt>Maintenance mode</dt><dd>{{ readiness.maintenance_mode ? "On" : "Off" }}</dd></div>
            <div><dt>Scheduler</dt><dd><span class="sysops-pill" :class="ok(readiness.scheduler_enabled)">{{ readiness.scheduler_enabled ? "Enabled" : "Disabled" }}</span></dd></div>
            <div><dt>Pending migrations</dt><dd><span class="sysops-pill" :class="ok(!readiness.pending_migrations)">{{ readiness.pending_migrations ? "Yes" : "None" }}</span></dd></div>
            <div><dt>Companies</dt><dd>{{ readiness.company_count }}</dd></div>
            <div><dt>First-time setup</dt><dd>{{ readiness.first_time_setup_required ? "Required" : "Complete" }}</dd></div>
            <div><dt>Email delivery</dt><dd><span class="sysops-pill" :class="ok(readiness.email_configured)">{{ readiness.email_configured ? "Configured" : "Not configured" }}</span></dd></div>
          </dl>
          <div class="rug-table-wrap">
            <table><thead><tr><th>App</th><th>Version</th></tr></thead>
              <tbody><tr v-for="(v, app) in readiness.app_versions" :key="app"><td>{{ app }}</td><td>{{ v || "—" }}</td></tr></tbody>
            </table>
          </div>
        </section>

        <section v-if="backups" class="rug-section-card">
          <header><div><h2>Backups</h2><p>{{ backups.backup_count }} backup(s); latest {{ backups.latest_age_hours == null ? "—" : backups.latest_age_hours + "h" }} ago.</p></div></header>
          <p class="sysops-note">{{ backups.note }}</p>
          <div v-if="backups.backups.length" class="rug-table-wrap">
            <table><thead><tr><th>File</th><th>Size (MB)</th><th>Created</th></tr></thead>
              <tbody><tr v-for="row in backups.backups" :key="row.file"><td>{{ row.file }}</td><td>{{ row.size_mb }}</td><td>{{ row.modified }}</td></tr></tbody>
            </table>
          </div>
          <p v-else class="ru-empty">No backups found.</p>
        </section>

        <section v-if="errors" class="rug-section-card">
          <header><div><h2>Recent errors</h2><p>{{ errors.total_7d }} in the last {{ errors.since_days }} days (counts only, no content).</p></div></header>
          <div v-if="errors.top_methods.length" class="rug-table-wrap">
            <table><thead><tr><th>Source</th><th>Count</th></tr></thead>
              <tbody><tr v-for="row in errors.top_methods" :key="row.method"><td>{{ row.method || "—" }}</td><td>{{ row.count }}</td></tr></tbody>
            </table>
          </div>
          <p v-else class="ru-empty">No errors in the window.</p>
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.sysops-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1rem;margin-bottom:1rem}
.sysops-facts dt{font-size:.85rem;color:var(--ref-secondary-text);font-weight:700}
.sysops-facts dd{margin:.25rem 0 0;font-weight:800}
.sysops-pill{display:inline-flex;padding:.25rem .6rem;border-radius:999px;font-weight:800;font-size:.85rem;background:var(--ref-border-colour)}
.sysops-pill.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.sysops-pill.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
.sysops-note{color:var(--ref-secondary-text);font-style:italic}
</style>
