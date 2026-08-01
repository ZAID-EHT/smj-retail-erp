<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from "vue";
import { RouterLink } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import {
  createCustomPrintFormat, getPrintFormatAdmin, previewPrintFormat,
  setDefaultPrintFormat, setPrintFormatDisabled,
} from "@/services/managementPages.js";

const data = ref(null);
const loading = ref(true);
const busy = ref(false);
const error = ref(null);
const notice = ref("");
let controller = null;

const selected = ref({});          // doctype -> chosen format in the selector
const selectedLanguage = ref({});  // doctype -> chosen language
const newName = ref({});           // doctype -> name for a new custom format

/* Preview modal */
const preview = ref(null);
const previewLoading = ref(false);
const previewError = ref("");
const closeButton = ref(null);
let lastFocused = null;

function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  getPrintFormatAdmin(controller.signal)
    .then((result) => {
      data.value = result;
      for (const doc of result.documents || []) {
        selected.value[doc.doctype] = doc.default_print_format || "";
        selectedLanguage.value[doc.doctype] = doc.default_language || "";
      }
    })
    .catch((err) => { if (err.name !== "AbortError") error.value = err; })
    .finally(() => { loading.value = false; });
}
load();
onBeforeUnmount(() => { controller?.abort(); document.removeEventListener("keydown", onKeydown); });

function run(promise, successMessage) {
  busy.value = true;
  error.value = null;
  notice.value = "";
  return promise
    .then(() => { notice.value = successMessage; load(); })
    .catch((err) => { error.value = err; })
    .finally(() => { busy.value = false; });
}

function saveDefault(doc) {
  run(
    setDefaultPrintFormat({
      doctype: doc.doctype,
      print_format: selected.value[doc.doctype] || "",
      language: selectedLanguage.value[doc.doctype] || "",
    }),
    `Default format saved for ${doc.label}.`,
  );
}

function duplicate(doc) {
  const name = (newName.value[doc.doctype] || "").trim();
  if (!name) { error.value = { message: "Enter a name for the new format." }; return; }
  run(
    createCustomPrintFormat({
      doctype: doc.doctype, format_name: name, based_on: selected.value[doc.doctype] || "",
    }),
    `Created custom format ${name}.`,
  ).then(() => { newName.value[doc.doctype] = ""; });
}

function disableFormat(doc, format) {
  run(setPrintFormatDisabled({ print_format: format.name, disabled: 1 }),
    `${format.name} disabled.`);
}

function openPreview(doc) {
  lastFocused = document.activeElement;
  preview.value = { doctype: doc.doctype, label: doc.label, html: "" };
  previewLoading.value = true;
  previewError.value = "";
  document.addEventListener("keydown", onKeydown);
  previewPrintFormat({
    doctype: doc.doctype,
    print_format: selected.value[doc.doctype] || "",
    language: selectedLanguage.value[doc.doctype] || "",
  })
    .then((result) => { preview.value = { ...preview.value, ...result }; })
    .catch((err) => { previewError.value = err.message; })
    .finally(() => {
      previewLoading.value = false;
      nextTick(() => closeButton.value?.focus());
    });
}

function closePreview() {
  preview.value = null;
  previewError.value = "";
  document.removeEventListener("keydown", onKeydown);
  lastFocused?.focus?.();
}

function onKeydown(event) {
  if (event.key === "Escape") closePreview();
}

function printPreview() {
  const frame = document.getElementById("smj-print-frame");
  frame?.contentWindow?.focus();
  frame?.contentWindow?.print();
}

const documents = computed(() => data.value?.documents || []);
</script>

