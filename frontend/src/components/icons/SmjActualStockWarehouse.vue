<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Actual stock" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M3.5 10 12 4l8.5 6" />
    <path d="M4.5 9.5v10h15v-10" />
    <path d="M9 19.5v-5h6v5" />
    <path d="M9 12.5h6" />
  </IconBase>
</template>
