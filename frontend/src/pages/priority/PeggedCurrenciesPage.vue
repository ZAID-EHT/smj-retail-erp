<script setup>
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { onBeforeRouteLeave } from "vue-router";
import UniversalChildTable from "@/components/generated/UniversalChildTable.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getDocumentDetail, getMetadata, updateDocument } from "@/services/universal.js";

const FEATURE = "pegged-currencies";
const NAME = "Pegged Currencies";
const loading = ref(true);
const saving = ref(false);
const metadata = ref(null);
const error = ref(null);
const success = ref("");
const values = reactive({ pegged_currency_item: [], modified: null });
const dirty = ref(false);
let controller;

const table = computed(() => metadata.value?.fields?.find((field) => field.fieldname === "pegged_currency_item"));
const canWrite = computed(() => Boolean(metadata.value?.permissions?.can_write));

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  success.value = "";
  try {
    const [meta, detail] = await Promise.all([
      getMetadata(FEATURE, controller.signal),
      getDocumentDetail(FEATURE, NAME, controller.signal),
    ]);
    metadata.value = meta;
    values.pegged_currency_item = detail.document.pegged_currency_item || [];
    values.modified = detail.document.modified;
    dirty.value = false;
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}
function updateRows(rows) {
  values.pegged_currency_item = rows;
  dirty.value = true;
  success.value = "";
}
async function save() {
  if (!canWrite.value || saving.value) return;
  saving.value = true;
  error.value = null;
  success.value = "";
  try {
    const result = await updateDocument(FEATURE, NAME, { pegged_currency_item: values.pegged_currency_item }, values.modified);
    values.modified = result.modified;
    dirty.value = false;
    success.value = "Pegged currency settings saved through ERPNext.";
  } catch (caught) {
    error.value = caught;
  } finally {
    saving.value = false;
  }
}
function beforeUnload(event) {
  if (!dirty.value) return;
  event.preventDefault();
  event.returnValue = "";
}
onBeforeRouteLeave(() => !dirty.value || window.confirm("Leave this page? Unsaved pegged-currency changes will be lost."));
window.addEventListener("beforeunload", beforeUnload);
onBeforeUnmount(() => {
  controller?.abort();
  window.removeEventListener("beforeunload", beforeUnload);
});
load();
</script>

<template>
  <PermissionDenied v-if="error?.permissionDenied" />
  <PageContainer v-else>
    <main class="rug-page pegged-currencies-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/finance">Finance</RouterLink><span>›</span><strong>Pegged Currencies</strong></nav>
      <header class="rug-banner rug-banner--purple">
        <div><span class="rug-badge">System Manager setting</span><h1>Pegged Currencies</h1><p>Maintain currency pairs and their pegged exchange rates in ERPNext's standard Single DocType.</p></div>
        <div class="rug-banner-actions"><button type="button" :disabled="loading" @click="load">Refresh</button><button class="rug-primary" type="button" :disabled="!canWrite || !dirty || saving" @click="save">{{ saving ? "Saving…" : "Save" }}</button></div>
      </header>
      <ErrorState v-if="error" title="Unable to load Pegged Currencies" :message="error.message" @retry="load" />
      <p v-if="success" class="rug-success" role="status">{{ success }}</p>
      <div v-if="loading" class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
      <UniversalChildTable v-else-if="table" :model-value="values.pegged_currency_item" :field="table" :feature="FEATURE" :read-only="!canWrite || table.read_only" @update:model-value="updateRows" />
      <section v-else-if="!error" class="rug-section-card"><h2>Configuration unavailable</h2><p>The installed ERPNext metadata does not expose the expected Pegged Currency Details table.</p></section>
      <footer v-if="table" class="rug-sticky-actions"><span v-if="dirty">Unsaved changes</span><button type="button" :disabled="loading" @click="load">Discard changes</button><button class="rug-primary" type="button" :disabled="!canWrite || !dirty || saving" @click="save">{{ saving ? "Saving…" : "Save" }}</button></footer>
    </main>
  </PageContainer>
</template>

<style scoped>
.rug-success { border: 1px solid var(--ref-success); border-radius: .75rem; padding: .8rem 1rem; background: var(--ref-success-background); color: var(--ref-primary-text); }
</style>
