<script setup>
import { computed, inject } from "vue";
import { SmjClose } from "@/components/icons";
import { moduleIcon } from "@/components/icons/moduleIconMap.js";
import { navigationModules } from "@/router/routes.js";

const SMJ_LOGO = "/assets/my_store_ui/images/smj-logo.png";

defineProps({ open: { type: Boolean, default: false } });
defineEmits(["close"]);
const session = inject("retailSession", null);
const modules = computed(() => session ? session.state.navigation : navigationModules);
</script>

<template>
  <Teleport to="body">
    <div v-if="open" v-focus-trap class="ref-mobile-navigation" role="dialog" aria-modal="true" aria-label="Mobile navigation">
      <button class="ref-mobile-navigation__backdrop" tabindex="-1" aria-label="Close navigation" @click="$emit('close')"></button>
      <aside class="ref-mobile-navigation__drawer">
        <div class="ref-mobile-navigation__header">
          <span class="ref-mobile-navigation__brand">
            <img class="ref-mobile-navigation__brand-logo" :src="SMJ_LOGO" alt="" aria-hidden="true" />
            <span><strong>SMJ ERP</strong><small>Menu</small></span>
          </span>
          <button class="ref-icon-button" type="button" data-dialog-close aria-label="Close navigation" @click="$emit('close')">
            <SmjClose size="18" decorative />
          </button>
        </div>
        <nav aria-label="Mobile modules">
          <section v-for="module in modules" :key="module.name" :data-accent="module.accent">
            <RouterLink class="ref-mobile-navigation__module" :to="module.path" @click="$emit('close')">
              <span class="ref-mobile-navigation__module-icon" aria-hidden="true">
                <component :is="moduleIcon(module.icon)" size="17" decorative />
              </span>
              <span class="ref-mobile-navigation__module-copy">
                <strong>{{ module.label }}</strong>
                <small>{{ module.links?.length || 0 }} permitted pages</small>
              </span>
              <span class="ref-mobile-navigation__module-arrow" aria-hidden="true">→</span>
            </RouterLink>
            <div v-if="module.links?.length" class="ref-mobile-navigation__links">
              <RouterLink
                v-for="link in module.links"
                :key="`${module.name}-${link.label}`"
                class="ref-mobile-navigation__link"
                :to="link.path"
                @click="$emit('close')"
              ><span aria-hidden="true"></span>{{ link.label }}</RouterLink>
            </div>
          </section>
        </nav>
      </aside>
    </div>
  </Teleport>
</template>
