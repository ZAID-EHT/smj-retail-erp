<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Operations" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <circle cx="12" cy="12" r="3" />
    <path d="M12 3.5v2.4M12 18.1v2.4M20.5 12h-2.4M5.9 12H3.5M17.9 6.1l-1.7 1.7M7.8 16.1l-1.7 1.7M17.9 17.9l-1.7-1.7M7.8 7.8 6.1 6.1" />
  </IconBase>
</template>
