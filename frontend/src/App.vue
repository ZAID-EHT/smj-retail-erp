<script setup>
import { onErrorCaptured, ref } from "vue";

import AppShell from "@/components/shell/AppShell.vue";

defineProps({
  context: { type: Object, default: () => ({}) },
});

const fatalError = ref(null);

onErrorCaptured((error) => {
  fatalError.value = error;
  console.error("Retail ERP application error", error);
  return false;
});
</script>

<template>
  <AppShell :fatal-error="fatalError" />
</template>
