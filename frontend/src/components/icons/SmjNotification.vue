<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Notifications" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M6 10.5a6 6 0 1 1 12 0c0 4 1.3 5.3 1.3 5.3H4.7S6 14.5 6 10.5Z" />
    <path d="M10 19a2 2 0 0 0 4 0" />
  </IconBase>
</template>
