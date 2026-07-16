<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { onBeforeRouteLeave, useRoute, useRouter } from "vue-router";
import UniversalChildTable from "@/components/generated/UniversalChildTable.vue";
import UniversalField from "@/components/generated/UniversalField.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { createDocument, getDocumentDetail, getMetadata, updateDocument } from "@/services/universal.js";

const props = defineProps({
  featureKey: { type: String, default: "" },
  basePath: { type: String, default: "" },
  recordName: { type: String, default: "" },
  defaults: { type: Object, default: () => ({}) },
	stayOnSave: { type: Boolean, default: false },
});
const route = useRoute();
const router = useRouter();
const loading = ref(true);
const saving = ref(false);
const error = ref(null);
const metadata = ref(null);
const values = reactive({});
const errors = reactive({});
const dirty = ref(false);
let controller;

const feature = computed(() => props.featureKey || String(route.params.feature || ""));
const name = computed(() => props.recordName || (route.params.name ? String(route.params.name) : ""));
const editing = computed(() => Boolean(name.value));
const listPath = computed(() => props.basePath || `/generated/${feature.value}`);
const presentation = computed(() => metadata.value?.presentation || {});
const accent = computed(() => presentation.value.accent || "blue");
const primaryNames = computed(() => new Set(presentation.value.primary_fields || []));
const visibleFields = computed(() => (metadata.value?.fields || []).filter(
  (field) => !field.hidden && !["Section Break", "Column Break", "Tab Break", "Table", "Table MultiSelect", "Button", "HTML"].includes(field.fieldtype),
));
const tables = computed(() => (metadata.value?.fields || []).filter(
  (field) => !field.hidden && ["Table", "Table MultiSelect"].includes(field.fieldtype),
));
const primaryFields = computed(() => visibleFields.value.filter((field) => primaryNames.value.has(field.fieldname)));
const sections = computed(() => {
  const result = [];
  let current = { key: "details", title: "Details", fields: [], tables: [] };
  const push = () => { if (current.fields.length || current.tables.length) result.push(current); };
  for (const field of metadata.value?.fields || []) {
    if (field.hidden) continue;
    if (["Section Break", "Tab Break"].includes(field.fieldtype)) {
      push(); current = { key: field.fieldname, title: field.label || "Details", fields: [], tables: [] };
    } else if (["Table", "Table MultiSelect"].includes(field.fieldtype)) current.tables.push(field);
    else if (!["Column Break", "Button", "HTML"].includes(field.fieldtype) && !primaryNames.value.has(field.fieldname)) current.fields.push(field);
  }
  push();
  return result;
});

