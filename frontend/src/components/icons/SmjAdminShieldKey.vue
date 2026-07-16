<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Administration" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M12 3.5 19 6.3v5.4c0 4.6-2.9 7.7-7 8.8-4.1-1.1-7-4.2-7-8.8V6.3L12 3.5Z" />
    <circle cx="11" cy="12.3" r="1.7" />
    <path d="M12.5 13.6 15.5 16.6M14 15.1l1.3-1.3" />
  </IconBase>
</template>
