<script setup>
import { computed } from "vue";

const companyName = computed(() => {
  const frappe = window.frappe;
  return (
    frappe?.defaults?.get_user_default?.("Company") ||
    frappe?.boot?.sysdefaults?.company ||
    "Retail ERP"
  );
});
</script>

<template>
  <RouterLink class="ref-brand" to="/home" aria-label="Retail ERP home">
    <span class="ref-brand__logo" aria-hidden="true">E</span>
    <span class="ref-brand__copy">
      <strong>{{ companyName }}</strong>
      <small>ERPNext v15</small>
    </span>
  </RouterLink>
</template>
