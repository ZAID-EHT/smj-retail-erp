<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Delivery" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M3 7h10v9H3z" />
    <path d="M13 10.5h3.6L19.5 13v3H13z" />
    <circle cx="7" cy="18" r="1.6" />
    <circle cx="16.5" cy="18" r="1.6" />
    <path d="M4.5 4v2" />
  </IconBase>
</template>
