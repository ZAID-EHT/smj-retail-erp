<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Approval" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M6 3.5h9l3.5 3.5V20H6Z" />
    <path d="m8.5 15 2 2 5-5.5" />
  </IconBase>
</template>
