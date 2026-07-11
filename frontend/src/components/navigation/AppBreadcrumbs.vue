<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const currentTitle = computed(() => route.meta.title || "Home");
</script>

<template>
  <nav class="ref-breadcrumbs" aria-label="Breadcrumb">
    <RouterLink to="/home">Retail ERP</RouterLink>
    <span aria-hidden="true">›</span>
    <span aria-current="page">{{ currentTitle }}</span>
  </nav>
</template>
