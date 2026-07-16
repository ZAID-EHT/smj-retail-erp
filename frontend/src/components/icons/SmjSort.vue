<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Sort" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M7 5v14m0 0-3-3m3 3 3-3" />
    <path d="M17 19V5m0 0-3 3m3-3 3 3" />
  </IconBase>
</template>
