<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  exportRecords,
  getImportHistory,
  getImportTemplateFields,
  getImportTypes,
  toCsv,
} from "@/services/dataManagement.js";

const types = ref([]);
const history = ref([]);
const selected = ref("");
const templateFields = ref(null);
const exportPreview = ref(null);
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, template: false, exporting: false });
let controller;

async function init() {
  loading.init = true;
  error.value = null;
  try {
    const [t, h] = await Promise.all([getImportTypes(), getImportHistory()]);
    types.value = t?.types || [];
    history.value = h?.imports || [];
    if (types.value.length) selectType(types.value[0].doctype);
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.init = false;
  }
}

async function selectType(doctype) {
  selected.value = doctype;
  exportPreview.value = null;
  loading.template = true;
  try {
    templateFields.value = await getImportTemplateFields(doctype);
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.template = false;
  }
}

function downloadTemplate() {
  if (!templateFields.value) return;
  const headers = templateFields.value.fields.map((f) => f.fieldname);
  const csv = `${headers.join(",")}\n`;
  triggerDownload(csv, `${selected.value.replace(/\s+/g, "_")}_template.csv`);
}

async function runExport() {
  loading.exporting = true;
  error.value = null;
  notice.value = null;
  try {
    controller?.abort();
    controller = new AbortController();
    const result = await exportRecords(selected.value, 1000, controller.signal);
    exportPreview.value = result;
    notice.value = `${result.row_count} row(s) ready (capped at ${result.capped_at}).`;
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.exporting = false;
  }
}

function downloadExport() {
  if (!exportPreview.value) return;
  const csv = toCsv(exportPreview.value.fields, exportPreview.value.rows);
  triggerDownload(csv, `${selected.value.replace(/\s+/g, "_")}_export.csv`);
}

function triggerDownload(text, filename) {
  const blob = new Blob([text], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

onBeforeUnmount(() => controller?.abort());
init();
</script>

<template>
  <PageContainer>
    <main class="rug-page data-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Admin</RouterLink><span>›</span><strong>Data Management</strong>
      </nav>
      <header class="rug-banner rug-banner--turquoise">
        <div>
          <span class="rug-badge">Guided import & export</span>
          <h1>Data Management</h1>
          <p>Import and export an allowlist of business records through standard Frappe Data Import. Exports respect your permissions and never include credentials or cost fields you cannot see.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Data management error" :message="error.message" @retry="init" />
      <p v-if="notice" class="data-notice" role="status">{{ notice }}</p>
      <div v-if="loading.init" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>

      <template v-else>
        <section class="rug-section-card">
          <header><div><h2>Choose data type</h2><p>Only these DocTypes are available; arbitrary DocTypes are rejected server-side.</p></div></header>
          <div v-if="!types.length" class="ru-empty">No data types available to you.</div>
          <div v-else class="data-types">
            <button
              v-for="t in types"
              :key="t.doctype"
              type="button"
              class="data-type"
              :class="{ 'is-active': selected === t.doctype }"
              @click="selectType(t.doctype)"
            >
              <strong>{{ t.doctype }}</strong>
              <span>{{ t.can_import ? "import + export" : "export only" }}</span>
            </button>
          </div>
        </section>

        <section v-if="selected" class="rug-section-card">
          <header><div><h2>{{ selected }}</h2><p>Download a template to import, or export current records to CSV.</p></div></header>
          <div class="rug-banner-actions data-actions">
            <button class="rug-button rug-button--secondary" type="button" :disabled="loading.template" @click="downloadTemplate">Download import template</button>
            <button class="rug-primary" type="button" :disabled="loading.exporting" @click="runExport">{{ loading.exporting ? "Exporting…" : "Export records" }}</button>
            <button v-if="exportPreview" class="rug-button rug-button--secondary" type="button" @click="downloadExport">Download CSV ({{ exportPreview.row_count }})</button>
          </div>
          <p class="data-hint">
            To import: download the template, fill it, then use ERPNext Data Import (Frappe validates every row and shows row-level errors before committing).
          </p>
          <div v-if="exportPreview && exportPreview.rows.length" class="rug-table-wrap data-preview">
            <table>
              <thead><tr><th v-for="f in exportPreview.fields.slice(0, 6)" :key="f">{{ f }}</th></tr></thead>
              <tbody>
                <tr v-for="(row, i) in exportPreview.rows.slice(0, 10)" :key="i">
                  <td v-for="f in exportPreview.fields.slice(0, 6)" :key="f">{{ row[f] }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Import history</h2><p>Recent imports of allowlisted data types.</p></div></header>
          <div v-if="!history.length" class="ru-empty">No import history.</div>
          <div v-else class="rug-table-wrap">
            <table>
              <thead><tr><th>Reference</th><th>Type</th><th>Status</th><th>Created</th></tr></thead>
              <tbody><tr v-for="row in history" :key="row.name"><td>{{ row.reference_doctype }}</td><td>{{ row.import_type }}</td><td>{{ row.status }}</td><td>{{ row.creation }}</td></tr></tbody>
            </table>
          </div>
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.data-types{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.6rem}
.data-type{display:flex;flex-direction:column;gap:.2rem;min-height:60px;padding:.6rem .8rem;border:1px solid var(--ref-border-colour);border-radius:.75rem;background:var(--ref-card-background);color:var(--ref-primary-text);cursor:pointer;text-align:left}
.data-type.is-active{border-color:var(--ref-accent-turquoise,#0ca);background:var(--ref-success-background)}
.data-type span{font-size:.8rem;color:var(--ref-secondary-text)}
.data-actions{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:.6rem}
.data-actions button{min-height:44px;padding:0 1rem;border-radius:.65rem;border:1px solid var(--ref-border-colour);cursor:pointer}
.data-hint,.data-notice{color:var(--ref-secondary-text)}
.data-notice{padding:.6rem .9rem;border-radius:.6rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
.data-preview{margin-top:.6rem}
</style>
