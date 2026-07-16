<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Landed cost" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <ellipse cx="9" cy="8" rx="5" ry="2.6" />
    <path d="M4 8v4c0 1.4 2.2 2.6 5 2.6s5-1.2 5-2.6V8" />
    <ellipse cx="15.5" cy="15" rx="4.5" ry="2.3" />
    <path d="M11 15v2.4c0 1.3 2 2.3 4.5 2.3s4.5-1 4.5-2.3V15" />
  </IconBase>
</template>
