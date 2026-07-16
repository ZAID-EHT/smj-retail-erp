<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Calendar" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <rect x="3.5" y="5" width="17" height="15.5" rx="1.8" />
    <path d="M3.5 9.5h17M8 3v3.6M16 3v3.6" />
  </IconBase>
</template>
