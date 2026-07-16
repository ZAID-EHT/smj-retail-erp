<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Payment" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <rect x="3.5" y="6.5" width="17" height="12" rx="2.4" />
    <path d="M3.5 10.5h17" />
    <path d="m13.5 14.3 1.6 1.6 2.8-3.1" />
  </IconBase>
</template>
