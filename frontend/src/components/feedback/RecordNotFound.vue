<script setup>
defineProps({ name: { type: String, default: "" }, backRoute: { type: String, required: true } });
</script>

<template>
  <section class="ref-record-not-found" role="alert">
    <span aria-hidden="true">?</span>
    <div><h2>Record not found</h2><p><code>{{ name }}</code> does not exist or is not available to your account.</p></div>
    <RouterLink class="ref-button ref-button--secondary" :to="backRoute">Back to list</RouterLink>
  </section>
</template>
