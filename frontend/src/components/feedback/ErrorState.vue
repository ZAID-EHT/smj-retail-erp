<script setup>
defineProps({
  title: { type: String, default: "Something went wrong" },
  message: { type: String, default: "Please reload the page or open the standard Desk fallback." },
});
</script>

<template>
  <section class="ref-state-card ref-error-state" role="alert">
    <span class="ref-state-card__icon" aria-hidden="true">!</span>
    <div><h1>{{ title }}</h1><p>{{ message }}</p></div>
    <a class="ref-button ref-button--secondary" href="/app">Open Standard Desk</a>
  </section>
</template>
