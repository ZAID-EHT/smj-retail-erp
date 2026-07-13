<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getReportHub } from "@/services/priority.js";
const props = defineProps({ group: { type: String, default: "" } });
const hub = ref(null); const error = ref(null); let controller;
async function load() { controller?.abort(); controller = new AbortController(); error.value = null; try { hub.value = await getReportHub(props.group || undefined, controller.signal); } catch (caught) { if (caught.name !== "AbortError") error.value = caught; } }
watch(() => props.group, load, { immediate: true }); onBeforeUnmount(() => controller?.abort());
</script>
<template><PageContainer><ErrorState v-if="error" title="Unable to load reports" :message="error.message" @retry="load" /><main v-else-if="hub" class="rug-page"><nav class="rug-breadcrumbs"><RouterLink to="/home">Home</RouterLink><span>›</span><RouterLink to="/reports">Reports</RouterLink><span v-if="group">›</span><strong v-if="group">{{ group }}</strong></nav><header class="rug-banner"><div><span class="rug-badge">Report hub</span><h1>{{ group ? `${group[0].toUpperCase()}${group.slice(1)} Reports` : 'Reports' }}</h1><p>Run the installed ERPNext reports your account is permitted to access.</p></div></header><section v-for="section in hub.groups" :key="section.key" class="rug-section-card"><header><div><h2>{{ section.label }}</h2><p>{{ section.reports.length }} permitted reports</p></div></header><div class="priority-link-grid"><RouterLink v-for="report in section.reports" :key="report.name" :to="report.path"><span>▥</span><strong>{{ report.name }}</strong><small>{{ report.report_type }}{{ report.prepared_report ? ' · Prepared' : '' }}</small></RouterLink></div></section><section v-if="!hub.groups.length" class="rug-section-card rug-empty"><h2>No permitted reports</h2><p>Your ERPNext report permissions do not currently grant access to this report group.</p></section></main><div v-else class="rug-skeleton"><i v-for="n in 8" :key="n" /></div></PageContainer></template>
