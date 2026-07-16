<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import UniversalChildTable from "@/components/generated/UniversalChildTable.vue";
import UniversalCollaborationPanel from "@/components/generated/UniversalCollaborationPanel.vue";
import UniversalPrintDialog from "@/components/generated/UniversalPrintDialog.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import RecordNotFound from "@/components/feedback/RecordNotFound.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getDashboardConnections, getDocumentDetail, getPrintFormats, getRelated, getTimeline, runDocumentAction, runWorkflowAction } from "@/services/universal.js";
import { formatUniversalValue } from "@/utils/universalFormat.js";
import { confirmAction } from "@/composables/confirm.js";
import { useToast } from "@/composables/toast.js";

const toast = useToast();

const props = defineProps({ featureKey: { type: String, default: "" }, basePath: { type: String, default: "" }, recordName: { type: String, default: "" } });
const route = useRoute();
const router = useRouter();
const loading = ref(true);
const error = ref(null);
const detail = ref(null);
const timeline = ref([]);
const related = ref([]);
const connections = ref([]);
const printOptions = ref({});
const printOpen = ref(false);
const acting = ref(false);
let controller;

const feature = computed(() => props.featureKey || String(route.params.feature || ""));
const name = computed(() => props.recordName || String(route.params.name || ""));
const listPath = computed(() => props.basePath || `/generated/${feature.value}`);
const presentation = computed(() => detail.value?.metadata?.presentation || {});
const accent = computed(() => presentation.value.accent || "blue");
const title = computed(() => detail.value?.document?.[detail.value?.metadata?.title_field] || detail.value?.document?.name || "Record");
const status = computed(() => detail.value?.document?.status || detail.value?.document?.workflow_state || ["Draft", "Submitted", "Cancelled"][detail.value?.document?.docstatus || 0]);
const primaryNames = computed(() => new Set(presentation.value.primary_fields || []));
const importantFields = computed(() => (detail.value?.metadata?.fields || []).filter(
  (field) => primaryNames.value.has(field.fieldname) && !field.hidden && !["Table", "Table MultiSelect"].includes(field.fieldtype),
));
const sections = computed(() => {
  const result = [];
  let current = { key: "details", title: "Details", fields: [], tables: [] };
  const push = () => { if (current.fields.length || current.tables.length) result.push(current); };
  for (const field of detail.value?.metadata?.fields || []) {
    if (field.hidden || primaryNames.value.has(field.fieldname)) continue;
    if (["Section Break", "Tab Break"].includes(field.fieldtype)) {
      push(); current = { key: field.fieldname, title: field.label || "Details", fields: [], tables: [] };
    } else if (["Table", "Table MultiSelect"].includes(field.fieldtype)) current.tables.push(field);
    else if (!["Column Break", "Button", "HTML"].includes(field.fieldtype)) current.fields.push(field);
  }
  push();
  return result;
});

function advanced(section, index) {
  return ![...section.fields, ...section.tables].some((field) => field.required)
    && (index > 3 || /additional|advanced|website|account|setting|default|integration|printing/i.test(section.title));
}

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    detail.value = await getDocumentDetail(feature.value, name.value, controller.signal);
    const [activity, links, connected, printing] = await Promise.allSettled([
      getTimeline(feature.value, name.value, controller.signal),
      getRelated(feature.value, name.value, controller.signal),
      getDashboardConnections(feature.value, name.value, controller.signal),
      detail.value.permissions.can_print ? getPrintFormats(feature.value, name.value, controller.signal) : Promise.resolve({}),
    ]);
    timeline.value = activity.value?.records || [];
    related.value = links.value?.records || [];
    connections.value = connected.value?.groups || [];
    printOptions.value = printing.value || {};
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

function actionParameters(action) {
  const parameters = {};
  for (const field of action.requires_parameters || []) {
    const defaultValue = field === "items_json"
      ? JSON.stringify((detail.value?.document?.items || []).map((row) => ({
        docname: row.name,
        item_code: row.item_code,
        item_name: row.item_name,
        qty: row.qty,
        rate: row.rate,
        uom: row.uom,
        conversion_factor: row.conversion_factor,
        schedule_date: row.schedule_date,
        fg_item: row.fg_item,
        fg_item_qty: row.fg_item_qty,
        idx: row.idx,
      })), null, 2)
      : "";
    const value = window.prompt(`Enter ${field.replaceAll("_", " ")}`, defaultValue);
    if (!value) return null;
    parameters[field] = value;
  }
  if (action.action === "rename") {
    const value = window.prompt("Enter the new document name", name.value);
    if (!value) return null;
    parameters.new_name = value;
  }
  return parameters;
}

async function act(action) {
  if (acting.value) return;
  const parameters = actionParameters(action);
  if (parameters === null) return;
  if (action.action !== "rename") {
    const confirmed = await confirmAction({
      title: `${action.label} ${name.value}?`,
      confirmLabel: action.label,
      danger: ["cancel", "delete"].includes(action.action),
    });
    if (!confirmed) return;
  }
  acting.value = true;
  error.value = null;
  try {
    const result = action.kind === "workflow"
      ? await runWorkflowAction(feature.value, name.value, action.action, detail.value.document.modified)
      : await runDocumentAction(feature.value, name.value, action.action, detail.value.document.modified, parameters);
    toast.success(`${action.label} complete`, `${name.value} was updated.`);
    if (result.download_url) window.location.assign(result.download_url);
    else if (result.route && result.route !== route.path) await router.push(result.route);
    else await load();
  } catch (caught) {
    error.value = caught;
    toast.error("Action failed", caught.message);
  } finally {
    acting.value = false;
  }
}

