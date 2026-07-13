<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import { getLinkOptions } from "@/services/universal.js";

const props = defineProps({ modelValue: { default: null }, field: { type: Object, required: true }, feature: { type: String, required: true }, parentFieldname: { type: String, default: "" }, error: { type: String, default: "" } });
const emit = defineEmits(["update:modelValue"]);
const options = ref([]); const linkOpen = ref(false); const query = ref(String(props.modelValue ?? "")); let timer; let controller;
watch(() => props.modelValue, (value) => { if (String(value ?? "") !== query.value) query.value = String(value ?? ""); });
watch(query, (value) => {
  if (props.field.fieldtype !== "Link") return;
  emit("update:modelValue", value); window.clearTimeout(timer);
  timer = window.setTimeout(async () => {
    controller?.abort(); controller = new AbortController();
    try { options.value = (await getLinkOptions(props.feature, props.field.fieldname, value, props.parentFieldname || undefined, controller.signal)).results; linkOpen.value = true; }
    catch (error) { if (error.name !== "AbortError") options.value = []; }
  }, 250);
});
onBeforeUnmount(() => { window.clearTimeout(timer); controller?.abort(); });
function update(event) {
  const value = props.field.fieldtype === "Check" ? Number(event.target.checked) : event.target.value;
  emit("update:modelValue", value);
}
function select(option) { query.value = option.value; emit("update:modelValue", option.value); linkOpen.value = false; }
const textTypes = ["Small Text", "Text", "Long Text", "Text Editor", "Code"];
</script>

<template>
  <label :class="['ru-field', { 'ru-field--error': error, 'ru-field--wide': textTypes.includes(field.fieldtype) }]" :for="`ru-${parentFieldname}-${field.fieldname}`">
    <span>{{ field.label }} <b v-if="field.required" aria-hidden="true">*</b></span>
    <small v-if="field.description" class="ru-field__description">{{ field.description }}</small>
    <div v-if="field.fieldtype === 'Link'" class="ru-link">
      <input :id="`ru-${parentFieldname}-${field.fieldname}`" v-model="query" :readonly="field.read_only" :required="field.required" type="search" autocomplete="off" @focus="linkOpen = true" @keydown.escape="linkOpen = false" />
      <ul v-if="linkOpen && options.length" role="listbox"><li v-for="option in options" :key="option.value" role="option" @mousedown.prevent="select(option)"><strong>{{ option.label }}</strong><small>{{ option.value }}</small></li></ul>
    </div>
    <select v-else-if="field.fieldtype === 'Select'" :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :disabled="field.read_only" @change="update"><option value="">Select…</option><option v-for="option in field.options" :key="option" :value="option">{{ option }}</option></select>
    <textarea v-else-if="textTypes.includes(field.fieldtype)" :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :readonly="field.read_only" rows="4" @input="update" />
    <input v-else-if="field.fieldtype === 'Check'" :id="`ru-${parentFieldname}-${field.fieldname}`" :checked="Boolean(modelValue)" :disabled="field.read_only" type="checkbox" @change="update" />
    <input v-else-if="field.fieldtype === 'Attach' || field.fieldtype === 'Attach Image'" :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :readonly="field.read_only" type="url" placeholder="/files/example.ext" @input="update" />
    <input v-else :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :readonly="field.read_only" :required="field.required" :min="field.non_negative ? 0 : undefined" :maxlength="field.length || undefined" :type="field.fieldtype === 'Date' ? 'date' : field.fieldtype === 'Datetime' ? 'datetime-local' : field.fieldtype === 'Time' ? 'time' : field.fieldtype === 'Color' ? 'color' : ['Currency','Float','Int','Percent','Duration','Rating'].includes(field.fieldtype) ? 'number' : 'text'" :step="field.fieldtype === 'Int' ? 1 : 'any'" @input="update" />
    <small v-if="error" class="ru-field__error">{{ error }}</small>
  </label>
</template>
