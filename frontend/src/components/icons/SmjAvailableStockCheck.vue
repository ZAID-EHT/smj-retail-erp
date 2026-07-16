<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Available to sell" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4 8 12 4l8 4-8 4-8-4Z" />
    <path d="M4 8v8l8 4 8-4V8" />
    <path d="M9.5 13.2l1.8 1.8 3.2-3.6" stroke="currentColor" />
  </IconBase>
</template>
