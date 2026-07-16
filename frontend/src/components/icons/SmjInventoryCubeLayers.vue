<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Inventory" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="m4 7 8-4 8 4-8 4-8-4Z" />
    <path d="m4 12 8 4 8-4" />
    <path d="m4 17 8 4 8-4" />
  </IconBase>
</template>
