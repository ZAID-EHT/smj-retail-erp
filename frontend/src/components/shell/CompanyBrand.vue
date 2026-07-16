<script setup>
import { computed, inject } from "vue";
import { SmjHomeBuilding } from "@/components/icons";

const session = inject("retailSession", null);
const branding = inject("retailBranding", {});

const companyName = computed(() => {
  const frappe = window.frappe;
  return (
    frappe?.defaults?.get_user_default?.("Company") ||
    frappe?.boot?.sysdefaults?.company || session?.state?.company || branding.brand ||
    "Retail ERP"
  );
});
</script>

<template>
  <RouterLink class="ref-brand" to="/home" aria-label="Retail ERP home">
    <img v-if="branding.logo" class="ref-brand__logo" :src="branding.logo" alt="" />
    <span v-else class="ref-brand__logo" aria-hidden="true"><SmjHomeBuilding size="22" decorative /></span>
    <span class="ref-brand__copy">
      <strong>{{ companyName }}</strong>
      <small>SMJ Retail ERP · ERPNext v15</small>
    </span>
  </RouterLink>
</template>
