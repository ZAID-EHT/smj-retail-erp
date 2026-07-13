<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import { searchLinkOptions } from "@/services/entityForms.js";

const props = defineProps({ modelValue: { type: [String, Number], default: "" }, field: { type: Object, required: true }, entityKey: { type: String, required: true }, disabled: Boolean });
const emit = defineEmits(["update:modelValue"]);
const options = ref([]); const open = ref(false); let timer; let controller;
const query = ref(props.modelValue || "");
watch(() => props.modelValue, (value) => { if (value !== query.value) query.value = value || ""; });
watch(query, (value) => { emit("update:modelValue", value); window.clearTimeout(timer); timer = window.setTimeout(async () => {
  controller?.abort(); controller = new AbortController();
  try { options.value = await searchLinkOptions(props.entityKey, props.field.fieldname, value, controller.signal); open.value = true; } catch (error) { if (error.name !== "AbortError") options.value = []; }
}, 240); });
onBeforeUnmount(() => { window.clearTimeout(timer); controller?.abort(); });
function select(option) { query.value = option.value; emit("update:modelValue", option.value); open.value = false; }
</script>
<template>
  <div class="ref-link-field">
    <input v-model="query" :disabled="disabled" :required="field.required" type="search" autocomplete="off" @focus="open = true" @keydown.escape="open = false" />
    <ul v-if="open && options.length" class="ref-link-field__options" role="listbox"><li v-for="option in options" :key="option.value" role="option" @mousedown.prevent="select(option)"><strong>{{ option.label }}</strong><small v-if="option.label !== option.value">{{ option.value }}</small></li></ul>
  </div>
</template>
