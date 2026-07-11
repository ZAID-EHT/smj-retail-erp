<script setup>
defineProps({
  title: { type: String, required: true },
  accent: { type: String, default: "blue" },
});
</script>

<template>
  <article class="ref-colour-card" :data-accent="accent">
    <span class="ref-colour-card__accent" aria-hidden="true"></span>
    <h2>{{ title }}</h2>
    <div class="ref-colour-card__body"><slot /></div>
  </article>
</template>
