<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Invoice" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M6 3.5h9l3.5 3.5V20H6Z" />
    <path d="M9 11h6M9 14.5h6" />
    <circle cx="9.5" cy="8" r="1.6" />
  </IconBase>
</template>
