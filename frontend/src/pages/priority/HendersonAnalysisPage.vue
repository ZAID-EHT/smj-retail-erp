<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { RouterLink } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import { getHendersonAnalysis, saveHendersonAnalysis } from "@/services/managementPages.js";

const data = ref(null);
const loading = ref(true);
const saving = ref(false);
const error = ref(null);
const notice = ref("");
const editing = ref(false);
const draft = ref([]);
const summaryNotes = ref("");
const assessmentDate = ref("");
let controller = null;

function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  getHendersonAnalysis({}, controller.signal)
    .then((result) => {
      data.value = result;
      resetDraft();
    })
    .catch((err) => { if (err.name !== "AbortError") error.value = err; })
    .finally(() => { loading.value = false; });
}
function resetDraft() {
  draft.value = (data.value?.domains || []).map((d) => ({ ...d }));
  summaryNotes.value = data.value?.assessment?.summary_notes || "";
  assessmentDate.value = data.value?.assessment?.assessment_date || new Date().toISOString().slice(0, 10);
}
load();
onBeforeUnmount(() => controller?.abort());

const canEdit = computed(() => !!data.value?.can_edit);
const maxScore = computed(() => data.value?.max_score ?? 5);
const summary = computed(() => data.value?.summary || {});

function startEdit() { resetDraft(); editing.value = true; notice.value = ""; }
function cancelEdit() { resetDraft(); editing.value = false; }

function save() {
  saving.value = true;
  error.value = null;
  saveHendersonAnalysis({
    company: data.value?.company || "",
    assessment_date: assessmentDate.value,
    summary_notes: summaryNotes.value,
    domains: draft.value.map((d) => ({
      domain: d.domain,
      current_score: Number(d.current_score) || 0,
      target_score: Number(d.target_score) || 0,
      priority: d.priority || "Medium",
      notes: d.notes || "",
    })),
    name: data.value?.assessment?.name || "",
  })
    .then(() => { editing.value = false; notice.value = "Assessment saved."; load(); })
    .catch((err) => { error.value = err; })
    .finally(() => { saving.value = false; });
}

function toneFor(gap) {
  if (gap >= 3) return "is-critical";
  if (gap === 2) return "is-high";
  if (gap === 1) return "is-medium";
  return "";
}
</script>

