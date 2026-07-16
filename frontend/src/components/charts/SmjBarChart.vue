<script setup>
const props = defineProps({
  bars: { type: Array, required: true }, // [{ label, value, color }]
  valueFormatter: { type: Function, default: (value) => Number(value).toLocaleString() },
});

const max = () => Math.max(...props.bars.map((bar) => Number(bar.value || 0)), 1);
</script>

<template>
  <ul class="smj-barchart">
    <li v-for="bar in bars" :key="bar.label">
      <span class="smj-barchart__label">{{ bar.label }}</span>
      <span class="smj-barchart__track">
        <i :style="{ width: `${(Number(bar.value || 0) / max()) * 100}%`, background: bar.color }" />
      </span>
      <b class="smj-barchart__value">{{ valueFormatter(bar.value) }}</b>
    </li>
  </ul>
</template>

<style scoped>
.smj-barchart { display: grid; gap: 12px; margin: 0; padding: 0; list-style: none; }
.smj-barchart li { display: grid; grid-template-columns: minmax(90px, 130px) minmax(0, 1fr) auto; align-items: center; gap: 10px; font-size: 11px; }
.smj-barchart__label { overflow: hidden; color: var(--ref-secondary-text); text-overflow: ellipsis; white-space: nowrap; }
.smj-barchart__track { display: block; height: 10px; overflow: hidden; border-radius: 999px; background: var(--ref-divider-colour); }
.smj-barchart__track i { display: block; height: 100%; border-radius: inherit; transition: width .3s ease; }
.smj-barchart__value { min-width: 55px; color: var(--ref-primary-text); font-weight: 700; text-align: right; font-variant-numeric: tabular-nums; }
</style>
