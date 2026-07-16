<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Import" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4 8h16l-1.6 9.5H5.6L4 8Z" />
    <path d="M8 8V6a4 4 0 0 1 8 0v2" />
    <path d="M9 12v3M12 12v3M15 12v3" />
  </IconBase>
</template>
