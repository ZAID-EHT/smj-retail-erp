<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { downloadPdfUrl, getPreviewCandidates, getPrintingOverview, previewDocument } from "@/services/printingAdmin.js";

const overview = ref(null);
const error = ref(null);
const loading = reactive({ init: true, preview: false });
const preview = reactive({ doctype: "", candidates: [], name: "", format: "", html: "" });
let controller;

async function init() {
  loading.init = true;
  error.value = null;
  try {
    overview.value = await getPrintingOverview();
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.init = false;
  }
}

async function pickDoctype(doctype) {
  preview.doctype = doctype;
  preview.name = "";
  preview.html = "";
  preview.format = "";
  try {
    const result = await getPreviewCandidates(doctype);
    preview.candidates = result.candidates || [];
  } catch (caught) {
    preview.candidates = [];
    error.value = caught;
  }
}

async function runPreview() {
  if (!preview.doctype || !preview.name) return;
  loading.preview = true;
  error.value = null;
  try {
    controller?.abort();
    controller = new AbortController();
    const result = await previewDocument(preview.doctype, preview.name, preview.format || null, controller.signal);
    preview.html = result.html;
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.preview = false;
  }
}

function formatsFor(doctype) {
  const row = (overview.value?.formats_by_doctype || []).find((r) => r.doctype === doctype);
  return row ? row.formats : [];
}

onBeforeUnmount(() => controller?.abort());
init();
</script>

<template>
  <PageContainer>
    <main class="rug-page print-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Admin</RouterLink><span>›</span><strong>Printing &amp; Branding</strong>
      </nav>
      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Standard ERPNext printing</span>
          <h1>Printing &amp; Branding</h1>
          <p>Manage letter heads and print formats, and preview any document you can access. Previews honour field permissions — cost fields you cannot see are not rendered.</p>
        </div>
        <div class="rug-banner-actions">
          <RouterLink class="rug-button rug-button--secondary" to="/admin/letter-head">Letter Heads</RouterLink>
          <RouterLink class="rug-primary" to="/admin/print-format">Print Formats</RouterLink>
        </div>
      </header>

      <ErrorState v-if="error" title="Printing error" :message="error.message" @retry="init" />
      <div v-else-if="loading.init" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>

      <template v-else-if="overview">
        <section class="rug-section-card">
          <header><div><h2>Letter heads</h2><p>{{ overview.letter_heads.length }} defined.</p></div></header>
          <div v-if="overview.letter_heads.length" class="rug-table-wrap">
            <table><thead><tr><th>Name</th><th>Default</th><th>Status</th></tr></thead>
              <tbody><tr v-for="lh in overview.letter_heads" :key="lh.name"><td>{{ lh.name }}</td><td>{{ lh.is_default ? "Yes" : "" }}</td><td>{{ lh.disabled ? "Disabled" : "Active" }}</td></tr></tbody>
            </table>
          </div>
          <p v-else class="ru-empty">No letter heads yet — create one to brand printed documents.</p>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Print formats</h2><p>Per document type.</p></div></header>
          <div class="rug-table-wrap">
            <table><thead><tr><th>Document</th><th>Formats</th><th>Default</th></tr></thead>
              <tbody><tr v-for="row in overview.formats_by_doctype" :key="row.doctype">
                <td>{{ row.doctype }}</td>
                <td>{{ row.formats.map((f) => f.name).join(", ") || "—" }}</td>
                <td>{{ row.default_format || "system default" }}</td>
              </tr></tbody>
            </table>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Preview</h2><p>Render a real document using a chosen format.</p></div></header>
          <div class="rug-form-grid">
            <label><span>Document type</span>
              <select v-model="preview.doctype" @change="pickDoctype(preview.doctype)">
                <option value="">Select…</option>
                <option v-for="row in overview.formats_by_doctype" :key="row.doctype" :value="row.doctype">{{ row.doctype }}</option>
              </select>
            </label>
            <label><span>Document</span>
              <select v-model="preview.name" :disabled="!preview.candidates.length">
                <option value="">{{ preview.candidates.length ? "Select…" : "none available" }}</option>
                <option v-for="c in preview.candidates" :key="c" :value="c">{{ c }}</option>
              </select>
            </label>
            <label><span>Format</span>
              <select v-model="preview.format" :disabled="!preview.doctype">
                <option value="">Default</option>
                <option v-for="f in formatsFor(preview.doctype)" :key="f.name" :value="f.name">{{ f.name }}</option>
              </select>
            </label>
            <div class="print-actions">
              <button class="rug-primary" type="button" :disabled="loading.preview || !preview.name" @click="runPreview">{{ loading.preview ? "Rendering…" : "Preview" }}</button>
              <a
                v-if="preview.name"
                class="rug-button rug-button--secondary"
                :href="downloadPdfUrl(preview.doctype, preview.name, preview.format || undefined)"
                target="_blank"
                rel="noopener"
              >Download PDF</a>
            </div>
          </div>
          <div v-if="preview.html" class="print-preview" v-html="preview.html" />
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.print-page label{display:grid;gap:.4rem;font-weight:700}
.print-page label select{min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.print-actions{display:flex;align-items:end}
.print-preview{margin-top:1rem;padding:1rem;border:1px solid var(--ref-border-colour);border-radius:.75rem;background:#fff;color:#111;max-height:640px;overflow:auto}
</style>
