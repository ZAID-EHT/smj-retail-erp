<script setup>
import { computed, inject } from "vue";
import { SmjClose } from "@/components/icons";
import { moduleIcon } from "@/components/icons/moduleIconMap.js";
import { navigationModules } from "@/router/routes.js";

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
          <strong>Retail ERP</strong>
          <button class="ref-icon-button" type="button" data-dialog-close aria-label="Close navigation" @click="$emit('close')">
            <SmjClose size="18" decorative />
          </button>
        </div>
        <nav aria-label="Mobile modules">
          <section v-for="module in modules" :key="module.name" :data-accent="module.accent">
            <RouterLink class="ref-mobile-navigation__module" :to="module.path" @click="$emit('close')">
              <component :is="moduleIcon(module.icon)" size="16" decorative />{{ module.label }}
            </RouterLink>
            <RouterLink
              v-for="link in module.links"
              :key="`${module.name}-${link.label}`"
              class="ref-mobile-navigation__link"
              :to="link.path"
              @click="$emit('close')"
            >{{ link.label }}</RouterLink>
          </section>
        </nav>
      </aside>
    </div>
  </Teleport>
</template>
