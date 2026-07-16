<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Home" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M3.5 11.5 12 4l8.5 7.5" />
    <path d="M5.5 10v9.5h13V10" />
    <path d="M9.5 19.5v-6h5v6" />
  </IconBase>
</template>
