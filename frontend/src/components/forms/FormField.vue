<script setup>
import LinkField from "./LinkField.vue";
const props = defineProps({ modelValue: { default: null }, field: { type: Object, required: true }, entityKey: { type: String, required: true }, error: { type: String, default: "" } });
const emit = defineEmits(["update:modelValue"]);
const update = (event) => emit("update:modelValue", props.field.fieldtype === "Check" ? Number(event.target.checked) : event.target.value);
</script>
<template>
  <label :class="['ref-form-field', { 'has-error': error, 'is-wide': field.fieldtype === 'Text' }]">
    <span>{{ field.label }} <b v-if="field.required">*</b></span>
    <LinkField v-if="field.fieldtype === 'Link'" :model-value="modelValue" :field="field" :entity-key="entityKey" :disabled="field.read_only" @update:model-value="emit('update:modelValue', $event)" />
    <select v-else-if="field.fieldtype === 'Select'" :value="modelValue ?? ''" :disabled="field.read_only" :required="field.required" @change="update"><option value="">Select…</option><option v-for="option in field.options" :key="option" :value="option">{{ option }}</option></select>
    <textarea v-else-if="field.fieldtype === 'Text'" :value="modelValue ?? ''" :readonly="field.read_only" :required="field.required" @input="update" />
    <input v-else-if="field.fieldtype === 'Check'" :checked="Boolean(modelValue)" :disabled="field.read_only" type="checkbox" @change="update" />
    <input v-else :value="modelValue ?? ''" :readonly="field.read_only" :required="field.required" :type="field.fieldtype === 'Date' ? 'date' : ['Currency','Percent','Float','Int'].includes(field.fieldtype) ? 'number' : 'text'" :step="field.fieldtype === 'Percent' || field.fieldtype === 'Currency' ? '0.01' : 'any'" @input="update" />
    <small v-if="error">{{ error }}</small>
  </label>
</template>
