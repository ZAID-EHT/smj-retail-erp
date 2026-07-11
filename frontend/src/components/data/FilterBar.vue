<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute } from "vue-router";

import FilterChip from "./FilterChip.vue";

const props = defineProps({
  entity: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  filters: { type: Object, default: () => ({}) },
  request: { type: Object, required: true },
});
const emit = defineEmits(["search", "filter", "refresh", "clear", "page-size"]);
const route = useRoute();
const searchText = ref(route.query.q || "");
let searchTimer;

watch(() => route.query.q, (value) => { searchText.value = value || ""; });
watch(searchText, (value) => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => emit("search", value.trim()), 350);
});
onBeforeUnmount(() => window.clearTimeout(searchTimer));

const activeFilters = computed(() => {
  const result = [];
  for (const definition of props.entity.filters) {
    const value = props.filters[definition.fieldname];
    if (value == null || value === "") continue;
    if (typeof value === "object") {
      if (value.from) result.push({ key: `${definition.fieldname}:from`, fieldname: definition.fieldname, boundary: "from", label: `${definition.label} from`, value: value.from });
      if (value.to) result.push({ key: `${definition.fieldname}:to`, fieldname: definition.fieldname, boundary: "to", label: `${definition.label} to`, value: value.to });
    } else {
      const option = definition.values?.find((entry) => String(entry.value) === String(value));
      result.push({ key: definition.fieldname, fieldname: definition.fieldname, label: definition.label, value: option?.label || value });
    }
  }
  return result;
});
</script>

<template>
  <section class="ref-filter-panel" aria-label="List filters">
    <div class="ref-filter-panel__primary">
      <label class="ref-list-search">
        <span aria-hidden="true">⌕</span>
        <input v-model="searchText" type="search" placeholder="Search records" autocomplete="off" />
      </label>

      <template v-for="definition in entity.filters" :key="definition.fieldname">
        <label v-if="definition.type === 'DateRange'" class="ref-filter-control ref-filter-control--dates">
          <span>{{ definition.label }}</span>
          <span class="ref-date-range">
            <input
              type="date"
              :value="filters[definition.fieldname]?.from || ''"
              :aria-label="`${definition.label} from`"
              @change="emit('filter', definition.fieldname, $event.target.value, 'from')"
            />
            <input
              type="date"
              :value="filters[definition.fieldname]?.to || ''"
              :aria-label="`${definition.label} to`"
              @change="emit('filter', definition.fieldname, $event.target.value, 'to')"
            />
          </span>
        </label>
        <label v-else class="ref-filter-control">
          <span>{{ definition.label }}</span>
          <select
            :value="filters[definition.fieldname] ?? ''"
            @change="emit('filter', definition.fieldname, $event.target.value)"
          >
            <option value="">All</option>
            <option v-for="option in definition.values" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
      </template>
    </div>

    <div class="ref-filter-panel__secondary">
      <div class="ref-filter-chips">
        <FilterChip
          v-for="chip in activeFilters"
          :key="chip.key"
          :label="chip.label"
          :value="String(chip.value)"
          @remove="emit('filter', chip.fieldname, '', chip.boundary)"
        />
      </div>
      <div class="ref-filter-actions">
        <label class="ref-page-size">
          <span>Rows</span>
          <select :value="request.page_size" @change="emit('page-size', Number($event.target.value))">
            <option :value="10">10</option><option :value="20">20</option><option :value="50">50</option><option :value="100">100</option>
          </select>
        </label>
        <button type="button" :disabled="loading" @click="emit('clear')">Clear filters</button>
        <button type="button" :disabled="loading" @click="emit('refresh')">↻ Refresh</button>
      </div>
    </div>
  </section>
</template>
