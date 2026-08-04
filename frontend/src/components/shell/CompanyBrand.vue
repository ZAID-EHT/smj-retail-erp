<script setup>
import { computed, inject } from "vue";

const SMJ_LOGO = "/assets/my_store_ui/images/smj-logo.png";

const session = inject("retailSession", null);
const branding = inject("retailBranding", {});

// The SMJ mark is the fallback, not a stock icon. `product-placeholder` is the
// generic image the server used to hand over when no company logo was set; treat
// it as "no logo" so the brand mark wins.
const logoSrc = computed(() => {
  const supplied = branding.logo ? String(branding.logo) : "";
  if (!supplied || supplied.includes("product-placeholder")) return SMJ_LOGO;
  return supplied;
});

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
    <img class="ref-brand__logo" :src="logoSrc" alt="" />
    <span class="ref-brand__copy">
      <strong>SMJ Retail ERP</strong>
      <small>ERPNext v15<template v-if="companyName && companyName !== 'Retail ERP'"> · {{ companyName }}</template></small>
    </span>
  </RouterLink>
</template>
