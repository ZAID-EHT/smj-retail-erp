<script setup>
defineProps({
  active: { type: Boolean, default: false },
  order: { type: String, default: "asc" },
  label: { type: String, required: true },
});
defineEmits(["sort"]);
</script>

<template>
  <button class="ref-sort-button" type="button" @click="$emit('sort')">
    <span>{{ label }}</span>
    <span v-if="active" aria-hidden="true">{{ order === "asc" ? "↑" : "↓" }}</span>
  </button>
</template>
