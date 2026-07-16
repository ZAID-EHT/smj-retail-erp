<script setup>
import { usePageActions } from "@/composables/pageActions.js";

const pageActions = usePageActions();
</script>

<template>
  <div v-if="pageActions.actions.length" class="ref-header-actions-left" aria-label="Page actions">
    <button
      v-for="action in pageActions.actions"
      :key="action.key"
      type="button"
      class="ref-header-action"
      :class="{ 'ref-header-action--primary': action.variant === 'primary' }"
      :disabled="action.disabled"
      @click="action.onClick"
    >
      <component :is="action.icon" v-if="action.icon" size="16" decorative />
      {{ action.label }}
    </button>
  </div>
</template>
