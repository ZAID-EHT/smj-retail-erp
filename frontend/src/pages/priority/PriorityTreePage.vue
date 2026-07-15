<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PriorityTreeNode from "@/components/priority/PriorityTreeNode.vue";
import { getTreeNodes } from "@/services/priority.js";

const props = defineProps({ definition: { type: Object, required: true } });
const route = useRoute(); const router = useRouter();
const roots = ref([]); const expanded = ref({}); const loading = ref(false); const error = ref(null); const company = ref("");
let controller;
async function children(parent = "") { return getTreeNodes(route.path, parent || undefined, company.value || undefined, controller?.signal); }
async function load() { controller?.abort(); controller = new AbortController(); loading.value = true; error.value = null; expanded.value = {}; company.value = String(route.query.company || ""); try { const result = await children(); roots.value = result.nodes; company.value = result.company || ""; } catch (caught) { if (caught.name !== "AbortError") error.value = caught; } finally { loading.value = false; } }
async function toggle(node) { if (!node.expandable) return; if (expanded.value[node.name]) { const copy = { ...expanded.value }; delete copy[node.name]; expanded.value = copy; return; } try { const result = await children(node.name); expanded.value = { ...expanded.value, [node.name]: result.nodes }; } catch (caught) { error.value = caught; } }
function open(node) { if (props.definition.base_path) router.push(`${props.definition.base_path}/${encodeURIComponent(node.name)}`); }
watch(() => route.path, load, { immediate: true }); onBeforeUnmount(() => controller?.abort());
</script>
<template><PageContainer><ErrorState v-if="error && !roots.length" title="Unable to load tree" :message="error.message" @retry="load" /><main v-else class="rug-page"><nav class="rug-breadcrumbs"><RouterLink to="/home">Home</RouterLink><span>›</span><strong>{{ definition.doctype }}</strong></nav><header class="rug-banner rug-banner--green"><div><span class="rug-badge">Tree view</span><h1>{{ definition.doctype }}</h1><p>Browse the permitted hierarchy{{ company ? ` for ${company}` : '' }}.</p></div><div class="rug-banner-actions"><RouterLink v-if="definition.permissions?.can_create && definition.base_path" class="rug-primary priority-button-link" :to="`${definition.base_path}/new`">New {{ definition.doctype }}</RouterLink><button type="button" @click="load">Refresh</button></div></header><section class="rug-section-card priority-tree"><div v-if="loading" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div><div v-else-if="!roots.length" class="rug-empty"><h2>No permitted nodes</h2></div><ul v-else><PriorityTreeNode v-for="node in roots" :key="node.name" :node="node" :children="expanded[node.name]" :expanded-map="expanded" @toggle="toggle" @open="open" /></ul></section></main></PageContainer></template>
