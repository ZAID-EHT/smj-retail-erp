<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import ColourCard from "@/components/ui/ColourCard.vue";
import PageContainer from "@/components/layout/PageContainer.vue";

const route = useRoute();
const routeLabel = computed(() => `/app/retail-erp${route.path}`);
</script>

<template>
  <PageContainer>
    <section class="ref-page-hero" :data-accent="route.meta.accent">
      <div class="ref-page-hero__copy">
        <span class="ref-page-hero__eyebrow">RETAIL ERP MODULE</span>
        <h1>{{ route.meta.title }}</h1>
        <p>{{ route.meta.description }}</p>
      </div>
      <div class="ref-page-hero__mark" aria-hidden="true">E</div>
    </section>

    <div class="ref-placeholder-grid">
      <ColourCard :accent="route.meta.accent" title="Frontend route">
        <code>{{ routeLabel }}</code>
      </ColourCard>
      <ColourCard accent="green" title="Foundation ready">
        <p>The shared Vue application shell is active on this route.</p>
      </ColourCard>
      <ColourCard accent="orange" title="Coming in a later stage">
        <p>This module’s ERPNext data and actions will be implemented in its approved workflow stage.</p>
      </ColourCard>
    </div>
  </PageContainer>
</template>
