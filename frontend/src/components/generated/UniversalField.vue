<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import { getLinkOptions } from "@/services/universal.js";

const props = defineProps({ modelValue: { default: null }, field: { type: Object, required: true }, feature: { type: String, required: true }, parentFieldname: { type: String, default: "" }, context: { type: Object, default: () => ({}) }, error: { type: String, default: "" } });
const emit = defineEmits(["update:modelValue"]);
const options = ref([]); const linkOpen = ref(false); const linkLoading = ref(false); const activeIndex = ref(-1); const query = ref(String(props.modelValue ?? "")); let timer; let controller; let closeTimer;
watch(() => props.modelValue, (value) => { if (String(value ?? "") !== query.value) query.value = String(value ?? ""); });
watch(query, (value) => {
  if (!["Link", "Dynamic Link"].includes(props.field.fieldtype)) return;
  emit("update:modelValue", value); window.clearTimeout(timer);
  if (linkOpen.value) timer = window.setTimeout(() => loadOptions(value), 250);
});
onBeforeUnmount(() => { window.clearTimeout(timer); window.clearTimeout(closeTimer); controller?.abort(); });
async function loadOptions(value = query.value) {
  controller?.abort(); const requestController = new AbortController(); controller = requestController; linkLoading.value = true;
  try {
    options.value = (await getLinkOptions(props.feature, props.field.fieldname, value, props.parentFieldname || undefined, requestController.signal, props.field.fieldtype === "Dynamic Link" ? props.context[props.field.options] : undefined)).results;
    activeIndex.value = options.value.length ? 0 : -1;
  } catch (error) {
    if (error.name !== "AbortError") options.value = [];
  } finally {
    if (!requestController.signal.aborted) linkLoading.value = false;
  }
}
function openLink() {
  if (props.field.read_only) return;
  window.clearTimeout(closeTimer); linkOpen.value = true; loadOptions();
}
function closeLink() { closeTimer = window.setTimeout(() => { linkOpen.value = false; }, 120); }
function onLinkKeydown(event) {
  if (event.key === "ArrowDown" && options.value.length) { event.preventDefault(); activeIndex.value = (activeIndex.value + 1) % options.value.length; }
  else if (event.key === "ArrowUp" && options.value.length) { event.preventDefault(); activeIndex.value = (activeIndex.value - 1 + options.value.length) % options.value.length; }
  else if (event.key === "Enter" && linkOpen.value && activeIndex.value >= 0) { event.preventDefault(); select(options.value[activeIndex.value]); }
  else if (event.key === "Escape") { event.preventDefault(); linkOpen.value = false; }
}
function update(event) {
  const value = props.field.fieldtype === "Check" ? Number(event.target.checked) : event.target.value;
  emit("update:modelValue", value);
}
function select(option) { query.value = option.value; emit("update:modelValue", option.value); linkOpen.value = false; }
function emptyMessage() {
  if (props.field.options === "Role Profile") return "No matching Role Profiles. Add individual roles in the Roles Assigned table below.";
  return `No matching permitted ${props.field.options || "options"}.`;
}
const textTypes = ["Small Text", "Text", "Long Text", "Text Editor", "Code"];
// A `readonly` input still looks and focuses exactly like a typeable one, so a
// calculated figure such as Amount reads as something you are meant to fill in.
// Marking it also drops it out of the tab order: nothing about it should invite
// an edit that the server would discard anyway.
const isCalculated = () => Boolean(props.field.read_only);
</script>

<template>
  <label :class="['ru-field', { 'ru-field--error': error, 'ru-field--wide': textTypes.includes(field.fieldtype) }]" :for="`ru-${parentFieldname}-${field.fieldname}`">
    <span>{{ field.label }} <b v-if="field.required && !isCalculated()" aria-hidden="true">*</b><em v-if="isCalculated()" class="ru-field__calc">calculated</em></span>
    <small v-if="field.description" class="ru-field__description">{{ field.description }}</small>
    <div v-if="field.fieldtype === 'Link' || field.fieldtype === 'Dynamic Link'" class="ru-link">
      <input :id="`ru-${parentFieldname}-${field.fieldname}`" v-model="query" :readonly="field.read_only" :required="field.required" :placeholder="`Search ${field.options || 'options'}…`" type="search" autocomplete="off" role="combobox" :aria-expanded="linkOpen" aria-autocomplete="list" @focus="openLink" @blur="closeLink" @keydown="onLinkKeydown" />
      <ul v-if="linkOpen" role="listbox">
        <li v-if="linkLoading" class="ru-link__message" role="status">Loading permitted options…</li>
        <li v-else-if="!options.length" class="ru-link__message">{{ emptyMessage() }}</li>
        <template v-else><li v-for="(option, index) in options" :key="option.value" role="option" :aria-selected="index === activeIndex" :class="{ 'is-active': index === activeIndex }" @mousemove="activeIndex = index" @mousedown.prevent="select(option)"><strong>{{ option.label }}</strong><small v-if="option.label !== option.value">{{ option.value }}</small></li></template>
      </ul>
    </div>
    <select v-else-if="field.fieldtype === 'Select'" :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :disabled="field.read_only" @change="update"><option value="">Select…</option><option v-for="option in field.options" :key="option" :value="option">{{ option }}</option></select>
    <textarea v-else-if="textTypes.includes(field.fieldtype)" :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :readonly="field.read_only" rows="4" @input="update" />
    <input v-else-if="field.fieldtype === 'Check'" :id="`ru-${parentFieldname}-${field.fieldname}`" :checked="Boolean(modelValue)" :disabled="field.read_only" type="checkbox" @change="update" />
    <input v-else-if="field.fieldtype === 'Attach' || field.fieldtype === 'Attach Image'" :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :readonly="field.read_only" type="url" placeholder="/files/example.ext" @input="update" />
    <input v-else-if="field.fieldtype === 'Password'" :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :readonly="field.read_only" :required="field.required" type="password" autocomplete="new-password" @input="update" />
    <input v-else :id="`ru-${parentFieldname}-${field.fieldname}`" :value="modelValue ?? ''" :readonly="field.read_only" :class="{ 'is-calculated': isCalculated() }" :tabindex="isCalculated() ? -1 : undefined" :required="field.required" :min="field.non_negative ? 0 : undefined" :maxlength="field.length || undefined" :type="field.fieldtype === 'Date' ? 'date' : field.fieldtype === 'Datetime' ? 'datetime-local' : field.fieldtype === 'Time' ? 'time' : field.fieldtype === 'Color' ? 'color' : ['Currency','Float','Int','Percent','Duration','Rating'].includes(field.fieldtype) ? 'number' : 'text'" :step="field.fieldtype === 'Int' ? 1 : 'any'" @input="update" />
    <small v-if="error" class="ru-field__error">{{ error }}</small>
  </label>
</template>
