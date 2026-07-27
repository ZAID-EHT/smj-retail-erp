<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  createScheduledReport,
  getSchedulableReports,
  getScheduledReportsOverview,
  setScheduleEnabled,
} from "@/services/scheduledReports.js";

const overview = ref(null);
const reports = ref([]);
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, saving: false });
const filters = reactive({ search: "", status: "" });
const form = reactive({ report: "", frequency: "Weekly", output_format: "HTML", email_to: "", day_of_week: "Monday" });

async function load() {
  loading.init = true;
  error.value = null;
  try {
    const [o, r] = await Promise.all([getScheduledReportsOverview(filters.search, filters.status), getSchedulableReports("")]);
    overview.value = o;
    reports.value = r?.reports || [];
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.init = false;
  }
}

async function create() {
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const result = await createScheduledReport({ ...form });
    notice.value = result.message || `Schedule created (${result.enabled ? "enabled" : "disabled"}).`;
    await load();
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.saving = false;
  }
}

async function toggle(row) {
  error.value = null;
  try {
    await setScheduleEnabled(row.name, row.enabled ? 0 : 1);
    await load();
  } catch (caught) {
    error.value = caught;
  }
}

onBeforeUnmount(() => {});
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page sched-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/reports">Reports</RouterLink><span>›</span><strong>Scheduled Reports</strong></nav>
      <header class="rug-banner rug-banner--dark-blue">
        <div>
          <span class="rug-badge">Auto-email reports</span>
          <h1>Scheduled Reports</h1>
          <p>Email a report on a schedule. You can only schedule reports you are permitted to run; delivery needs a configured outgoing email account.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Scheduled reports error" :message="error.message" @retry="load" />
      <p v-if="notice" class="sched-notice" role="status">{{ notice }}</p>
      <div v-if="loading.init" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>

      <template v-else-if="overview">
        <section v-if="!overview.email.can_send_welcome_email" class="rug-section-card sched-warn">
          <strong>⚠ Email delivery is not configured.</strong>
          New schedules are created <em>disabled</em> and cannot be enabled until an outgoing Email Account is set up.
          <RouterLink to="/admin/email">Open Email Setup</RouterLink>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Create a schedule</h2></div></header>
          <form class="rug-form-grid" @submit.prevent="create">
            <label><span>Report *</span>
              <select v-model="form.report" required>
                <option value="">Select…</option>
                <option v-for="r in reports" :key="r.name" :value="r.name">{{ r.name }}</option>
              </select>
            </label>
            <label><span>Frequency</span>
              <select v-model="form.frequency"><option v-for="f in overview.frequencies" :key="f" :value="f">{{ f }}</option></select>
            </label>
            <label><span>Format</span>
              <select v-model="form.output_format"><option v-for="f in overview.formats" :key="f" :value="f">{{ f }}</option></select>
            </label>
            <label><span>Recipients (comma/newline)</span><input v-model="form.email_to" type="text" placeholder="ops@example.com" /></label>
            <div class="sched-actions"><button class="rug-primary" type="submit" :disabled="loading.saving || !form.report">{{ loading.saving ? "Saving…" : "Create schedule" }}</button></div>
          </form>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Schedules</h2><p>{{ overview.schedules.length }} configured.</p></div></header>
          <div v-if="!overview.schedules.length" class="ru-empty">No scheduled reports yet.</div>
          <div v-else class="rug-table-wrap">
            <table>
              <thead><tr><th>Report</th><th>Frequency</th><th>Format</th><th>Status</th><th></th></tr></thead>
              <tbody>
                <tr v-for="row in overview.schedules" :key="row.name">
                  <td>{{ row.report }}</td>
                  <td>{{ row.frequency }}</td>
                  <td>{{ row.format }}</td>
                  <td><span class="sched-pill" :class="row.enabled ? 'is-good' : 'is-off'">{{ row.enabled ? "Enabled" : "Disabled" }}</span></td>
                  <td><button type="button" class="sched-link" @click="toggle(row)">{{ row.enabled ? "Disable" : "Enable" }}</button></td>
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
.sched-page label{display:grid;gap:.4rem;font-weight:700}
.sched-page label :is(input,select){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.sched-actions{display:flex;align-items:end}
.sched-warn{background:var(--ref-warning-background);color:var(--ref-danger)}
.sched-warn a{margin-left:.5rem;font-weight:800}
.sched-notice{padding:.6rem 1rem;border-radius:.6rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
.sched-pill{display:inline-flex;padding:.25rem .6rem;border-radius:999px;font-weight:800;font-size:.85rem}
.sched-pill.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.sched-pill.is-off{background:var(--ref-border-colour)}
.sched-link{min-height:40px;padding:0 .8rem;border:1px solid var(--ref-border-colour);border-radius:.6rem;background:var(--ref-card-background);cursor:pointer}
</style>
