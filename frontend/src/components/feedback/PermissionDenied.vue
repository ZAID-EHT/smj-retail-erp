<script setup>
defineProps({ message: { type: String, default: "You do not have permission to view these records." } });
</script>

<template>
  <section class="ref-permission-denied" role="alert">
    <span aria-hidden="true">⌾</span>
    <div><h2>Permission denied</h2><p>{{ message }}</p><small>No record details or counts were loaded.</small></div>
  </section>
</template>
