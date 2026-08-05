<script setup>
/* A dropdown backed by the admin-managed Retail Option List, with the "add or
   delete these choices" button the requirement asks for beside it.

   Two shapes from one component: a plain <select> for the short fixed lists
   (Business Nature, Transport Method) and a type-to-search combobox for the long
   ones (City, Product Size, Product Material, Carpet Category). The manage button
   is rendered only when the server says this user may manage options, so it is
   absent for everyone but the admin rather than merely disabled. */
import { computed, onMounted, ref, watch } from "vue";
import { listOptions, optionAdminUrl } from "@/services/retailOptions.js";

const props = defineProps({
  modelValue: { type: String, default: "" },
  optionType: { type: String, required: true },
  label: { type: String, default: "" },
  searchable: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  placeholder: { type: String, default: "" },
  hint: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue"]);

const options = ref([]);
const canManage = ref(false);
const loading = ref(true);
const failed = ref(false);
// A stable id so the <datalist> and its input pair up even when several of these
// sit on the same form.
const listId = `opt-${props.optionType.toLowerCase().replace(/[^a-z]+/g, "-")}`;

const value = computed({
  get: () => props.modelValue || "",
  set: (next) => emit("update:modelValue", next),
});

/* A value already on the record but no longer offered (deactivated, or renamed
   after the record was saved) is still shown, so opening an old record never
   silently blanks the field. */
const shownOptions = computed(() => {
  const current = props.modelValue;
  if (current && !options.value.includes(current)) return [current, ...options.value];
  return options.value;
});

async function load() {
  loading.value = true;
  failed.value = false;
  try {
    const result = await listOptions(props.optionType);
    options.value = result?.options || [];
    canManage.value = Boolean(result?.can_manage);
  } catch {
    // A failed load must not block the form: the field stays usable with
    // whatever it already holds, and the hint says the list is unavailable.
    options.value = [];
    canManage.value = false;
    failed.value = true;
  } finally {
    loading.value = false;
  }
}

function manage() {
  window.open(optionAdminUrl(props.optionType), "_blank", "noopener");
}

// The admin page opens in another tab; refresh when this one is looked at again
// so a newly added choice appears without a manual reload.
function refreshOnFocus() {
  if (document.visibilityState === "visible") load();
}

onMounted(() => {
  load();
  document.addEventListener("visibilitychange", refreshOnFocus);
});
watch(() => props.optionType, load);
</script>

<template>
  <label class="opt-field">
    <span class="opt-field__label">
      {{ label }}<template v-if="required"> *</template>
      <button
        v-if="canManage"
        type="button"
        class="opt-field__manage"
        :title="`Add or delete ${label || optionType} options`"
        @click="manage"
      >Add / delete</button>
    </span>

    <template v-if="searchable">
      <input
        v-model="value"
        :list="listId"
        :required="required"
        :placeholder="placeholder || (loading ? 'Loading…' : 'Type to search…')"
        type="search"
        autocomplete="off"
      />
      <datalist :id="listId">
        <option v-for="option in shownOptions" :key="option" :value="option" />
      </datalist>
    </template>
    <select v-else v-model="value" :required="required">
      <option value="">Select…</option>
      <option v-for="option in shownOptions" :key="option" :value="option">{{ option }}</option>
    </select>

    <small v-if="failed" class="opt-field__warn">The list could not be loaded. Type the value instead.</small>
    <small v-else-if="hint">{{ hint }}</small>
  </label>
</template>

<style scoped>
.opt-field{display:grid;gap:.35rem;font-weight:700}
.opt-field :is(input,select){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.opt-field__label{display:flex;align-items:center;justify-content:space-between;gap:.5rem}
.opt-field__manage{border:1px solid var(--ref-border-colour);border-radius:.5rem;background:transparent;color:var(--ref-accent, var(--ref-primary-text));font-size:.72rem;font-weight:700;padding:.15rem .5rem;cursor:pointer}
.opt-field__manage:hover{background:var(--ref-card-background)}
.opt-field small{font-weight:500;color:var(--ref-secondary-text)}
.opt-field__warn{color:var(--ref-danger)}
</style>
