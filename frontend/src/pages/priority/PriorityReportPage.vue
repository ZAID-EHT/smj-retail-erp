<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getPriorityReportDefinition, runPriorityReport } from "@/services/priority.js";
import { formatUniversalValue } from "@/utils/universalFormat.js";

const props = defineProps({ reportName: { type: String, required: true } });
const definition = ref(null);
const result = ref(null);
const filters = reactive({});
const error = ref(null);
const running = ref(false);
let controller;
const columns = computed(() => (result.value?.columns || []).map((column, index) => (
  typeof column === "string"
    ? { fieldname: `column_${index}`, label: column.split(":")[0], fieldtype: "Data", index }
    : { ...column, index }
)).filter((column) => !column.hidden));
const rows = computed(() => result.value?.result || []);
const chart = computed(() => { const data = result.value?.chart?.data; const dataset = data?.datasets?.[0]; return (data?.labels || []).map((label, index) => ({ label, value: Number(dataset?.values?.[index] ?? dataset?.data?.[index] ?? 0) })).slice(0, 30); });
const chartMaximum = computed(() => Math.max(1, ...chart.value.map((item) => Math.abs(item.value))));
function cell(row, column) { return Array.isArray(row) ? row[column.index] : row?.[column.fieldname]; }
function cellLink(row, column) { const doctype = column.fieldtype === "Dynamic Link" ? row?.[column.options] : column.options; return result.value?.retail_links?.[`${doctype}:${cell(row, column)}`]; }
async function load() {
  controller?.abort(); controller = new AbortController(); error.value = null; result.value = null;
  try {
    definition.value = await getPriorityReportDefinition(props.reportName, controller.signal);
    Object.keys(filters).forEach((key) => delete filters[key]);
    for (const field of definition.value.filters) if (field.default != null) filters[field.fieldname] = field.default;
  } catch (caught) { if (caught.name !== "AbortError") error.value = caught; }
}
async function run() {
  if (running.value) return;
  running.value = true; error.value = null;
  try { result.value = await runPriorityReport(props.reportName, filters, controller?.signal); }
  catch (caught) { error.value = caught; }
  finally { running.value = false; }
}
function exportCsv() {
  const quote = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const lines = [columns.value.map((column) => quote(column.label)).join(","), ...rows.value.map((row) => columns.value.map((column) => quote(cell(row, column))).join(","))];
  const url = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/csv" }));
  const anchor = document.createElement("a"); anchor.href = url; anchor.download = `${props.reportName}.csv`; anchor.click(); URL.revokeObjectURL(url);
}
watch(() => props.reportName, load, { immediate: true });
onBeforeUnmount(() => controller?.abort());
</script>

<template>
  <PageContainer>
    <ErrorState v-if="error && !definition" title="Unable to load report" :message="error.message" @retry="load" />
    <main v-else-if="definition" class="rug-page">
      <nav class="rug-breadcrumbs"><RouterLink to="/home">Home</RouterLink><span>›</span><RouterLink to="/reports">Reports</RouterLink><span>›</span><strong>{{ reportName }}</strong></nav>
      <header class="rug-banner"><div><span class="rug-badge">ERPNext report</span><h1>{{ reportName }}</h1><p>{{ definition.report_type }} report · calculations run on the ERPNext server.</p></div><div class="rug-banner-actions"><button v-if="rows.length && definition.permissions.can_export" type="button" @click="exportCsv">Export CSV</button><button v-if="rows.length && definition.permissions.can_print" type="button" @click="window.print()">Print Preview</button><button class="rug-primary" type="button" :disabled="running" @click="run">{{ running ? "Running…" : "Run report" }}</button></div></header>
      <section class="rug-section-card"><header><div><h2>Report filters</h2><p>Required defaults are loaded from your ERPNext session.</p></div></header><div class="rug-form-grid"><label v-for="field in definition.filters" :key="field.fieldname" class="priority-report-filter"><span>{{ field.label }}<b v-if="field.required"> *</b></span><select v-if="field.fieldtype === 'Select'" v-model="filters[field.fieldname]"><option value="">Choose…</option><option v-for="option in field.options" :key="option">{{ option }}</option></select><input v-else v-model="filters[field.fieldname]" :type="field.fieldtype === 'Date' ? 'date' : 'text'" :required="field.required" :placeholder="field.options ? `Enter permitted ${field.options}` : ''" /></label></div></section>
      <div v-if="error" class="rug-inline-error">{{ error.message }}</div>
      <section v-if="chart.length" class="rug-section-card"><header><div><h2>Chart</h2><p>Chart data returned by the installed ERPNext report.</p></div></header><div class="priority-report-chart"><div v-for="item in chart" :key="item.label"><span>{{ item.label }}</span><i :style="{ width: `${Math.max(2, Math.abs(item.value) / chartMaximum * 100)}%` }" /><strong>{{ item.value }}</strong></div></div></section>
      <section v-if="result" class="rug-list-card"><div class="rug-count"><span><strong>{{ rows.length }}</strong> rows</span><span v-if="result.execution_time">{{ result.execution_time }} seconds</span></div><div v-if="result.message" class="rug-warning">{{ result.message }}</div><div v-if="!rows.length" class="rug-empty"><h2>No report rows</h2><p>Try changing the filters.</p></div><div v-else class="rug-table-region"><table><thead><tr><th v-for="column in columns" :key="column.fieldname">{{ column.label }}</th></tr></thead><tbody><tr v-for="(row, rowIndex) in rows" :key="rowIndex"><td v-for="column in columns" :key="column.fieldname" :data-label="column.label" :style="column.index === 0 && row.indent ? { paddingLeft: `${14 + Number(row.indent) * 18}px` } : undefined"><RouterLink v-if="cellLink(row, column)" :to="cellLink(row, column)">{{ formatUniversalValue(cell(row, column), column) }}</RouterLink><span v-else>{{ formatUniversalValue(cell(row, column), column) }}</span></td></tr></tbody></table></div></section>
      <section v-if="result?.report_summary?.length" class="rug-summary-grid"><article v-for="item in result.report_summary" :key="item.label"><span>{{ item.label }}</span><strong>{{ item.value }}</strong></article></section>
      <div v-if="!definition.pdf_environment?.available" class="rug-warning">PDF generation is unavailable because wkhtmltopdf is not installed. Print Preview and CSV export remain available.</div>
    </main>
    <div v-else class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
  </PageContainer>
</template>
