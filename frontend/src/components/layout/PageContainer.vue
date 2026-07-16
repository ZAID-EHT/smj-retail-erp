<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const accent = computed(() => route.meta?.accent || "blue");
const moduleName = computed(() => {
  const segment = String(route.path || "/home").split("/").filter(Boolean)[0] || "home";
  return segment.replace(/[^a-z0-9-]/gi, "-").toLowerCase();
});
</script>

<template>
  <div
    class="ref-page-container"
    :data-accent="accent"
    :data-module="moduleName"
  >
    <slot />
  </div>
</template>
