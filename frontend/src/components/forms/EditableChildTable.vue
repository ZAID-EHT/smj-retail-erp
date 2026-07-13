<script setup>
import FormField from "./FormField.vue";
const props = defineProps({ modelValue: { type: Array, default: () => [] }, table: { type: Object, required: true }, entityKey: { type: String, required: true }, errors: { type: Object, default: () => ({}) } });
const emit = defineEmits(["update:modelValue"]);
function update(rowIndex, fieldname, value) { const rows = props.modelValue.map((row) => ({ ...row })); rows[rowIndex][fieldname] = value; emit("update:modelValue", rows); }
function add() { emit("update:modelValue", [...props.modelValue, { qty: 1, conversion_factor: 1, discount_percentage: 0 }]); }
function remove(index) { emit("update:modelValue", props.modelValue.filter((_row, rowIndex) => rowIndex !== index)); }
</script>
<template>
  <section class="ref-editable-table"><header><div><h2>{{ table.title }}</h2><small>{{ modelValue.length }} row{{ modelValue.length === 1 ? '' : 's' }}</small></div><button class="ref-button ref-button--secondary" type="button" @click="add">+ Add item</button></header>
    <div v-if="!modelValue.length" class="ref-child-empty">Add at least one item to continue.</div>
    <article v-for="(row, rowIndex) in modelValue" :key="rowIndex" class="ref-editable-row"><div class="ref-editable-row__fields"><FormField v-for="field in table.fields" :key="field.fieldname" :model-value="row[field.fieldname]" :field="field" :entity-key="entityKey" :error="errors[`${rowIndex}.${field.fieldname}`]" @update:model-value="update(rowIndex, field.fieldname, $event)" /></div><button type="button" class="ref-row-remove" @click="remove(rowIndex)">Remove</button></article>
  </section>
</template>
