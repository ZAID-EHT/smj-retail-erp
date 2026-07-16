<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Warehouse transfer" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M2.5 9 6.5 6l4 3" />
    <path d="M3 8.7v6.8h7V8.7" />
    <path d="M13.5 9 17.5 6l4 3" />
    <path d="M14 8.7v6.8h7V8.7" />
    <path d="M10.5 12h3" />
  </IconBase>
</template>
