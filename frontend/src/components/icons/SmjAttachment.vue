<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Attachments" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M16.5 7 8.8 14.7a2.6 2.6 0 0 0 3.7 3.7l7.4-7.4a4.4 4.4 0 0 0-6.2-6.2L6.3 12.2a6.2 6.2 0 0 0 8.8 8.8" />
  </IconBase>
</template>
