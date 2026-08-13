<script setup>
import UniversalField from "./UniversalField.vue";
const props = defineProps({ modelValue: { type: Array, default: () => [] }, field: { type: Object, required: true }, feature: { type: String, required: true }, readOnly: Boolean });
const emit = defineEmits(["update:modelValue"]);
// Amount is calculated by the server on save, so until then the field sat
// blank and looked like something the user had forgotten to fill in. Every
// ERPNext transaction line means the same thing by it -- qty x rate -- so it is
// filled in as soon as both exist. This is display only: the field is read-only
// and the server strips it from the payload, so it can never disagree with the
// posted figure.
const CALCULATED = { amount: ["qty", "rate"] };
function update(index, fieldname, value) {
  const rows = props.modelValue.map((row) => ({ ...row }));
  rows[index][fieldname] = value;
  for (const [target, [left, right]] of Object.entries(CALCULATED)) {
    if (fieldname !== left && fieldname !== right) continue;
    if (!(props.field.child_fields || []).some((item) => item.fieldname === target)) continue;
    const a = Number(rows[index][left]); const b = Number(rows[index][right]);
    rows[index][target] = Number.isFinite(a) && Number.isFinite(b) ? a * b : null;
  }
  emit("update:modelValue", rows);
}
function add() { const row = Object.fromEntries((props.field.child_fields || []).filter((item) => item.default != null).map((item) => [item.fieldname, item.default])); emit("update:modelValue", [...props.modelValue, row]); }
function remove(index) { emit("update:modelValue", props.modelValue.filter((_row, position) => position !== index)); }
function duplicate(index) { emit("update:modelValue", [...props.modelValue.slice(0, index + 1), { ...props.modelValue[index], name: undefined, idx: undefined }, ...props.modelValue.slice(index + 1)]); }
function move(index, offset) { const target = index + offset; if (target < 0 || target >= props.modelValue.length) return; const rows = [...props.modelValue]; [rows[index], rows[target]] = [rows[target], rows[index]]; emit("update:modelValue", rows); }
</script>
<template>
  <section class="ru-child"><header><div><h2>{{ field.label }}</h2><p v-if="field.description" class="ru-child__description">{{ field.description }}</p><small>{{ modelValue.length }} row{{ modelValue.length === 1 ? '' : 's' }}</small></div><button v-if="!readOnly" class="ref-button ref-button--secondary" type="button" @click="add">+ Add {{ field.options === 'Has Role' ? 'role' : 'row' }}</button></header>
    <div v-if="!modelValue.length" class="ru-empty">No rows yet.</div>
    <article v-for="(row, index) in modelValue" :key="row.name || index" class="ru-child__row">
      <div class="ru-child__fields"><UniversalField v-for="child in field.child_fields" :key="child.fieldname" :model-value="row[child.fieldname]" :field="{ ...child, read_only: readOnly || child.read_only }" :feature="feature" :parent-fieldname="field.fieldname" :context="row" @update:model-value="update(index, child.fieldname, $event)" /></div>
      <div v-if="!readOnly" class="ru-child__actions"><button type="button" @click="move(index, -1)" :disabled="index === 0" aria-label="Move row up">↑</button><button type="button" @click="move(index, 1)" :disabled="index === modelValue.length - 1" aria-label="Move row down">↓</button><button type="button" @click="duplicate(index)">Duplicate</button><button type="button" @click="remove(index)">Remove</button></div>
    </article>
  </section>
</template>
