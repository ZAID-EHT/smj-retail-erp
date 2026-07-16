<script setup>
import { useConfirmDialog } from "@/composables/confirm.js";

const state = useConfirmDialog();
</script>

<template>
  <div class="ref-confirm-dialog-host" aria-live="assertive">
    <div v-if="state.dialog" class="ref-confirm-backdrop" @click="state.dialog.resolve(false)">
      <div
        v-focus-trap
        class="ref-confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        :aria-label="state.dialog.title"
        @click.stop
      >
        <h2>{{ state.dialog.title }}</h2>
        <p v-if="state.dialog.message">{{ state.dialog.message }}</p>
        <div class="ref-confirm-dialog__actions">
          <button type="button" class="ref-button ref-button--secondary" @click="state.dialog.resolve(false)">
            {{ state.dialog.cancelLabel }}
          </button>
          <button
            type="button"
            data-dialog-close
            class="ref-button"
            :class="state.dialog.danger ? 'ref-button--danger' : 'ref-button--primary'"
            @click="state.dialog.resolve(true)"
          >
            {{ state.dialog.confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