<template>
  <PageContainer>
    <main class="rug-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span>
        <RouterLink to="/admin">Admin</RouterLink><span>›</span><strong>Print Formats</strong>
      </nav>

      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Administration</span>
          <h1>Print Formats</h1>
          <p>Choose the Retail ERP format for each document. ERPNext Standard formats are never modified.</p>
        </div>
        <button type="button" @click="load">Refresh</button>
      </header>

      <ErrorState v-if="error && !data" title="Unable to load print formats" :message="error.message" @retry="load" />
      <p v-else-if="error" class="rug-inline-error" role="alert">{{ error.message }}</p>
      <p v-if="notice" class="smj-sales-notice" role="status">{{ notice }}</p>

      <div v-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <section v-for="doc in documents" v-else :key="doc.doctype" class="rug-section-card smj-print-doc">
        <header>
          <div>
            <h2>{{ doc.label }}</h2>
            <p>{{ doc.formats.length }} enabled format{{ doc.formats.length === 1 ? "" : "s" }}</p>
          </div>
          <button type="button" :disabled="!doc.sample" :title="doc.sample ? '' : 'No document to preview yet'" @click="openPreview(doc)">
            Preview
          </button>
        </header>

        <div class="smj-print-controls">
          <label>
            <span>Retail ERP default</span>
            <select v-model="selected[doc.doctype]" :aria-label="`Default print format for ${doc.label}`">
              <option value="">Use ERPNext default</option>
              <option v-for="f in doc.formats" :key="f.name" :value="f.name">
                {{ f.name }}{{ f.is_standard ? " (Standard)" : "" }}
              </option>
            </select>
          </label>
          <label>
            <span>Language</span>
            <select v-model="selectedLanguage[doc.doctype]" :aria-label="`Print language for ${doc.label}`">
              <option value="">System default</option>
              <option v-for="lang in data?.languages || []" :key="lang" :value="lang">{{ lang }}</option>
            </select>
          </label>
          <button type="button" class="rug-primary" :disabled="busy" @click="saveDefault(doc)">Save default</button>
        </div>

        <div class="smj-print-controls">
          <label>
            <span>New custom format</span>
            <input v-model="newName[doc.doctype]" type="text" :placeholder="`${doc.label} — Retail ERP`" :aria-label="`New custom format name for ${doc.label}`" />
          </label>
          <button type="button" :disabled="busy" @click="duplicate(doc)">
            Create{{ selected[doc.doctype] ? ` from ${selected[doc.doctype]}` : " blank" }}
          </button>
        </div>

        <ul class="smj-print-formats">
          <li v-for="f in doc.formats" :key="f.name">
            <strong>{{ f.name }}</strong>
            <span :class="['smj-print-tag', f.is_standard ? 'is-standard' : 'is-custom']">
              {{ f.is_standard ? "Standard — protected" : "Custom" }}
            </span>
            <button v-if="!f.is_standard" type="button" :disabled="busy" @click="disableFormat(doc, f)">Disable</button>
          </li>
        </ul>
      </section>
    </main>

    <!-- Print preview: aligned, keyboard accessible, with working Close, Cancel and Print. -->
    <div v-if="preview" class="smj-print-modal" role="dialog" aria-modal="true" aria-labelledby="smj-print-modal-title" @click.self="closePreview">
      <section>
        <header>
          <div>
            <h2 id="smj-print-modal-title">Print preview</h2>
            <p>{{ preview.label }}<template v-if="preview.name"> · {{ preview.name }}</template></p>
          </div>
          <button ref="closeButton" type="button" class="smj-print-modal__close" aria-label="Close preview" @click="closePreview">×</button>
        </header>

        <div class="smj-print-modal__body">
          <p v-if="previewLoading" class="smj-print-modal__state">Loading preview…</p>
          <p v-else-if="previewError" class="rug-inline-error" role="alert">{{ previewError }}</p>
          <iframe v-else id="smj-print-frame" :srcdoc="preview.html" title="Print preview"></iframe>
        </div>

        <footer>
          <span class="smj-print-modal__meta">
            Format: {{ preview.print_format || "ERPNext default" }}<template v-if="preview.language"> · {{ preview.language }}</template>
          </span>
          <span class="smj-print-modal__actions">
            <button type="button" @click="closePreview">Cancel</button>
            <button type="button" class="rug-primary" :disabled="previewLoading || !!previewError" @click="printPreview">Print</button>
          </span>
        </footer>
      </section>
    </div>
  </PageContainer>
</template>
