<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Assignment" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <circle cx="12" cy="8.3" r="3.3" />
    <path d="M5.5 20c.8-3.6 3.2-5.4 6.5-5.4.7 0 1.3.1 1.9.2" />
    <path d="m15.5 17.7 1.6 1.6 3-3.3" />
  </IconBase>
</template>
