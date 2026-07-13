<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getDocumentList, getListConfiguration } from "@/services/universal.js";

const route = useRoute(); const router = useRouter(); const loading = ref(true); const error = ref(null); const config = ref(null); const records = ref([]); const pagination = ref({ page: 1, pages: 1, total: 0 }); const search = ref(""); const filters = ref([]); const sortField = ref("modified"); const sortOrder = ref("desc"); let controller; let timer;
const feature = computed(() => String(route.params.feature || ""));
async function load() {
  controller?.abort(); controller = new AbortController(); loading.value = true; error.value = null;
  try {
    config.value ||= await getListConfiguration(feature.value, controller.signal);
    const result = await getDocumentList({ feature: feature.value, search: search.value, filters: filters.value, sort_field: sortField.value, sort_order: sortOrder.value, page: Number(route.query.page || 1), page_size: Number(route.query.page_size || 20) }, controller.signal);
    records.value = result.records; pagination.value = result.pagination;
  } catch (caught) { if (caught.name !== "AbortError") error.value = caught; }
  finally { loading.value = false; }
}
function schedule() { window.clearTimeout(timer); timer = window.setTimeout(() => { router.replace({ query: { ...route.query, page: 1, q: search.value || undefined } }); load(); }, 280); }
function sort(fieldname) { if (sortField.value === fieldname) sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc"; else { sortField.value = fieldname; sortOrder.value = "asc"; } load(); }
function setFilter(field, value) { filters.value = filters.value.filter((item) => item[0] !== field.fieldname); if (value !== "") filters.value.push([field.fieldname, "=", field.fieldtype === "Check" ? Number(value) : value]); load(); }
function open(name) { router.push(`/generated/${feature.value}/${encodeURIComponent(name)}`); }
watch(() => route.fullPath, () => { search.value = String(route.query.q || ""); config.value = null; load(); }, { immediate: true });
onBeforeUnmount(() => { controller?.abort(); window.clearTimeout(timer); });
</script>
<template>
  <PageContainer>
    <PermissionDenied v-if="error?.permissionDenied" />
    <ErrorState v-else-if="error" title="Unable to load generated feature" :message="error.message" />
    <div v-else class="ru-page">
      <header class="ru-page__header"><div><span class="ru-eyebrow">METADATA-DRIVEN · PROVISIONAL</span><h1>{{ config?.feature?.feature_label || 'Loading…' }}</h1><p>Permission-aware records generated from the installed ERPNext metadata.</p></div><button v-if="config?.permissions?.can_create" class="ref-button ref-button--primary" type="button" @click="router.push(`/generated/${feature}/new`)">+ Create</button></header>
      <section class="ru-toolbar" aria-label="List controls"><label><span>Search</span><input v-model="search" type="search" placeholder="Search permitted records…" @input="schedule" /></label><label v-for="field in config?.filter_fields || []" :key="field.fieldname"><span>{{ field.label }}</span><select v-if="field.fieldtype === 'Select'" @change="setFilter(field, $event.target.value)"><option value="">All</option><option v-for="option in field.options" :key="option">{{ option }}</option></select><select v-else-if="field.fieldtype === 'Check'" @change="setFilter(field, $event.target.value)"><option value="">All</option><option value="0">No</option><option value="1">Yes</option></select><input v-else-if="['Date','Datetime'].includes(field.fieldtype)" :type="field.fieldtype === 'Date' ? 'date' : 'datetime-local'" @change="setFilter(field, $event.target.value)" /></label><button type="button" @click="filters = []; search = ''; router.replace({ query: {} }); load()">Clear</button><button type="button" @click="load">Refresh</button></section>
      <div class="ru-count"><strong>{{ pagination.total }}</strong> records <span v-if="loading">Refreshing…</span></div>
      <div v-if="loading && !records.length" class="ru-skeleton" role="status"><i v-for="n in 8" :key="n"></i></div>
      <div v-else-if="!records.length" class="ru-empty"><h2>No records found</h2><p>Try changing the search or filters.</p></div>
      <div v-else class="ru-table-wrap"><table><thead><tr><th v-for="column in config.columns" :key="column.fieldname"><button type="button" @click="sort(column.fieldname)">{{ column.label }} <span v-if="sortField === column.fieldname">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></button></th></tr></thead><tbody><tr v-for="record in records" :key="record.name" tabindex="0" @click="open(record.name)" @keydown.enter="open(record.name)"><td v-for="column in config.columns" :key="column.fieldname" :data-label="column.label">{{ record[column.fieldname] ?? '—' }}</td></tr></tbody></table></div>
      <nav v-if="pagination.pages > 1" class="ru-pagination" aria-label="Pagination"><button :disabled="pagination.page <= 1" @click="router.push({ query: { ...route.query, page: pagination.page - 1 } })">Previous</button><span>Page {{ pagination.page }} of {{ pagination.pages }}</span><button :disabled="pagination.page >= pagination.pages" @click="router.push({ query: { ...route.query, page: pagination.page + 1 } })">Next</button></nav>
    </div>
  </PageContainer>
</template>
