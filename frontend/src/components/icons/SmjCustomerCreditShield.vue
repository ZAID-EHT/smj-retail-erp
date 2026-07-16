<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Customer credit" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <circle cx="12" cy="8" r="3" />
    <path d="M6 20c.7-3.4 3-5 6-5s5.3 1.6 6 5" />
  </IconBase>
</template>
