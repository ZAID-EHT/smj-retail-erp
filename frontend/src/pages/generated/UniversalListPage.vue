<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getDocumentList, getListConfiguration } from "@/services/universal.js";
import { formatUniversalValue, isBadgeColumn } from "@/utils/universalFormat.js";

const route = useRoute(); const router = useRouter(); const loading = ref(true); const error = ref(null); const config = ref(null); const records = ref([]); const columns = ref([]); const selectedColumns = ref([]); const pagination = ref({ page: 1, pages: 1, total: 0 }); const search = ref(""); const appliedFilters = reactive({}); const draftFilters = reactive({}); const moreOpen = ref(false); const columnsOpen = ref(false); const sortField = ref("modified"); const sortOrder = ref("desc"); let controller; let timer;
const feature = computed(() => String(route.params.feature || ""));
const title = computed(() => config.value?.presentation?.plural || config.value?.feature?.feature_label || "Records");
const accent = computed(() => config.value?.presentation?.accent || "blue");
const activeChips = computed(() => Object.entries(appliedFilters).filter(([, value]) => value !== "" && value != null).map(([fieldname, value]) => ({ fieldname, value, label: config.value?.filter_fields?.find((field) => field.fieldname === fieldname)?.label || fieldname })));
const preferenceKey = computed(() => `retail-erp:list:${window.frappe?.session?.user || "user"}:${feature.value}`);
function readPreferences() { try { return JSON.parse(localStorage.getItem(preferenceKey.value) || "{}"); } catch { return {}; } }
function savePreferences() { localStorage.setItem(preferenceKey.value, JSON.stringify({ columns: selectedColumns.value, pageSize: Number(route.query.page_size || 20) })); }
function filterArray() { return Object.entries(appliedFilters).filter(([, value]) => value !== "" && value != null).map(([fieldname, value]) => [fieldname, "=", value]); }
async function load({ resetConfig = false } = {}) {
  controller?.abort(); controller = new AbortController(); loading.value = true; error.value = null;
  try {
    if (resetConfig || !config.value) {
      config.value = await getListConfiguration(feature.value, controller.signal);
      const preferences = readPreferences(); const allowed = new Set(config.value.all_columns.map((column) => column.fieldname));
      selectedColumns.value = (preferences.columns || config.value.default_columns).filter((fieldname) => allowed.has(fieldname)).slice(0, 12);
      if (!selectedColumns.value.length) selectedColumns.value = [...config.value.default_columns];
    }
    const result = await getDocumentList({ feature: feature.value, search: search.value, filters: filterArray(), columns: selectedColumns.value, sort_field: sortField.value, sort_order: sortOrder.value, page: Number(route.query.page || 1), page_size: Number(route.query.page_size || 20) }, controller.signal);
    records.value = result.records; columns.value = result.columns; pagination.value = result.pagination;
  } catch (caught) { if (caught.name !== "AbortError") error.value = caught; }
  finally { loading.value = false; }
}
function scheduleSearch() { window.clearTimeout(timer); timer = window.setTimeout(() => { router.replace({ query: { ...route.query, page: 1, q: search.value || undefined } }); load(); }, 300); }
function sort(fieldname) { if (!config.value.sortable_fields.includes(fieldname)) return; if (sortField.value === fieldname) sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc"; else { sortField.value = fieldname; sortOrder.value = "asc"; } load(); }
function applyFilters() { Object.keys(appliedFilters).forEach((key) => delete appliedFilters[key]); Object.assign(appliedFilters, draftFilters); moreOpen.value = false; router.replace({ query: { ...route.query, page: 1 } }); load(); }
function clearFilters() { Object.keys(appliedFilters).forEach((key) => delete appliedFilters[key]); Object.keys(draftFilters).forEach((key) => delete draftFilters[key]); moreOpen.value = false; load(); }
function removeFilter(fieldname) { delete appliedFilters[fieldname]; delete draftFilters[fieldname]; load(); }
function toggleColumn(fieldname) { selectedColumns.value = selectedColumns.value.includes(fieldname) ? selectedColumns.value.filter((name) => name !== fieldname) : [...selectedColumns.value, fieldname].slice(0, 12); if (!selectedColumns.value.length) selectedColumns.value = ["name"]; savePreferences(); load(); }
function open(name) { router.push(`/generated/${feature.value}/${encodeURIComponent(name)}`); }
watch(() => route.params.feature, () => { search.value = String(route.query.q || ""); config.value = null; Object.keys(appliedFilters).forEach((key) => delete appliedFilters[key]); Object.keys(draftFilters).forEach((key) => delete draftFilters[key]); load({ resetConfig: true }); }, { immediate: true });
watch(() => route.query.page, () => { if (config.value) load(); });
onBeforeUnmount(() => { controller?.abort(); window.clearTimeout(timer); });
</script>

<template><PageContainer><PermissionDenied v-if="error?.permissionDenied" /><ErrorState v-else-if="error" title="Unable to load records" :message="error.message" /><main v-else class="rug-page">
  <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/home">Home</RouterLink><span>›</span><span>{{ config?.feature?.module || 'Records' }}</span><span>›</span><strong>{{ title }}</strong></nav>
  <header :class="['rug-banner', `rug-banner--${accent}`]"><div><span class="rug-badge">Generated page</span><h1>{{ title }}</h1><p>{{ config?.presentation?.description || `Browse and manage permitted ${title.toLowerCase()}.` }}</p></div><button v-if="config?.permissions?.can_create" class="rug-primary" type="button" @click="router.push(`/generated/${feature}/new`)">+ New {{ config.feature.feature_label }}</button></header>
  <section class="rug-list-card">
    <div class="rug-list-toolbar"><label class="rug-search"><span class="sr-only">Search</span><input v-model="search" type="search" placeholder="Search by name or ID…" @input="scheduleSearch" /></label><button type="button" @click="moreOpen = !moreOpen">Filters <b v-if="activeChips.length">{{ activeChips.length }}</b></button><div class="rug-popover-wrap"><button type="button" @click="columnsOpen = !columnsOpen">Columns</button><div v-if="columnsOpen" class="rug-popover"><strong>Visible columns</strong><label v-for="column in config?.all_columns || []" :key="column.fieldname"><input type="checkbox" :checked="selectedColumns.includes(column.fieldname)" @change="toggleColumn(column.fieldname)" />{{ column.label }}</label><button type="button" @click="selectedColumns = [...config.default_columns]; savePreferences(); columnsOpen = false; load()">Restore defaults</button></div></div><button type="button" :disabled="loading" @click="load">Refresh</button></div>
    <div class="rug-primary-filters"><label v-for="field in config?.main_filters || []" :key="field.fieldname"><span>{{ field.label }}</span><select v-if="field.fieldtype === 'Select'" v-model="draftFilters[field.fieldname]"><option value="">All</option><option v-for="option in field.options" :key="option">{{ option }}</option></select><select v-else-if="field.fieldtype === 'Check'" v-model="draftFilters[field.fieldname]"><option value="">All</option><option :value="1">Yes</option><option :value="0">No</option></select><input v-else v-model="draftFilters[field.fieldname]" :type="['Date','Datetime'].includes(field.fieldtype) ? 'date' : 'search'" /></label><button class="rug-apply" type="button" @click="applyFilters">Apply</button></div>
    <aside v-if="moreOpen" class="rug-filter-drawer"><header><div><h2>More filters</h2><p>All additional fields available to your permission level.</p></div><button type="button" @click="moreOpen = false" aria-label="Close filters">×</button></header><div class="rug-filter-grid"><label v-for="field in config?.more_filters || []" :key="field.fieldname"><span>{{ field.label }}</span><select v-if="field.fieldtype === 'Select'" v-model="draftFilters[field.fieldname]"><option value="">All</option><option v-for="option in field.options" :key="option">{{ option }}</option></select><select v-else-if="field.fieldtype === 'Check'" v-model="draftFilters[field.fieldname]"><option value="">All</option><option :value="1">Yes</option><option :value="0">No</option></select><input v-else v-model="draftFilters[field.fieldname]" :type="['Date','Datetime'].includes(field.fieldtype) ? 'date' : 'search'" /></label></div><footer><button type="button" @click="clearFilters">Clear all</button><button class="rug-primary" type="button" @click="applyFilters">Apply filters</button></footer></aside>
    <div v-if="activeChips.length" class="rug-chips"><button v-for="chip in activeChips" :key="chip.fieldname" type="button" @click="removeFilter(chip.fieldname)">{{ chip.label }}: {{ chip.value }} <span>×</span></button><button type="button" @click="clearFilters">Clear all</button></div>
    <div class="rug-count"><span><strong>{{ pagination.total }}</strong> records</span><span v-if="loading">Refreshing…</span></div>
    <div v-if="loading && !records.length" class="rug-skeleton" role="status"><i v-for="n in 8" :key="n" /></div><div v-else-if="!records.length" class="rug-empty"><span>⌕</span><h2>No {{ title.toLowerCase() }} found</h2><p>Try changing the search or filters.</p></div>
    <div v-else class="rug-table-region"><table><thead><tr><th v-for="column in columns" :key="column.fieldname"><button type="button" @click="sort(column.fieldname)">{{ column.label }}<span v-if="sortField === column.fieldname">{{ sortOrder === 'asc' ? ' ↑' : ' ↓' }}</span></button></th></tr></thead><tbody><tr v-for="record in records" :key="record.name" tabindex="0" @click="open(record.name)" @keydown.enter="open(record.name)"><td v-for="column in columns" :key="column.fieldname" :data-label="column.label"><span v-if="isBadgeColumn(column)" :class="['rug-value-badge', `is-${String(record[column.fieldname]).toLowerCase().replace(/\s+/g,'-')}`]">{{ formatUniversalValue(record[column.fieldname], column, record.currency) }}</span><span v-else>{{ formatUniversalValue(record[column.fieldname], column, record.currency) }}</span></td></tr></tbody></table></div>
    <nav v-if="pagination.pages > 1" class="rug-pagination" aria-label="Pagination"><button :disabled="pagination.page <= 1" @click="router.push({ query: { ...route.query, page: pagination.page - 1 } })">← Previous</button><span>Page {{ pagination.page }} of {{ pagination.pages }}</span><button :disabled="pagination.page >= pagination.pages" @click="router.push({ query: { ...route.query, page: pagination.page + 1 } })">Next →</button></nav>
  </section>
</main></PageContainer></template>
