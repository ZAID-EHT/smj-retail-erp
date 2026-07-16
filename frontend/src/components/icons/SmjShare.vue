<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Share" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <circle cx="18" cy="6" r="2.3" />
    <circle cx="6" cy="12" r="2.3" />
    <circle cx="18" cy="18" r="2.3" />
    <path d="m8.1 10.8 7.8-3.6M8.1 13.2l7.8 3.6" />
  </IconBase>
</template>