<template>
  <PageContainer>
    <main class="rug-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span>
        <RouterLink to="/reports">Reports</RouterLink><span>›</span>
        <strong>Henderson Analysis</strong>
      </nav>

      <header class="rug-banner rug-banner--dark-blue">
        <div>
          <span class="rug-badge">Management analysis</span>
          <h1>Henderson Analysis</h1>
          <p>Strategic alignment across business and IT. Separate from day-to-day sales, pricing and stock.</p>
        </div>
        <div class="rug-banner-actions">
          <button v-if="canEdit && !editing" type="button" class="rug-primary" @click="startEdit">Edit assessment</button>
          <template v-if="editing">
            <button type="button" class="rug-primary" :disabled="saving" @click="save">{{ saving ? "Saving…" : "Save" }}</button>
            <button type="button" :disabled="saving" @click="cancelEdit">Cancel</button>
          </template>
          <button v-if="!editing" type="button" @click="load">Refresh</button>
        </div>
      </header>

      <ErrorState v-if="error && !data" title="Unable to load the analysis" :message="error.message" @retry="load" />
      <p v-else-if="error" class="rug-inline-error" role="alert">{{ error.message }}</p>
      <p v-if="notice" class="smj-sales-notice" role="status">{{ notice }}</p>

      <div v-if="loading" class="rug-skeleton"><i v-for="n in 5" :key="n" /></div>

      <template v-else-if="data">
        <section v-if="!data.assessment && !editing" class="rug-section-card">
          <div class="rug-empty">
            <h2>No assessment recorded yet</h2>
            <p v-if="canEdit">Use “Edit assessment” to record the first Henderson assessment.</p>
            <p v-else>A manager has not recorded an assessment for this company yet.</p>
          </div>
        </section>

        <section class="smj-henderson-summary" aria-label="Alignment summary">
          <article><small>Average current</small><strong>{{ summary.average_current ?? 0 }}</strong><em>of {{ maxScore }}</em></article>
          <article><small>Average target</small><strong>{{ summary.average_target ?? 0 }}</strong><em>of {{ maxScore }}</em></article>
          <article><small>Total alignment gap</small><strong>{{ summary.total_gap ?? 0 }}</strong><em>across all domains</em></article>
          <article><small>Domains assessed</small><strong>{{ summary.assessed_domains ?? 0 }}</strong><em>of {{ (data.domain_options || []).length }}</em></article>
        </section>

        <section v-if="summary.priority_areas?.length" class="rug-section-card">
          <header><h2>Priority areas</h2><p>The widest gaps between current and target.</p></header>
          <ul class="smj-henderson-priorities">
            <li v-for="area in summary.priority_areas" :key="area.domain" :class="toneFor(area.gap)">
              <strong>{{ area.domain }}</strong>
              <span>gap {{ area.gap }}</span>
              <em>{{ area.priority }}</em>
            </li>
          </ul>
        </section>

        <section class="rug-section-card">
          <header>
            <h2>Domain assessment</h2>
            <p v-if="editing">Scores run from 0 to {{ maxScore }}.</p>
          </header>

          <div class="rug-table-region">
            <table>
              <thead>
                <tr>
                  <th>Domain</th><th>Current</th><th>Target</th><th>Gap</th><th>Priority</th><th>Notes</th>
                </tr>
              </thead>
              <tbody v-if="!editing">
                <tr v-for="row in data.domains" :key="row.domain" :class="toneFor(row.gap)">
                  <td data-label="Domain"><strong>{{ row.domain }}</strong></td>
                  <td data-label="Current">{{ row.current_score }}</td>
                  <td data-label="Target">{{ row.target_score }}</td>
                  <td data-label="Gap">{{ row.gap }}</td>
                  <td data-label="Priority">{{ row.priority }}</td>
                  <td data-label="Notes">{{ row.notes || "—" }}</td>
                </tr>
              </tbody>
              <tbody v-else>
                <tr v-for="row in draft" :key="row.domain">
                  <td data-label="Domain"><strong>{{ row.domain }}</strong></td>
                  <td data-label="Current">
                    <input v-model.number="row.current_score" type="number" min="0" :max="maxScore" :aria-label="`Current score for ${row.domain}`" />
                  </td>
                  <td data-label="Target">
                    <input v-model.number="row.target_score" type="number" min="0" :max="maxScore" :aria-label="`Target score for ${row.domain}`" />
                  </td>
                  <td data-label="Gap">{{ Math.max((Number(row.target_score) || 0) - (Number(row.current_score) || 0), 0) }}</td>
                  <td data-label="Priority">
                    <select v-model="row.priority" :aria-label="`Priority for ${row.domain}`">
                      <option>Low</option><option>Medium</option><option>High</option><option>Critical</option>
                    </select>
                  </td>
                  <td data-label="Notes">
                    <input v-model="row.notes" type="text" :aria-label="`Notes for ${row.domain}`" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="rug-section-card">
          <header><h2>Management notes</h2></header>
          <p v-if="!editing" class="smj-henderson-notes">{{ data.assessment?.summary_notes || "No notes recorded." }}</p>
          <label v-else class="smj-henderson-notes-edit">
            <span>Summary notes</span>
            <textarea v-model="summaryNotes" rows="4"></textarea>
          </label>
          <label v-if="editing" class="smj-henderson-notes-edit">
            <span>Assessment date</span>
            <input v-model="assessmentDate" type="date" />
          </label>
        </section>

        <footer v-if="data.assessment" class="smj-henderson-meta">
          Last updated {{ new Date(data.assessment.modified).toLocaleString() }}
          by {{ data.assessment.modified_by }} · status {{ data.assessment.status }}
        </footer>
      </template>
    </main>
  </PageContainer>
</template>
