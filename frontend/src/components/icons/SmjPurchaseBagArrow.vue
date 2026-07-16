<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Purchases" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M6 8h12l-1 12H7L6 8Z" />
    <path d="M9 8V6.5a3 3 0 0 1 6 0V8" />
    <path d="M12 11v5m0 0-2-2m2 2 2-2" />
  </IconBase>
</template>
