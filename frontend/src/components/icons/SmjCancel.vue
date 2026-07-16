<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Cancel" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <circle cx="12" cy="12" r="8.5" />
    <path d="m9 9 6 6m0-6-6 6" />
  </IconBase>
</template>
