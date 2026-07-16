<script setup>
import { SmjCancel, SmjClose, SmjHelp, SmjSubmit } from "@/components/icons";
import { useToast } from "@/composables/toast.js";

const { toasts, dismiss } = useToast();

const ICONS = { success: SmjSubmit, error: SmjCancel, warning: SmjHelp, info: SmjHelp };
</script>

<template>
  <div class="ref-toast-host" aria-live="polite" aria-atomic="false">
    <div v-for="toast in toasts" :key="toast.id" class="ref-toast" :class="`ref-toast--${toast.type}`" role="status">
      <component :is="ICONS[toast.type] || SmjHelp" size="18" decorative />
      <div class="ref-toast__body">
        <strong v-if="toast.title">{{ toast.title }}</strong>
        <p v-if="toast.message">{{ toast.message }}</p>
        <button v-if="toast.actionLabel" type="button" class="ref-toast__action" @click="toast.onAction?.(); dismiss(toast.id)">
          {{ toast.actionLabel }}
        </button>
      </div>
      <button type="button" class="ref-toast__close" aria-label="Dismiss notification" @click="dismiss(toast.id)">
        <SmjClose size="14" decorative />
      </button>
    </div>
  </div>
</template>
