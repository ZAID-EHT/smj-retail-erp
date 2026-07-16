<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Finance" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <rect x="3.5" y="6.5" width="17" height="12" rx="2.4" />
    <path d="M3.5 10.5h17" />
    <circle cx="16.5" cy="14.5" r="1.1" fill="currentColor" stroke="none" />
  </IconBase>
</template>
