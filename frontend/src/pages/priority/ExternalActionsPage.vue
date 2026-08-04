<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getExternalActions } from "@/services/externalActions.js";

const data = ref(null);
const error = ref(null);
const loading = ref(true);
const category = ref("");
const owner = ref("");
const status = ref("");
const blockingOnly = ref(false);
const overdueOnly = ref(false);
const readyOnly = ref(false);
let controller;

const categories = computed(() => (data.value ? Object.entries(data.value.by_category) : []));

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    data.value = await getExternalActions(
      {
        category: category.value,
        owner: owner.value,
        status: status.value,
        blocking_only: blockingOnly.value ? 1 : 0,
        overdue_only: overdueOnly.value ? 1 : 0,
        ready_only: readyOnly.value ? 1 : 0,
      },
      controller.signal,
    );
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

watch([category, owner, status, blockingOnly, overdueOnly, readyOnly], load);

function statusClass(value) {
  if (value === "Verified") return "is-good";
  if (value === "Rejected" || value === "Blocked") return "is-bad";
  if (value === "Ready for Verification") return "is-ready";
  return "is-pending";
}

function exportCsv() {
  if (!data.value) return;
  const header = ["Action ID", "Category", "Title", "Owner", "Status", "Blocking",
    "Due", "Required action", "Verification", "Evidence"];
  const rows = data.value.items.map((i) => [
    i.action_id, i.category, i.title, i.owner_role || "", i.status,
    i.blocking_go_live ? "yes" : "no", i.due_date || "",
    i.required_action || "", i.verification_procedure || "", i.evidence || "",
  ]);
  const csv = [header, ...rows]
    .map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(","))
    .join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "smj-external-actions.csv";
  link.click();
  URL.revokeObjectURL(url);
}

function print() {
  window.print();
}

onBeforeUnmount(() => controller?.abort());
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page external-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Admin</RouterLink><span>›</span>
        <RouterLink to="/admin/readiness">Launch Readiness</RouterLink><span>›</span>
        <strong>External Actions</strong>
      </nav>

      <header class="rug-banner rug-banner--gold">
        <div>
          <span class="rug-badge">Owned outside this system</span>
          <h1>External Actions</h1>
          <p v-if="data">{{ data.summary }}</p>
        </div>
        <div class="rug-banner-actions">
          <button class="rug-button rug-button--secondary" type="button" @click="exportCsv">Export</button>
          <button class="rug-button rug-button--secondary" type="button" @click="print">Print</button>
          <button class="rug-primary" type="button" :disabled="loading" @click="load">
            {{ loading ? "…" : "Refresh" }}
          </button>
        </div>
      </header>

      <ErrorState v-if="error" title="Unable to load external actions" :message="error.message" @retry="load" />
      <div v-else-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <template v-else-if="data">
        <p v-if="!data.go_live_ready" class="external-blockers">
          {{ data.blocking_outstanding }} blocking action(s) outstanding:
          {{ data.blocking_ids.join(", ") }}. None can be completed by changing this software.
        </p>

        <section class="rug-section-card external-filters">
          <label>Category
            <select v-model="category">
              <option value="">All</option>
              <option v-for="c in data.categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </label>
          <label>Owner
            <select v-model="owner">
              <option value="">All</option>
              <option v-for="o in data.owners" :key="o" :value="o">{{ o }}</option>
            </select>
          </label>
          <label>Status
            <select v-model="status">
              <option value="">All</option>
              <option v-for="s in data.statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </label>
          <label class="external-toggle"><input v-model="blockingOnly" type="checkbox" /> Blocking only</label>
          <label class="external-toggle"><input v-model="overdueOnly" type="checkbox" /> Overdue</label>
          <label class="external-toggle"><input v-model="readyOnly" type="checkbox" /> Ready for verification</label>
        </section>

        <section v-for="[cat, items] in categories" :key="cat" class="rug-section-card">
          <header><div><h2>{{ cat }}</h2></div></header>
          <div class="rug-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Action</th><th>Owner</th><th>Status</th>
                  <th>Verification required</th><th>Evidence</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in items" :key="item.action_id">
                  <td>
                    {{ item.action_id }}
                    <small v-if="item.blocking_go_live" class="external-blocking">blocking</small>
                  </td>
                  <td>
                    <strong>{{ item.title }}</strong>
                    <small class="external-detail">{{ item.required_action }}</small>
                    <small v-if="item.risk && item.risk !== '—'" class="external-risk">
                      Risk: {{ item.risk }}
                    </small>
                  </td>
                  <td>
                    {{ item.owner_role || "—" }}
                    <small v-if="item.overdue" class="external-risk">overdue</small>
                  </td>
                  <td><span class="external-pill" :class="statusClass(item.status)">{{ item.status }}</span></td>
                  <td class="external-detail">{{ item.verification_procedure }}</td>
                  <td>
                    <span v-if="item.evidence">{{ item.evidence }}</span>
                    <span v-else class="external-none">none recorded</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <p class="external-note">
          A document describing a step is not evidence that it happened, and a script
          that would perform it is not a rehearsal. Verification needs proof, and cannot
          be recorded by the person who did the work.
        </p>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.external-filters{display:flex;flex-wrap:wrap;gap:1rem;align-items:end}
.external-filters label{display:flex;flex-direction:column;gap:.25rem;font-weight:700;font-size:.85rem}
.external-toggle{flex-direction:row!important;align-items:center;gap:.4rem}
.external-blockers{margin:0 0 1rem;padding:.75rem 1rem;border-radius:.6rem;font-weight:700;background:var(--ref-warning-background);color:var(--ref-danger)}
.external-pill{display:inline-flex;padding:.25rem .6rem;border-radius:999px;font-weight:800;font-size:.82rem;background:var(--ref-border-colour);white-space:nowrap}
.external-pill.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.external-pill.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
.external-pill.is-ready{background:var(--ref-warning-background);color:var(--ref-warning,#8a6d00)}
.external-pill.is-pending{background:var(--ref-border-colour)}
.external-detail{display:block;color:var(--ref-secondary-text);font-weight:500}
.external-risk{display:block;color:var(--ref-danger);font-weight:600}
.external-blocking{display:block;color:var(--ref-danger);font-weight:700;font-size:.75rem}
.external-none{color:var(--ref-secondary-text);font-style:italic}
.external-note{margin-top:1rem;color:var(--ref-secondary-text)}
</style>
