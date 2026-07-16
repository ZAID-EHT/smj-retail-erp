<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Print" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M6 9V4h12v5" />
    <rect x="4.5" y="9" width="15" height="7" rx="1.4" />
    <rect x="7" y="14" width="10" height="6.5" rx="0.6" />
  </IconBase>
</template>
