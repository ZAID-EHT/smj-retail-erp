<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Columns" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <rect x="3.5" y="4.5" width="17" height="15" rx="1.6" />
    <path d="M10 4.5V19.5M15 4.5V19.5" />
  </IconBase>
</template>
