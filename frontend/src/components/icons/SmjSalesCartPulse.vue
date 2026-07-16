<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Smart Sales" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M3 4h2.2l1 3.2M6.2 7.2 8 15h9.5l2-7.8H6.2" />
    <circle cx="9.5" cy="19" r="1.4" />
    <circle cx="16.5" cy="19" r="1.4" />
    <path d="M8.5 11.2h2l1.5 2.4 2-4.6 1.4 2.2h2.4" />
  </IconBase>
</template>
