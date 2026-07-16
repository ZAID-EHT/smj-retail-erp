<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  loading: { type: Boolean, default: false },
  error: { type: String, default: "" },
  empty: { type: Boolean, default: false },
  emptyText: { type: String, default: "No data for this period yet." },
  reportLink: { type: String, default: "" },
  lastRefreshed: { type: String, default: "" },
});
defineEmits(["refresh"]);
</script>

<template>
  <section class="smj-chart-card">
    <header class="smj-chart-card__header">
      <div>
        <h2>{{ title }}<small v-if="subtitle"> ({{ subtitle }})</small></h2>
        <span v-if="lastRefreshed" class="smj-chart-card__refreshed">Updated {{ lastRefreshed }}</span>
      </div>
      <div class="smj-chart-card__actions">
        <slot name="filter" />
        <RouterLink v-if="reportLink" :to="reportLink" class="smj-chart-card__link">View Report</RouterLink>
        <button type="button" class="smj-chart-card__refresh" aria-label="Refresh chart" @click="$emit('refresh')">
          <slot name="refresh-icon">↻</slot>
        </button>
      </div>
    </header>
    <div v-if="loading" class="smj-chart-card__skeleton" role="status" aria-label="Loading chart">
      <i /><i /><i />
    </div>
    <p v-else-if="error" class="smj-chart-card__error">{{ error }}</p>
    <p v-else-if="empty" class="smj-chart-card__empty">{{ emptyText }}</p>
    <div v-else class="smj-chart-card__body"><slot /></div>
  </section>
</template>

<style scoped>
.smj-chart-card { display: grid; gap: 14px; min-width: 0; max-width: 100%; padding: 18px 20px; border: 1px solid var(--ref-border-colour); border-radius: var(--ref-card-radius); background: var(--ref-card-background); box-shadow: var(--ref-card-shadow); }
.smj-chart-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; min-width: 0; }
.smj-chart-card__header h2 { margin: 0 !important; overflow: hidden; min-width: 0; color: var(--ref-primary-text) !important; font: var(--ref-text-section-title) !important; font-weight: 750 !important; text-overflow: ellipsis; white-space: nowrap; }
.smj-chart-card__header h2 small { color: var(--ref-secondary-text); font-size: 12px; font-weight: 500; }
.smj-chart-card__refreshed { color: var(--ref-muted-text); font-size: 10px; }
.smj-chart-card__actions { display: flex; align-items: center; gap: 8px; flex: 0 1 auto; min-width: 0; flex-wrap: wrap; justify-content: flex-end; }
.smj-chart-card__body { min-width: 0; }
.smj-chart-card__link { color: var(--ref-primary-blue); font-size: 12px; font-weight: 700; text-decoration: none; }
.smj-chart-card__refresh { display: grid; place-items: center; width: 26px; height: 26px; border: 1px solid var(--ref-border-colour); border-radius: 7px; background: #fff; color: var(--ref-secondary-text); cursor: pointer; }
.smj-chart-card__refresh:hover { color: var(--ref-primary-blue); border-color: var(--ref-primary-blue); }
.smj-chart-card__skeleton { display: grid; gap: 8px; min-height: 120px; }
.smj-chart-card__skeleton i { display: block; height: 100%; min-height: 24px; border-radius: 8px; background: linear-gradient(90deg, #f4f6f9 25%, #e9eef5 50%, #f4f6f9 75%); background-size: 220% 100%; animation: ref-shimmer 1.25s linear infinite; }
.smj-chart-card__error { margin: 0; padding: 20px 0; color: var(--ref-danger); font-size: 12px; text-align: center; }
.smj-chart-card__empty { margin: 0; padding: 30px 0; color: var(--ref-muted-text); font-size: 12px; text-align: center; }
@media (max-width: 480px) {
  .smj-chart-card__header { flex-direction: column; align-items: stretch; }
  .smj-chart-card__actions { justify-content: space-between; width: 100%; }
}
</style>
