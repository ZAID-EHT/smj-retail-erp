<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Refresh" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4.5 12a7.5 7.5 0 0 1 12.8-5.3L20 9" />
    <path d="M20 4v5h-5" />
    <path d="M19.5 12a7.5 7.5 0 0 1-12.8 5.3L4 15" />
    <path d="M4 20v-5h5" />
  </IconBase>
</template>
