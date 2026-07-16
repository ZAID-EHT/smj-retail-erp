<script setup>
import { computed } from "vue";

const props = defineProps({
  values: { type: Array, default: () => [] },
  color: { type: String, default: "currentColor" },
  height: { type: Number, default: 36 },
});

const path = computed(() => {
  const values = props.values.filter((value) => Number.isFinite(value));
  if (values.length < 2) return { line: "", area: "" };
  const width = 100;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const points = values.map((value, index) => {
    const x = (index / (values.length - 1)) * width;
    const y = props.height - ((value - min) / range) * props.height;
    return [x, y];
  });
  const line = points.map(([x, y], index) => `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`).join(" ");
  const area = `${line} L${width},${props.height} L0,${props.height} Z`;
  return { line, area };
});
</script>

<template>
  <svg
    v-if="path.line"
    class="smj-sparkline"
    :viewBox="`0 0 100 ${height}`"
    preserveAspectRatio="none"
    aria-hidden="true"
  >
    <path :d="path.area" class="smj-sparkline__area" :style="{ fill: color }" />
    <path :d="path.line" class="smj-sparkline__line" :style="{ stroke: color }" fill="none" />
  </svg>
</template>

<style scoped>
.smj-sparkline { display: block; width: 100%; height: v-bind('`${height}px`'); overflow: visible; }
.smj-sparkline__area { opacity: .12; }
.smj-sparkline__line { stroke-width: 2; vector-effect: non-scaling-stroke; }
</style>
