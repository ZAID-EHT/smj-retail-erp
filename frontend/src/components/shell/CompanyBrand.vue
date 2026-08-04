<script setup>
import { computed, inject } from "vue";

const SMJ_LOGO = "/assets/my_store_ui/images/smj-logo.png";

const branding = inject("retailBranding", {});

// The SMJ mark is the fallback, not a stock icon. `product-placeholder` is the
// generic image the server used to hand over when no company logo was set; treat
// it as "no logo" so the brand mark wins.
const logoSrc = computed(() => {
  const supplied = branding.logo ? String(branding.logo) : "";
  if (!supplied || supplied.includes("product-placeholder")) return SMJ_LOGO;
  return supplied;
});
</script>

<template>
  <!-- Mark only. The wordmark and version line that used to sit beside it are
       already in the logo artwork, and the label carries the accessible name. -->
  <RouterLink class="ref-brand ref-brand--mark-only" to="/home" aria-label="SMJ Retail ERP home">
    <img class="ref-brand__logo" :src="logoSrc" alt="SMJ Retail ERP" />
  </RouterLink>
</template>
