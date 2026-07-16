<script setup>
import IconBase from "./IconBase.vue";
defineProps({
  size: { type: [Number, String], default: 24 },
  title: { type: String, default: "Comments" },
  decorative: { type: Boolean, default: false },
});
</script>

<template>
  <IconBase :size="size" :title="title" :decorative="decorative">
    <path d="M4 5.5h16V16H9l-4 3.5V16H4Z" />
    <path d="M8 9h8M8 12.2h5" />
  </IconBase>
</template>
