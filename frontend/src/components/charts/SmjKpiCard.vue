<script setup>
import { computed } from "vue";
import SmjSparkline from "./SmjSparkline.vue";

const props = defineProps({
  label: { type: String, required: true },
  value: { type: String, required: true },
  icon: { type: [Object, Function], default: null },
  accent: { type: String, default: "blue" },
  trend: { type: Number, default: null },
  trendLabel: { type: String, default: "vs last month" },
  spark: { type: Array, default: () => [] },
  to: { type: String, default: "" },
});

const trendDirection = computed(() => {
  if (props.trend == null) return null;
  return props.trend >= 0 ? "up" : "down";
});
</script>

<template>
  <component :is="to ? 'RouterLink' : 'div'" :to="to || undefined" class="smj-kpi-card" :data-accent="accent">
    <div class="smj-kpi-card__top">
      <span class="smj-kpi-card__label">{{ label }}</span>
      <span v-if="icon" class="smj-kpi-card__icon"><component :is="icon" size="16" decorative /></span>
    </div>
    <strong class="smj-kpi-card__value">{{ value }}</strong>
    <div class="smj-kpi-card__footer">
      <span v-if="trendDirection" class="smj-kpi-card__trend" :class="`is-${trendDirection}`">
        {{ trendDirection === "up" ? "▲" : "▼" }} {{ Math.abs(trend).toFixed(1) }}%
        <small>{{ trendLabel }}</small>
      </span>
      <SmjSparkline v-if="spark.length > 1" :values="spark" color="var(--ref-accent)" :height="28" />
    </div>
  </component>
</template>

<style scoped>
.smj-kpi-card { --ref-accent: var(--ref-primary-blue); display: grid; gap: 10px; min-width: 0; max-width: 100%; padding: 16px 18px; border: 1px solid var(--ref-border-colour); border-radius: var(--ref-card-radius); background: var(--ref-card-background); box-shadow: var(--ref-card-shadow); color: inherit; text-decoration: none !important; }
.smj-kpi-card__top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.smj-kpi-card__label { color: var(--ref-secondary-text); font-size: 12px; font-weight: 700; }
.smj-kpi-card__icon { display: grid; place-items: center; width: 30px; height: 30px; flex: 0 0 auto; border-radius: 9px; background: color-mix(in srgb, var(--ref-accent), white 88%); color: var(--ref-accent); }
.smj-kpi-card__value { color: var(--ref-primary-text); font: 700 24px/1.1 var(--ref-font); font-variant-numeric: tabular-nums; }
.smj-kpi-card__footer { display: grid; gap: 4px; min-height: 28px; }
.smj-kpi-card__trend { display: flex; align-items: baseline; gap: 5px; font-size: 11px; font-weight: 700; }
.smj-kpi-card__trend.is-up { color: var(--ref-success); }
.smj-kpi-card__trend.is-down { color: var(--ref-danger); }
.smj-kpi-card__trend small { color: var(--ref-muted-text); font-weight: 500; }
</style>
