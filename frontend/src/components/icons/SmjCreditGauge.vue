<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Credit" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4 15.5a8 8 0 1 1 16 0" />
    <path d="M12 15.5 16 10" />
    <path d="M4 15.5h16" />
  </IconBase>
</template>
