<script setup>
import { computed, inject } from "vue";
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
          <button class="ref-icon-button" type="button" data-dialog-close aria-label="Close navigation" @click="$emit('close')">×</button>
        </div>
        <nav aria-label="Mobile modules">
          <RouterLink
            v-for="module in modules"
            :key="module.name"
            :to="module.path"
            :data-accent="module.accent"
            @click="$emit('close')"
          >
            <span aria-hidden="true">◆</span>
            {{ module.label }}
          </RouterLink>
          <RouterLink v-if="modules.some((module) => module.name === 'sales')" to="/smart-sales" data-accent="orange" @click="$emit('close')">
            <span aria-hidden="true">◆</span>
            Smart Sales
          </RouterLink>
        </nav>
      </aside>
    </div>
  </Teleport>
</template>
