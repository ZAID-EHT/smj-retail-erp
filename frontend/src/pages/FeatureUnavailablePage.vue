<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
const route = useRoute();
const feature = computed(() => String(route.query.feature || "This feature").slice(0, 80));
</script>
<template><PageContainer><section class="ref-state-card"><span class="ref-state-card__icon" aria-hidden="true">…</span><div><h1>{{ feature }} is under development</h1><p>This feature is not yet available in the Retail ERP interface.</p></div><RouterLink class="ref-button ref-button--primary" to="/home">Return home</RouterLink></section></PageContainer></template>
