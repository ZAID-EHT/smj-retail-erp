<script setup>
defineProps({ label: { type: String, default: "Loading…" } });
</script>

<template>
  <div class="ref-state-card ref-loading-state" role="status" aria-live="polite">
    <span class="ref-spinner" aria-hidden="true"></span>
    <strong>{{ label }}</strong>
  </div>
</template>
