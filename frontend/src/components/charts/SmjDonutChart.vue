<script setup>
import { computed } from "vue";

const props = defineProps({
  segments: { type: Array, required: true }, // [{ label, value, color }]
  centerLabel: { type: String, default: "" },
  centerValue: { type: String, default: "" },
  valueFormatter: { type: Function, default: (value) => Number(value).toLocaleString() },
});

const total = computed(() => props.segments.reduce((sum, seg) => sum + Number(seg.value || 0), 0));

const arcs = computed(() => {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;
  return props.segments.map((seg) => {
    const fraction = total.value > 0 ? Number(seg.value || 0) / total.value : 0;
    const length = fraction * circumference;
    const arc = { ...seg, fraction, dasharray: `${length} ${circumference - length}`, dashoffset: -offset, radius };
    offset += length;
    return arc;
  });
});
</script>

<template>
  <div class="smj-donut">
    <svg viewBox="0 0 100 100" class="smj-donut__svg" role="img" aria-label="Donut chart">
      <circle cx="50" cy="50" r="42" fill="none" stroke="var(--ref-divider-colour)" stroke-width="14" />
      <circle
        v-for="arc in arcs"
        :key="arc.label"
        cx="50" cy="50" :r="arc.radius"
        fill="none" :stroke="arc.color" stroke-width="14"
        :stroke-dasharray="arc.dasharray"
        :stroke-dashoffset="arc.dashoffset"
        transform="rotate(-90 50 50)"
        stroke-linecap="round"
      />
      <text x="50" y="47" text-anchor="middle" class="smj-donut__center-value">{{ centerValue }}</text>
      <text x="50" y="60" text-anchor="middle" class="smj-donut__center-label">{{ centerLabel }}</text>
    </svg>
    <ul class="smj-donut__legend">
      <li v-for="arc in arcs" :key="arc.label">
        <i :style="{ background: arc.color }" />
        <span>{{ arc.label }}</span>
        <b>{{ (arc.fraction * 100).toFixed(0) }}% ({{ valueFormatter(arc.value) }})</b>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.smj-donut { display: flex; flex-wrap: wrap; align-items: center; gap: 18px; min-width: 0; }
.smj-donut__svg { width: 130px; height: 130px; flex: 0 0 auto; }
.smj-donut__center-value { fill: var(--ref-primary-text); font: 700 13px var(--ref-font); }
.smj-donut__center-label { fill: var(--ref-muted-text); font: 500 6px var(--ref-font); text-transform: uppercase; letter-spacing: .04em; }
.smj-donut__legend { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; min-width: 0; flex: 1 1 160px; }
.smj-donut__legend li { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 7px; min-width: 0; font-size: 11px; }
.smj-donut__legend i { width: 9px; height: 9px; flex: 0 0 auto; border-radius: 3px; }
.smj-donut__legend span { overflow: hidden; color: var(--ref-secondary-text); text-overflow: ellipsis; white-space: nowrap; }
.smj-donut__legend b { margin-left: auto; flex: 0 1 auto; min-width: 0; color: var(--ref-primary-text); font-variant-numeric: tabular-nums; }
@media (max-width: 480px) {
  .smj-donut__legend li { flex-direction: column; align-items: flex-start; gap: 2px; }
  .smj-donut__legend b { margin-left: 0; }
}
</style>
