<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Profile" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <circle cx="12" cy="8.3" r="3.3" />
    <path d="M5.5 20c.8-3.6 3.2-5.4 6.5-5.4s5.7 1.8 6.5 5.4" />
  </IconBase>
</template>
