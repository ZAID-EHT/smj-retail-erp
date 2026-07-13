<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { searchRetailERP } from "@/services/globalSearch.js";

const router = useRouter();
const root = ref(null);
const input = ref(null);
const query = ref("");
const results = ref([]);
const loading = ref(false);
const error = ref("");
const focused = ref(false);
const activeIndex = ref(-1);
let timer;
let controller;

const open = computed(() => focused.value && query.value.trim().length >= 2);
const groups = computed(() => {
  const grouped = new Map();
  for (const result of results.value) {
    if (!grouped.has(result.group)) grouped.set(result.group, []);
    grouped.get(result.group).push(result);
  }
  return [...grouped.entries()].map(([label, records]) => ({ label, records }));
});

async function runSearch(text) {
  controller?.abort();
  if (text.length < 2) { results.value = []; loading.value = false; return; }
  controller = new AbortController();
  loading.value = true;
  error.value = "";
  try {
    results.value = await searchRetailERP(text, controller.signal);
    activeIndex.value = results.value.length ? 0 : -1;
  } catch (requestError) {
    if (requestError.name !== "AbortError") error.value = requestError.message;
  } finally {
    if (!controller.signal.aborted) loading.value = false;
  }
}

watch(query, (value) => {
  clearTimeout(timer);
  timer = setTimeout(() => runSearch(value.trim()), 300);
});

function choose(result) {
  query.value = "";
  results.value = [];
  focused.value = false;
  router.push(result.route);
}

function onKeydown(event) {
  if (event.key === "ArrowDown" && results.value.length) {
    event.preventDefault();
    activeIndex.value = (activeIndex.value + 1) % results.value.length;
  } else if (event.key === "ArrowUp" && results.value.length) {
    event.preventDefault();
    activeIndex.value = (activeIndex.value - 1 + results.value.length) % results.value.length;
  } else if (event.key === "Enter" && activeIndex.value >= 0) {
    event.preventDefault();
    choose(results.value[activeIndex.value]);
  } else if (event.key === "Escape") {
    focused.value = false;
    input.value?.blur();
  }
}

function globalShortcut(event) {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "g") {
    event.preventDefault();
    input.value?.focus();
  }
}

function outsideClick(event) {
  if (!root.value?.contains(event.target)) focused.value = false;
}

onMounted(() => {
  document.addEventListener("keydown", globalShortcut);
  document.addEventListener("click", outsideClick);
});
onBeforeUnmount(() => {
  clearTimeout(timer);
  controller?.abort();
  document.removeEventListener("keydown", globalShortcut);
  document.removeEventListener("click", outsideClick);
});
</script>

<template>
  <div ref="root" class="ref-global-search" role="search" :class="{ 'is-open': open }">
    <span class="ref-global-search__icon" aria-hidden="true">⌕</span>
    <input
      ref="input"
      v-model="query"
      type="search"
      role="combobox"
      aria-label="Global search"
      aria-controls="retail-global-search-results"
      :aria-expanded="open"
      aria-autocomplete="list"
      placeholder="Search permitted records"
      autocomplete="off"
      @focus="focused = true"
      @keydown="onKeydown"
    />
    <span v-if="loading" class="ref-search-spinner" aria-label="Searching"></span>
    <kbd v-else>Ctrl G</kbd>
    <div v-if="open" id="retail-global-search-results" class="ref-search-results" role="listbox">
      <p v-if="loading" class="ref-search-message">Searching permitted records…</p>
      <p v-else-if="error" class="ref-search-message ref-search-message--error">{{ error }}</p>
      <p v-else-if="!results.length" class="ref-search-message">No permitted records found.</p>
      <template v-else>
        <section v-for="group in groups" :key="group.label">
          <h2>{{ group.label }}</h2>
          <button
            v-for="result in group.records"
            :key="`${result.doctype}-${result.name}`"
            type="button"
            role="option"
            :aria-selected="results[activeIndex] === result"
            :class="{ 'is-active': results[activeIndex] === result }"
            @mousemove="activeIndex = results.indexOf(result)"
            @click="choose(result)"
          >
            <span><strong>{{ result.title }}</strong><small>{{ result.name }}</small></span>
            <small>{{ result.subtitle }}</small>
          </button>
        </section>
      </template>
    </div>
  </div>
</template>
