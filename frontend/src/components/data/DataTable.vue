<script setup>
import SortButton from "./SortButton.vue";

const props = defineProps({
  entity: { type: Object, required: true },
  records: { type: Array, required: true },
  sortField: { type: String, default: "" },
  sortOrder: { type: String, default: "asc" },
});
const emit = defineEmits(["row", "sort"]);

function isSortable(fieldname) {
  return props.entity.sortable_fields.includes(fieldname);
}

function formatValue(record, column) {
  const value = record[column.fieldname];
  if (value == null || value === "") return "—";
  if (column.type === "date") return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
  if (column.type === "datetime") return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
  if (column.type === "currency") {
    try { return new Intl.NumberFormat(undefined, { style: "currency", currency: record.currency || "LKR" }).format(value); }
    catch { return `${record.currency || ""} ${Number(value).toLocaleString()}`.trim(); }
  }
  if (column.type === "percent") return `${Number(value).toFixed(0)}%`;
  if (column.type === "boolean") return Number(value) ? "Yes" : "No";
  if (column.type === "enabled_status") return Number(value) ? "Disabled" : "Enabled";
  return value;
}

function statusClass(value, type) {
  const normalized = String(value || "").toLowerCase();
  if (type === "enabled_status") return Number(value) ? "muted" : "green";
  if (["completed", "enabled", "paid", "submitted"].some((item) => normalized.includes(item))) return "green";
  if (["cancelled", "closed", "disabled"].some((item) => normalized.includes(item))) return "muted";
  if (["draft", "on hold"].some((item) => normalized.includes(item))) return "orange";
  return "blue";
}
</script>

<template>
  <div class="ref-data-table-wrap">
    <table class="ref-data-table">
      <thead><tr>
        <th v-for="column in entity.columns" :key="column.fieldname">
          <SortButton
            v-if="isSortable(column.fieldname)"
            :label="column.label"
            :active="sortField === column.fieldname"
            :order="sortOrder"
            @sort="emit('sort', column.fieldname)"
          />
          <span v-else>{{ column.label }}</span>
        </th>
        <th class="ref-row-action-heading"><span class="sr-only">Actions</span></th>
      </tr></thead>
      <tbody>
        <tr
          v-for="record in records"
          :key="record.name"
          tabindex="0"
          @click="emit('row', record)"
          @keydown.enter="emit('row', record)"
        >
          <td v-for="column in entity.columns" :key="column.fieldname" :data-label="column.label">
            <img
              v-if="column.type === 'image'"
              class="ref-record-image"
              :src="record[column.fieldname] || '/assets/my_store_ui/images/product-placeholder.svg'"
              :alt="record[entity.primary_field] || record.name"
              loading="lazy"
              @error="$event.target.src = '/assets/my_store_ui/images/product-placeholder.svg'"
            />
            <span
              v-else-if="column.type === 'status' || column.type === 'enabled_status'"
              class="ref-status-badge"
              :data-status="statusClass(record[column.fieldname], column.type)"
            >{{ formatValue(record, column) }}</span>
            <span v-else-if="column.type === 'percent'" class="ref-percent-cell">
              <span><i :style="{ width: `${Math.min(Number(record[column.fieldname]) || 0, 100)}%` }"></i></span>
              {{ formatValue(record, column) }}
            </span>
            <code v-else-if="column.type === 'code'">{{ formatValue(record, column) }}</code>
            <span v-else>{{ formatValue(record, column) }}</span>
          </td>
          <td class="ref-row-actions"><button type="button" disabled title="Actions will be added with detail pages" @click.stop>⋮</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
