<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Help" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <circle cx="12" cy="12" r="8.5" />
    <path d="M9.6 9.5a2.4 2.4 0 1 1 3.6 2.1c-.9.6-1.2 1-1.2 1.9" />
    <circle cx="12" cy="16.7" r="0.15" fill="currentColor" />
  </IconBase>
</template>
