<script setup>
/* The SKU field's price-code picker.

   The requirement is specific: the SKU field offers the price codes and nothing
   else, grouped by product category, and the code must be typeable and searchable
   rather than hunted for in a long list. A native <select> cannot do that -- it
   groups but does not filter -- so this is a combobox: type to narrow, arrow keys
   or the mouse to choose, and the SKU the chosen code would issue is shown as the
   user picks. */
import { computed, nextTick, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  // [{ category, codes: [{ price_code, category, description, next_sku, … }] }]
  groups: { type: Array, default: () => [] },
  // When set, only this category's codes are offered: a code from another
  // category is refused on save, so it is not worth offering.
  category: { type: String, default: "" },
  disabled: { type: Boolean, default: false },
  placeholder: { type: String, default: "Type a code, category or description…" },
});
const emit = defineEmits(["update:modelValue"]);

const search = ref("");
const open = ref(false);
const active = ref(0);
const input = ref(null);
let blurTimer;

const scopedGroups = computed(() => (props.category
  ? props.groups.filter((group) => group.category === props.category)
  : props.groups));

/* Filtering keeps the grouping: a category whose codes all fail the search
   disappears with them, rather than leaving an empty heading behind. */
const filteredGroups = computed(() => {
  const text = search.value.trim().toLowerCase();
  if (!text) return scopedGroups.value;
  return scopedGroups.value
    .map((group) => ({
      category: group.category,
      codes: group.codes.filter((code) => (
        code.price_code.toLowerCase().includes(text)
        || (code.description || "").toLowerCase().includes(text)
        || (code.category || "").toLowerCase().includes(text)
      )),
    }))
    .filter((group) => group.codes.length);
});

// A flat view of what is on screen, so the arrow keys can walk the list across
// category boundaries without the template having to track indices.
const flat = computed(() => filteredGroups.value.flatMap((group) => group.codes));

const selected = computed(() => flat.value.find((code) => code.price_code === props.modelValue)
  || scopedGroups.value.flatMap((group) => group.codes).find((code) => code.price_code === props.modelValue)
  || null);

function show() {
  if (props.disabled) return;
  open.value = true;
  active.value = Math.max(0, flat.value.findIndex((code) => code.price_code === props.modelValue));
}

function pick(code) {
  emit("update:modelValue", code.price_code);
  search.value = "";
  open.value = false;
}

function clear() {
  emit("update:modelValue", "");
  search.value = "";
  open.value = false;
  nextTick(() => input.value?.focus());
}

function onKeydown(event) {
  if (event.key === "Escape") { open.value = false; return; }
  if (!open.value && ["ArrowDown", "ArrowUp", "Enter"].includes(event.key)) { show(); return; }
  if (event.key === "ArrowDown") {
    event.preventDefault();
    active.value = Math.min(active.value + 1, flat.value.length - 1);
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    active.value = Math.max(active.value - 1, 0);
  } else if (event.key === "Enter") {
    const code = flat.value[active.value];
    if (code) { event.preventDefault(); pick(code); }
  }
}

// A click on an option fires after blur, so closing is deferred long enough for
// the mousedown handler to run.
function closeSoon() {
  window.clearTimeout(blurTimer);
  blurTimer = window.setTimeout(() => { open.value = false; }, 120);
}

watch(() => search.value, () => { active.value = 0; });
// Narrowing to another category can strip the chosen code out of the list; the
// parent clears it, and the search box should not keep showing stale text.
watch(() => props.category, () => { search.value = ""; });
</script>

<template>
  <div class="pcs" :class="{ 'is-disabled': disabled }">
    <div class="pcs__control">
      <input
        ref="input"
        v-model="search"
        type="text"
        role="combobox"
        aria-autocomplete="list"
        :aria-expanded="open"
        :disabled="disabled"
        :placeholder="selected ? `${selected.price_code}${selected.description ? ' — ' + selected.description : ''}` : placeholder"
        :class="{ 'has-value': Boolean(selected) }"
        autocomplete="off"
        @focus="show"
        @input="show"
        @keydown="onKeydown"
        @blur="closeSoon"
      />
      <button
        v-if="selected && !disabled"
        type="button"
        class="pcs__clear"
        aria-label="Clear price code"
        @mousedown.prevent="clear"
      >&times;</button>
    </div>

    <ul v-if="open" class="pcs__list" role="listbox">
      <li v-if="!flat.length" class="is-state">
        {{ scopedGroups.length ? "No code matches that." : "No price codes for this category yet." }}
      </li>
      <template v-for="group in filteredGroups" :key="group.category">
        <li class="is-group" role="presentation">{{ group.category }}</li>
        <li
          v-for="code in group.codes"
          :key="code.name || code.price_code"
          role="option"
          :aria-selected="code.price_code === modelValue"
          :class="{ 'is-active': flat[active]?.price_code === code.price_code }"
          @mousedown.prevent="pick(code)"
          @mousemove="active = flat.findIndex((item) => item.price_code === code.price_code)"
        >
          <strong>{{ code.price_code }}</strong>
          <small>
            <template v-if="code.description">{{ code.description }} &middot; </template>
            next {{ code.next_sku }}
          </small>
        </li>
      </template>
    </ul>
  </div>
</template>

<style scoped>
.pcs{position:relative}
.pcs__control{position:relative;display:block}
.pcs__control input{width:100%;min-height:44px;padding:0 2rem 0 .8rem;border:1px solid var(--ref-border-colour);border-radius:.75rem;background:var(--ref-card-background);color:var(--ref-primary-text);font:inherit}
.pcs__control input.has-value::placeholder{color:var(--ref-primary-text);opacity:1}
.pcs.is-disabled .pcs__control input{opacity:.6}
.pcs__clear{position:absolute;top:50%;right:.4rem;width:24px;height:24px;padding:0;transform:translateY(-50%);border:0;border-radius:6px;background:transparent;color:var(--ref-secondary-text);font-size:17px;line-height:1;cursor:pointer}
.pcs__clear:hover{background:var(--ref-blue-background);color:var(--ref-primary-text)}
.pcs__list{position:absolute;z-index:60;top:calc(100% + 4px);right:0;left:0;max-height:17rem;margin:0;padding:.3rem;overflow-y:auto;border:1px solid var(--ref-border-colour);border-radius:.65rem;background:#fff;box-shadow:0 16px 34px rgba(23,32,51,.18);list-style:none}
.pcs__list li{display:grid;gap:1px;padding:.5rem .6rem;border-radius:.45rem;cursor:pointer}
.pcs__list li.is-active{background:var(--ref-blue-background)}
.pcs__list li.is-group{padding:.45rem .6rem .2rem;color:var(--ref-secondary-text);font-size:.68rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;cursor:default}
.pcs__list li.is-state{color:var(--ref-secondary-text);font-size:.8rem;font-weight:500;cursor:default}
.pcs__list small{color:var(--ref-secondary-text);font-weight:500}
</style>
