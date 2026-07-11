<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import ColourCard from "@/components/ui/ColourCard.vue";
import PageContainer from "@/components/layout/PageContainer.vue";

const route = useRoute();
const recordName = computed(() => decodeURIComponent(String(route.params.name || "")));
</script>

<template>
  <PageContainer>
    <section class="ref-detail-placeholder">
      <span class="ref-entity-page__eyebrow">CUSTOM DETAIL ROUTE</span>
      <h1>{{ route.meta.title }}</h1>
      <code>{{ recordName }}</code>
      <ColourCard accent="orange" title="Detail page under development">
        <p>This record stayed inside the Retail ERP shell. Read-only detail fields and actions will be added in the next approved detail-page stage.</p>
      </ColourCard>
      <RouterLink class="ref-button ref-button--secondary" :to="route.meta.backRoute">← Back to list</RouterLink>
    </section>
  </PageContainer>
</template>
