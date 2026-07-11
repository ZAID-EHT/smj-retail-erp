<script setup>
defineProps({ pagination: { type: Object, required: true } });
defineEmits(["page"]);
</script>

<template>
  <nav class="ref-pagination" aria-label="Record pages">
    <button
      type="button"
      :disabled="!pagination.has_previous"
      @click="$emit('page', pagination.page - 1)"
    >
      ← Previous
    </button>
    <span>Page <b>{{ pagination.page }}</b> of <b>{{ pagination.pages }}</b></span>
    <button
      type="button"
      :disabled="!pagination.has_next"
      @click="$emit('page', pagination.page + 1)"
    >
      Next →
    </button>
  </nav>
</template>
