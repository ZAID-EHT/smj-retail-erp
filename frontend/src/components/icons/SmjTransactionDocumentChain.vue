<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Transaction" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <rect x="3" y="4.5" width="7.5" height="9.5" rx="1.3" />
    <rect x="13.5" y="10" width="7.5" height="9.5" rx="1.3" />
    <path d="M10.5 9h3M9 14.5v1.8a1.7 1.7 0 0 0 1.7 1.7H13" />
  </IconBase>
</template>
