<script setup>
import { formatDetailValue } from "@/services/detailFormatters.js";

defineProps({ field: { type: Object, required: true }, currency: { type: String, default: "LKR" } });
</script>

<template>
  <article class="ref-detail-summary-card">
    <span>{{ field.label }}</span>
    <strong>{{ formatDetailValue(field.value, field.type, currency) }}</strong>
  </article>
</template>
