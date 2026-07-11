<script setup>
import { formatDetailValue } from "@/services/detailFormatters.js";

defineProps({ table: { type: Object, required: true }, currency: { type: String, default: "LKR" } });
</script>

<template>
  <section class="ref-child-table-section">
    <header><h2>{{ table.title }}</h2><span>{{ table.count }} rows</span></header>
    <div v-if="!table.rows.length" class="ref-child-empty">No {{ table.title.toLowerCase() }} recorded.</div>
    <template v-else>
      <div class="ref-child-table-wrap">
        <table class="ref-child-table">
          <thead><tr><th v-for="column in table.columns" :key="column.fieldname">{{ column.label }}</th></tr></thead>
          <tbody>
            <tr v-for="(row, index) in table.rows" :key="index">
              <td v-for="column in table.columns" :key="column.fieldname" :class="{ 'is-multiline': column.type === 'multiline' }">
                {{ formatDetailValue(row[column.fieldname], column.type, currency) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="ref-child-mobile-list">
        <article v-for="(row, index) in table.rows" :key="index">
          <strong>Row {{ index + 1 }}</strong>
          <dl><template v-for="column in table.columns" :key="column.fieldname">
            <dt>{{ column.label }}</dt><dd>{{ formatDetailValue(row[column.fieldname], column.type, currency) }}</dd>
          </template></dl>
        </article>
      </div>
    </template>
  </section>
</template>
