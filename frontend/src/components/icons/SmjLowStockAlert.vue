<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Low stock" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4 8 12 4l8 4-8 4-8-4Z" />
    <path d="M4 8v8l8 4 8-4V8" />
    <path d="M12 10.5v3" />
    <circle cx="12" cy="15.3" r="0.15" fill="currentColor" />
  </IconBase>
</template>
