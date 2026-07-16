<script setup>
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <svg
    class="smj-icon"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    :aria-hidden="decorative ? 'true' : undefined"
    :role="decorative ? undefined : 'img'"
  >
    <title v-if="!decorative && title">{{ title }}</title>
    <slot />
  </svg>
</template>

<style scoped>
.smj-icon { display: inline-block; flex: 0 0 auto; vertical-align: middle; }
</style>
