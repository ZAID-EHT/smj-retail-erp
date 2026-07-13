<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getSpecialPage } from "@/services/priority.js";
defineProps({ definition: { type: Object, required: true } });
const route = useRoute(); const router = useRouter(); const page = ref(null); const error = ref(null); let controller;
async function load() { controller?.abort(); controller = new AbortController(); error.value = null; try { const result = await getSpecialPage(route.path, controller.signal); if (result.redirect) await router.replace(result.redirect); else page.value = result; } catch (caught) { if (caught.name !== "AbortError") error.value = caught; } }
watch(() => route.path, load, { immediate: true }); onBeforeUnmount(() => controller?.abort());
</script>
<template>
  <PageContainer>
    <PermissionDenied v-if="error?.permissionDenied" />
    <ErrorState v-else-if="error" title="Unable to load specialised page" :message="error.message" @retry="load" />
    <main v-else-if="page" class="rug-page">
      <nav class="rug-breadcrumbs"><RouterLink to="/home">Home</RouterLink><span>›</span><strong>{{ page.label }}</strong></nav>
      <header class="rug-banner rug-banner--purple"><div><span class="rug-badge">Specialised interface</span><h1>{{ page.label }}</h1><p>{{ page.limitations }}</p></div><div class="rug-banner-actions"><a v-if="page.launch_url" class="rug-primary priority-button-link" :href="page.launch_url">Launch {{ page.label }}</a></div></header>
      <section v-if="page.profiles?.length" class="rug-section-card"><header><div><h2>Available POS profile</h2><p>The launch action is shown only after server-side profile and permission checks.</p></div></header><div class="rug-summary-grid"><article v-for="profile in page.profiles" :key="profile.name"><span>{{ profile.company }}</span><strong>{{ profile.name }}</strong><small>{{ profile.warehouse }} · {{ profile.currency }}</small></article></div></section>
      <section v-if="page.facts?.length" class="rug-summary-grid"><article v-for="fact in page.facts" :key="fact.label"><span>{{ fact.label }}</span><strong>{{ fact.value }}</strong></article></section>
      <section v-if="page.permission_matrix?.length" class="rug-list-card"><div class="rug-count"><span><strong>{{ page.permission_matrix.length }}</strong> installed permission rules</span><span>Read-only metadata view</span></div><div class="rug-table-region"><table><thead><tr><th>DocType</th><th>Role</th><th v-for="permission in ['read','create','write','delete','submit','cancel','print','email','import','export']" :key="permission">{{ permission }}</th></tr></thead><tbody><tr v-for="(row, index) in page.permission_matrix" :key="`${row.doctype}-${row.role}-${index}`"><td>{{ row.doctype }}</td><td>{{ row.role }}</td><td v-for="permission in ['read','create','write','delete','submit','cancel','print','email','import','export']" :key="permission"><span :class="['rug-status', row[permission] ? 'is-positive' : 'is-muted']">{{ row[permission] ? 'Yes' : '—' }}</span></td></tr></tbody></table></div></section>
      <section class="rug-section-card"><header><div><h2>Permitted recent records</h2><p>Readable context from the installed feature. No generic ERPNext Workspace is opened.</p></div></header><div v-if="!page.records?.length" class="rug-muted">No permitted recent records are available.</div><component :is="record.route ? 'RouterLink' : 'div'" v-for="record in page.records" :key="`${record.doctype}-${record.name}`" :to="record.route" class="rug-related"><span>{{ record.doctype }}<small>{{ record.modified }}</small></span><strong>{{ record.name }}</strong></component></section>
      <section class="rug-warning"><strong>Controlled specialised coverage</strong><span>This page exposes the maximum safe read or launch capability implemented in this sprint. Transaction interactions not listed here remain classified for a dedicated adapter.</span></section>
    </main>
    <div v-else class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
  </PageContainer>
</template>
