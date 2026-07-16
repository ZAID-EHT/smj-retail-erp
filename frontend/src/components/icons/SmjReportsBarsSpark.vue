<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Reports" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4 20V10M9.5 20V4M15 20v-7M20 20V8" />
    <path d="M4 6.5 9 4l4.5 3L20 4" />
  </IconBase>
</template>