watch(() => [feature.value, name.value, route.path], load, { immediate: true });
onBeforeUnmount(() => controller?.abort());
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="error?.permissionDenied" />
    <RecordNotFound v-else-if="error?.notFound" />
    <ErrorState v-else-if="error && !detail" title="Unable to load document" :message="error.message" />
    <main v-else-if="detail" class="rug-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/home">Home</RouterLink><span>›</span><RouterLink :to="listPath">{{ presentation.plural || detail.metadata.label }}</RouterLink><span>›</span><strong>{{ detail.document.name }}</strong></nav>
      <header :class="['rug-banner', `rug-banner--${accent}`]">
        <div><span class="rug-badge">Retail ERP page</span><div class="rug-title-line"><h1>{{ title }}</h1><span class="rug-status">{{ status }}</span></div><p>{{ detail.document.name }} · Updated {{ detail.document.modified }}</p></div>
        <div class="rug-banner-actions"><button type="button" @click="router.push(listPath)">Back to list</button><button v-if="detail.permissions.can_write && detail.document.docstatus === 0" class="rug-primary" type="button" @click="router.push(`${listPath}/${encodeURIComponent(name)}/edit`)">Edit</button><button v-if="detail.permissions.can_print" type="button" @click="printOpen = true">Print / PDF</button><details v-if="detail.actions.length"><summary>Actions</summary><div class="rug-action-menu"><button v-for="action in detail.actions" :key="action.action" type="button" :disabled="acting" :class="{ 'is-danger': action.destructive }" @click="act(action)">{{ action.label }}</button></div></details></div>
      </header>
      <div v-if="error" class="rug-inline-error" role="alert">{{ error.message }}</div>
      <section v-if="importantFields.length" class="rug-summary-grid"><article v-for="field in importantFields" :key="field.fieldname"><span>{{ field.label }}</span><strong>{{ formatUniversalValue(detail.document[field.fieldname], field, detail.document.currency) }}</strong></article><article><span>Owner</span><strong>{{ detail.document.owner }}</strong></article></section>
      <template v-for="(section, index) in sections.filter((item, position) => !advanced(item, position))" :key="section.key"><section v-if="section.fields.length" class="rug-section-card"><header><h2>{{ section.title }}</h2></header><dl class="rug-detail-grid"><div v-for="field in section.fields" :key="field.fieldname"><dt>{{ field.label }}</dt><dd>{{ formatUniversalValue(detail.document[field.fieldname], field, detail.document.currency) }}</dd></div></dl></section><UniversalChildTable v-for="table in section.tables" :key="table.fieldname" :model-value="detail.document[table.fieldname] || []" :field="table" :feature="feature" read-only /></template>
      <details v-if="sections.some(advanced)" class="rug-advanced"><summary>Advanced information</summary><template v-for="(section, index) in sections" :key="section.key"><section v-if="advanced(section, index) && section.fields.length" class="rug-section-card"><header><h2>{{ section.title }}</h2></header><dl class="rug-detail-grid"><div v-for="field in section.fields" :key="field.fieldname"><dt>{{ field.label }}</dt><dd>{{ formatUniversalValue(detail.document[field.fieldname], field, detail.document.currency) }}</dd></div></dl></section><UniversalChildTable v-for="table in advanced(section, index) ? section.tables : []" :key="table.fieldname" :model-value="detail.document[table.fieldname] || []" :field="table" :feature="feature" read-only /></template></details>
      <section class="rug-section-card"><header><h2>Related records</h2></header><div v-if="!related.length" class="rug-muted">No permitted related records.</div><RouterLink v-for="record in related" :key="`${record.doctype}-${record.name}`" :to="record.route" class="rug-related">{{ record.doctype }}<strong>{{ record.name }}</strong></RouterLink></section>
      <section v-if="connections.length" class="rug-section-card"><header><h2>Linked documents</h2><p>Documents connected to this record through standard ERPNext links.</p></header>
        <div v-for="group in connections" :key="group.label" class="rug-connection-group">
          <h3>{{ group.label }}</h3>
          <div v-for="item in group.items" :key="item.doctype" class="rug-connection-item">
            <span>{{ item.doctype }}<small>{{ item.count }} linked</small></span>
            <RouterLink v-for="linked in item.records" :key="linked.name" :to="linked.route" class="rug-related">{{ linked.name }}</RouterLink>
          </div>
        </div>
      </section>
      <UniversalCollaborationPanel :feature="feature" :name="name" :print-options="printOptions" />
      <section class="rug-section-card"><header><h2>Timeline</h2><button type="button" @click="load">Refresh</button></header><div v-if="!timeline.length" class="rug-muted">No recent activity.</div><article v-for="event in timeline" :key="event.name" class="rug-timeline"><span class="rug-timeline__dot" /><div><strong>{{ event.comment_type }}</strong><p>{{ event.content }}</p><small>{{ event.owner }} · {{ event.creation }}</small></div></article></section>
      <UniversalPrintDialog :open="printOpen" :options="printOptions" :document="detail.document" @close="printOpen = false" />
    </main>
    <div v-else class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
  </PageContainer>
</template>