function advanced(section, index) {
  const containsRequiredInput = [...section.fields, ...section.tables].some((field) => field.required && !field.read_only);
  return !containsRequiredInput && (index > 3 || /additional|advanced|website|account|setting|default|integration|printing/i.test(section.title));
}

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  Object.keys(values).forEach((key) => delete values[key]);
  try {
    metadata.value = await getMetadata(feature.value, controller.signal);
    if (editing.value) {
      const result = await getDocumentDetail(feature.value, name.value, controller.signal);
      Object.assign(values, result.document);
    } else {
      Object.assign(values, metadata.value.defaults || {}, props.defaults || {});
      for (const field of metadata.value.fields) {
        if (["Table", "Table MultiSelect"].includes(field.fieldtype) && !Array.isArray(values[field.fieldname])) values[field.fieldname] = [];
      }
    }
    dirty.value = false;
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

function change(fieldname, value) {
  values[fieldname] = value;
  delete errors[fieldname];
  dirty.value = true;
}

function validate() {
  Object.keys(errors).forEach((key) => delete errors[key]);
  for (const field of visibleFields.value) {
    if (field.required && !field.read_only && [undefined, null, ""].includes(values[field.fieldname])) errors[field.fieldname] = `${field.label} is required.`;
  }
  for (const table of tables.value) {
    if (table.required && !table.read_only && !(values[table.fieldname] || []).length) errors[table.fieldname] = `${table.label} requires at least one row.`;
  }
  return !Object.keys(errors).length;
}

function payload() {
  const allowed = [...visibleFields.value, ...tables.value].filter((field) => !field.read_only).map((field) => field.fieldname);
  return Object.fromEntries(allowed.filter((key) => key in values).map((key) => [key, values[key]]));
}

async function save(continueEditing = false) {
  if (saving.value || !validate()) return;
  saving.value = true;
  error.value = null;
  try {
    const result = editing.value
      ? await updateDocument(feature.value, name.value, payload(), values.modified)
      : await createDocument(feature.value, payload());
    dirty.value = false;
		if (props.stayOnSave) {
			values.modified = result.modified;
			return;
		}
    if (continueEditing) await router.replace(`${listPath.value}/${encodeURIComponent(result.name)}/edit`);
    else await router.push(result.route);
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

onBeforeRouteLeave(() => !dirty.value || window.confirm("Leave this page? Unsaved changes will be lost."));
watch(() => [feature.value, name.value, route.path], load, { immediate: true });
window.addEventListener("beforeunload", beforeUnload);
onBeforeUnmount(() => {
  controller?.abort();
  window.removeEventListener("beforeunload", beforeUnload);
});
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="error?.permissionDenied" />
    <ErrorState v-else-if="error && !metadata" title="Unable to load form" :message="error.message" />
    <form v-else-if="metadata" class="rug-page rug-form-page" @submit.prevent="save(false)">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span>
        <RouterLink :to="listPath">{{ presentation.plural || metadata.label }}</RouterLink><span>›</span>
        <strong>{{ editing ? name : `New ${metadata.label}` }}</strong>
      </nav>
      <header :class="['rug-banner', `rug-banner--${accent}`]">
        <div><span class="rug-badge">Retail ERP page</span><h1>{{ editing ? `Edit ${metadata.label}` : `New ${metadata.label}` }}</h1><p>{{ presentation.description || `Enter the required ${metadata.label.toLowerCase()} information.` }}</p></div>
        <div class="rug-banner-actions"><button type="button" @click="router.back()">Cancel</button><button class="rug-primary" type="submit" :disabled="saving">{{ saving ? "Saving…" : "Save" }}</button></div>
      </header>
      <nav v-if="sections.length > 1" class="rug-section-nav" aria-label="Form sections">
        <a v-if="primaryFields.length" href="#rug-primary-fields">Overview</a>
        <a v-for="(section, index) in sections.filter((item, position) => !advanced(item, position))" :key="section.key" :href="`#rug-section-${section.key}`">{{ section.title }}</a>
        <a v-if="sections.some(advanced)" href="#rug-advanced">Advanced</a>
      </nav>
      <div v-if="error" class="rug-inline-error" role="alert"><strong>Unable to save record</strong><span>{{ error.message }}</span></div>
      <div v-if="Object.keys(errors).length" class="rug-inline-error" role="alert"><strong>Check the highlighted fields</strong><span v-for="message in errors" :key="message">{{ message }}</span></div>
      <section v-if="primaryFields.length" id="rug-primary-fields" class="rug-section-card">
        <header><div><h2>Overview</h2><p>The most important information for this record.</p></div></header>
        <div class="rug-form-grid"><UniversalField v-for="field in primaryFields" :key="field.fieldname" :model-value="values[field.fieldname]" :field="field" :feature="feature" :context="values" :error="errors[field.fieldname]" @update:model-value="change(field.fieldname, $event)" /></div>
      </section>
      <template v-for="(section, index) in sections" :key="section.key">
        <template v-if="!advanced(section, index)">
          <section v-if="section.fields.length" :id="`rug-section-${section.key}`" class="rug-section-card"><header><h2>{{ section.title }}</h2></header><div class="rug-form-grid"><UniversalField v-for="field in section.fields" :key="field.fieldname" :model-value="values[field.fieldname]" :field="field" :feature="feature" :context="values" :error="errors[field.fieldname]" @update:model-value="change(field.fieldname, $event)" /></div></section>
          <div v-for="table in section.tables" :key="table.fieldname" :class="{ 'rug-section-error': errors[table.fieldname] }"><UniversalChildTable :model-value="values[table.fieldname] || []" :field="table" :feature="feature" :read-only="table.read_only" @update:model-value="change(table.fieldname, $event)" /><p v-if="errors[table.fieldname]" class="rug-inline-error">{{ errors[table.fieldname] }}</p></div>
        </template>
      </template>
      <details v-if="sections.some(advanced)" id="rug-advanced" class="rug-advanced"><summary>Advanced information</summary><template v-for="(section, index) in sections" :key="section.key"><template v-if="advanced(section, index)"><section v-if="section.fields.length" class="rug-section-card"><header><h2>{{ section.title }}</h2></header><div class="rug-form-grid"><UniversalField v-for="field in section.fields" :key="field.fieldname" :model-value="values[field.fieldname]" :field="field" :feature="feature" :context="values" :error="errors[field.fieldname]" @update:model-value="change(field.fieldname, $event)" /></div></section><UniversalChildTable v-for="table in section.tables" :key="table.fieldname" :model-value="values[table.fieldname] || []" :field="table" :feature="feature" :read-only="table.read_only" @update:model-value="change(table.fieldname, $event)" /></template></template></details>
      <footer class="rug-sticky-actions"><span v-if="dirty">Unsaved changes</span><button type="button" @click="router.back()">Cancel</button><button type="button" :disabled="saving" @click="save(true)">Save and continue</button><button class="rug-primary" type="submit" :disabled="saving">{{ saving ? "Saving…" : "Save" }}</button></footer>
    </form>
    <div v-else class="rug-skeleton"><i v-for="n in 10" :key="n" /></div>
  </PageContainer>
</template>
