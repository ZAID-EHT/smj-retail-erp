<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Reserved stock" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="m4 7.5 8-3.5 8 3.5-8 3.5-8-3.5Z" />
    <path d="M4 7.5V16l8 3.5m0-8v8m8-11.5V16l-8 3.5" />
    <rect x="9.3" y="17.6" width="5.4" height="4.3" rx="1" />
    <path d="M10.4 17.6v-1.3a1.6 1.6 0 0 1 3.2 0v1.3" />
  </IconBase>
</template>
