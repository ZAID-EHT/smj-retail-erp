<script setup>
import { formatDetailValue } from "@/services/detailFormatters.js";

defineProps({ section: { type: Object, required: true }, currency: { type: String, default: "LKR" } });
</script>

<template>
  <section class="ref-detail-section">
    <h2>{{ section.title }}</h2>
    <dl>
      <template v-for="field in section.fields" :key="field.fieldname">
        <div :class="{ 'is-wide': field.type === 'multiline' }">
          <dt>{{ field.label }}</dt>
          <dd :class="[`is-${field.type}`]">{{ formatDetailValue(field.value, field.type, currency) }}</dd>
        </div>
      </template>
    </dl>
  </section>
</template>
