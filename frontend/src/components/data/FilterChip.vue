<script setup>
defineProps({ label: { type: String, required: true }, value: { type: String, required: true } });
defineEmits(["remove"]);
</script>

<template>
  <span class="ref-filter-chip">
    <b>{{ label }}:</b> {{ value }}
    <button type="button" :aria-label="`Remove ${label} filter`" @click="$emit('remove')">×</button>
  </span>
</template>
