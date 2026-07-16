<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Barcode scan" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4 4v3M8 4v16M11 4v16M14 4v3M14 17v3M17 4v16M20 4v3M20 17v3M4 17v3" />
  </IconBase>
</template>
