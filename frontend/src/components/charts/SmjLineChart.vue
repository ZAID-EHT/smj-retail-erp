<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  labels: { type: Array, required: true },
  series: { type: Array, required: true }, // [{ name, color, values }]
  height: { type: Number, default: 220 },
  valueFormatter: { type: Function, default: (value) => Number(value).toLocaleString() },
});

const WIDTH = 600;
const PAD = { top: 12, right: 12, bottom: 24, left: 12 };
const hoverIndex = ref(null);

const bounds = computed(() => {
  const all = props.series.flatMap((entry) => entry.values).filter((value) => Number.isFinite(value));
  const max = all.length ? Math.max(...all, 0) : 0;
  const min = all.length ? Math.min(...all, 0) : 0;
  return { min, max: max === min ? max + 1 : max };
});

function pointsFor(values) {
  const { min, max } = bounds.value;
  const range = max - min || 1;
  const innerWidth = WIDTH - PAD.left - PAD.right;
  const innerHeight = props.height - PAD.top - PAD.bottom;
  return values.map((value, index) => {
    const x = PAD.left + (values.length > 1 ? (index / (values.length - 1)) * innerWidth : innerWidth / 2);
    const y = PAD.top + innerHeight - ((value - min) / range) * innerHeight;
    return [x, y];
  });
}

const seriesPaths = computed(() =>
  props.series.map((entry) => {
    const points = pointsFor(entry.values);
    const line = points.map(([x, y], index) => `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`).join(" ");
    return { ...entry, points, line };
  }),
);

const gridLines = computed(() => {
  const { min, max } = bounds.value;
  const steps = 4;
  return Array.from({ length: steps + 1 }, (_, index) => {
    const value = min + ((max - min) * index) / steps;
    const innerHeight = props.height - PAD.top - PAD.bottom;
    const y = PAD.top + innerHeight - (index / steps) * innerHeight;
    return { y, value };
  });
});

function onMove(event) {
  const svg = event.currentTarget;
  const rect = svg.getBoundingClientRect();
  const ratio = (event.clientX - rect.left) / rect.width;
  const count = props.labels.length;
  hoverIndex.value = Math.min(count - 1, Math.max(0, Math.round(ratio * (count - 1))));
}
</script>

<template>
  <div class="smj-linechart">
    <div class="smj-linechart__legend" v-if="series.length > 1">
      <span v-for="entry in series" :key="entry.name" class="smj-linechart__legend-item">
        <i :style="{ background: entry.color }" />{{ entry.name }}
      </span>
    </div>
    <svg
      :viewBox="`0 0 ${WIDTH} ${height}`"
      class="smj-linechart__svg"
      preserveAspectRatio="none"
      role="img"
      :aria-label="`Line chart: ${series.map((entry) => entry.name).join(', ')}`"
      @mousemove="onMove"
      @mouseleave="hoverIndex = null"
    >
      <line v-for="grid in gridLines" :key="grid.y" x1="0" :x2="WIDTH" :y1="grid.y" :y2="grid.y" class="smj-linechart__grid" />
      <path v-for="entry in seriesPaths" :key="entry.name" :d="entry.line" fill="none" :stroke="entry.color" class="smj-linechart__line" />
      <g v-if="hoverIndex !== null">
        <line :x1="seriesPaths[0]?.points[hoverIndex]?.[0]" :x2="seriesPaths[0]?.points[hoverIndex]?.[0]" y1="0" :y2="height" class="smj-linechart__hover-line" />
        <circle v-for="entry in seriesPaths" :key="`${entry.name}-dot`" :cx="entry.points[hoverIndex]?.[0]" :cy="entry.points[hoverIndex]?.[1]" r="4" :fill="entry.color" stroke="#fff" stroke-width="2" />
      </g>
    </svg>
    <div class="smj-linechart__axis">
      <span v-for="(label, index) in labels" :key="label" :class="{ 'is-hover': hoverIndex === index }">{{ label }}</span>
    </div>
    <div v-if="hoverIndex !== null" class="smj-linechart__tooltip">
      <strong>{{ labels[hoverIndex] }}</strong>
      <div v-for="entry in seriesPaths" :key="entry.name" class="smj-linechart__tooltip-row">
        <i :style="{ background: entry.color }" />{{ entry.name }}: <b>{{ valueFormatter(entry.values[hoverIndex]) }}</b>
      </div>
    </div>
  </div>
</template>

<style scoped>
.smj-linechart { position: relative; }
.smj-linechart__legend { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 8px; font-size: 11px; color: var(--ref-secondary-text); }
.smj-linechart__legend-item { display: inline-flex; align-items: center; gap: 5px; }
.smj-linechart__legend-item i { width: 8px; height: 8px; border-radius: 50%; }
.smj-linechart__svg { display: block; width: 100%; cursor: crosshair; }
.smj-linechart__grid { stroke: var(--ref-divider-colour); stroke-width: 1; }
.smj-linechart__line { stroke-width: 2.5; vector-effect: non-scaling-stroke; }
.smj-linechart__hover-line { stroke: var(--ref-border-colour); stroke-width: 1; }
.smj-linechart__axis { display: flex; justify-content: space-between; margin-top: 4px; color: var(--ref-muted-text); font-size: 10px; }
.smj-linechart__axis span.is-hover { color: var(--ref-primary-text); font-weight: 700; }
.smj-linechart__tooltip { position: absolute; top: 4px; right: 4px; display: grid; gap: 3px; padding: 8px 10px; border-radius: 8px; background: var(--ref-primary-text); color: #fff; font-size: 11px; box-shadow: var(--ref-float-shadow); pointer-events: none; }
.smj-linechart__tooltip strong { font-size: 10px; opacity: .8; }
.smj-linechart__tooltip-row { display: flex; align-items: center; gap: 5px; }
.smj-linechart__tooltip-row i { width: 7px; height: 7px; border-radius: 50%; }
</style>
