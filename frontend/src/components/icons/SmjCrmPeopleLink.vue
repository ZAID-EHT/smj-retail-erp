<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "CRM" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <circle cx="8" cy="8" r="2.6" />
    <circle cx="17" cy="15.5" r="2.6" />
    <path d="M4.5 19c.6-2.4 2-3.6 3.5-3.6s2.2.7 2.7 1.6M13.5 12.4c.9-1.5 2-2 3.5-2s2.7 1.1 3.4 2.6" />
    <path d="M10.5 9.5 14.5 12" />
  </IconBase>
</template>
