<script setup>
/* A type-to-search dropdown that looks like the rest of the forms.

   The fields this replaces used a native <datalist>. That works, but the popup it
   opens is drawn by the browser, not by the page: it ignores every style here and
   on this platform renders as a dark list with none of the form's spacing or
   rounding, which is exactly the mismatch the requirement points at. So the list
   is drawn here instead -- the same panel the price-code picker already uses.

   Strict by default: the field holds one of the offered values or nothing. Typing
   only narrows the list, and text that matches no option is dropped when the field
   is left rather than saved as a value nobody can choose again. `freeText` opts a
   field out of that where anything typed is genuinely acceptable. */
import { computed, nextTick, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: "Type to search…" },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  freeText: { type: Boolean, default: false },
  emptyText: { type: String, default: "Nothing matches that." },
  noOptionsText: { type: String, default: "There is nothing to choose from yet." },
  inputId: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue"]);

// Null while the field is showing its value; a string once the user starts typing.
const query = ref(null);
const open = ref(false);
const active = ref(0);
const input = ref(null);
let blurTimer;

const display = computed(() => (query.value === null ? props.modelValue || "" : query.value));

/* A value already on the record but no longer offered -- deactivated, or renamed
   after the record was saved -- is still listed, so opening an old record never
   silently blanks the field. */
const allOptions = computed(() => {
  const current = props.modelValue;
  if (current && !props.options.includes(current)) return [current, ...props.options];
  return props.options;
});

const matches = computed(() => {
  if (query.value === null) return allOptions.value;
  const text = query.value.trim().toLowerCase();
  if (!text) return allOptions.value;
  return allOptions.value.filter((option) => option.toLowerCase().includes(text));
});

function show() {
  if (props.disabled) return;
  open.value = true;
  active.value = Math.max(0, matches.value.indexOf(props.modelValue));
}

function pick(option) {
  emit("update:modelValue", option);
  query.value = null;
  open.value = false;
}

function onInput(event) {
  query.value = event.target.value;
  if (props.freeText) emit("update:modelValue", event.target.value);
  show();
}

/* Leaving the field settles what it holds. An exact match is taken as a choice, so
   typing a full value and tabbing away works; anything else is discarded, which is
   what keeps a strict field strict. */
function settle() {
  if (query.value === null) return;
  const typed = query.value.trim();
  const exact = allOptions.value.find((option) => option.toLowerCase() === typed.toLowerCase());
  if (exact) emit("update:modelValue", exact);
  else if (props.freeText) emit("update:modelValue", typed);
  else if (!typed) emit("update:modelValue", "");
  query.value = null;
}

function clear() {
  emit("update:modelValue", "");
  query.value = null;
  open.value = false;
  nextTick(() => input.value?.focus());
}

function onKeydown(event) {
  if (event.key === "Escape") { open.value = false; query.value = null; return; }
  if (!open.value && ["ArrowDown", "ArrowUp"].includes(event.key)) { show(); return; }
  if (event.key === "ArrowDown") {
    event.preventDefault();
    active.value = Math.min(active.value + 1, matches.value.length - 1);
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    active.value = Math.max(active.value - 1, 0);
  } else if (event.key === "Enter") {
    const option = matches.value[active.value];
    // Only swallow Enter when it is choosing something; otherwise it stays the
    // form's own submit key.
    if (open.value && option) { event.preventDefault(); pick(option); }
  } else if (event.key === "Tab") {
    settle();
    open.value = false;
  }
}

// A click on an option fires after blur, so closing waits long enough for the
// mousedown handler to run.
function closeSoon() {
  window.clearTimeout(blurTimer);
  blurTimer = window.setTimeout(() => { settle(); open.value = false; }, 140);
}

watch(() => query.value, () => { active.value = 0; });
</script>

<template>
  <div class="cb" :class="{ 'is-disabled': disabled }">
    <div class="cb__control">
      <input
        :id="inputId || undefined"
        ref="input"
        :value="display"
        type="text"
        role="combobox"
        aria-autocomplete="list"
        :aria-expanded="open"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        autocomplete="off"
        @focus="show"
        @input="onInput"
        @keydown="onKeydown"
        @blur="closeSoon"
      />
      <button
        v-if="modelValue && !disabled"
        type="button"
        class="cb__clear"
        aria-label="Clear"
        @mousedown.prevent="clear"
      >&times;</button>
    </div>

    <ul v-if="open" class="cb__list" role="listbox">
      <li v-if="!matches.length" class="is-state">
        {{ allOptions.length ? emptyText : noOptionsText }}
      </li>
      <li
        v-for="option in matches"
        :key="option"
        role="option"
        :aria-selected="option === modelValue"
        :class="{ 'is-active': matches[active] === option, 'is-chosen': option === modelValue }"
        @mousedown.prevent="pick(option)"
        @mousemove="active = matches.indexOf(option)"
      >{{ option }}</li>
    </ul>
  </div>
</template>

<style scoped>
.cb{position:relative}
.cb__control{position:relative;display:block}
.cb__control input{width:100%;min-height:44px;padding:0 2rem 0 .8rem;border:1px solid var(--ref-border-colour);border-radius:.75rem;background:var(--ref-card-background);color:var(--ref-primary-text);font:inherit}
.cb.is-disabled .cb__control input{opacity:.6}
.cb__clear{position:absolute;top:50%;right:.4rem;width:24px;height:24px;padding:0;transform:translateY(-50%);border:0;border-radius:6px;background:transparent;color:var(--ref-secondary-text);font-size:17px;line-height:1;cursor:pointer}
.cb__clear:hover{background:var(--ref-blue-background);color:var(--ref-primary-text)}
.cb__list{position:absolute;z-index:60;top:calc(100% + 4px);right:0;left:0;max-height:17rem;margin:0;padding:.3rem;overflow-y:auto;border:1px solid var(--ref-border-colour);border-radius:.65rem;background:var(--ref-card-background, #fff);box-shadow:0 16px 34px rgba(23,32,51,.18);list-style:none}
.cb__list li{padding:.5rem .6rem;border-radius:.45rem;font-weight:500;cursor:pointer}
.cb__list li.is-active{background:var(--ref-blue-background)}
.cb__list li.is-chosen{font-weight:700}
.cb__list li.is-state{color:var(--ref-secondary-text);font-size:.8rem;cursor:default}
</style>
