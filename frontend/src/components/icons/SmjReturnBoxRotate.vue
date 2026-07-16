<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Return" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4 8 12 4l8 4-8 4-8-4Z" />
    <path d="M4 8v8l8 4 8-4V8" />
    <path d="M9.5 10.2a2.6 2.6 0 1 1-.5 2.7" />
    <path d="M8.7 8.8l.8 1.6-1.7.4" />
  </IconBase>
</template>
