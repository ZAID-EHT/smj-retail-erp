<script setup>
const props = defineProps({ entity: { type: Object, required: true }, record: { type: Object, required: true } });
defineEmits(["open"]);

function labelFor(fieldname) {
  return props.entity.columns.find((column) => column.fieldname === fieldname)?.label || fieldname;
}

function display(fieldname) {
  const column = props.entity.columns.find((item) => item.fieldname === fieldname);
  const value = props.record[fieldname];
  if (column?.type === "enabled_status") return Number(value) ? "Disabled" : "Enabled";
  if (column?.type === "currency") return `${props.record.currency || "LKR"} ${Number(value || 0).toLocaleString()}`;
  return value ?? "—";
}
</script>

<template>
  <article class="ref-mobile-record-card" tabindex="0" @click="$emit('open')" @keydown.enter="$emit('open')">
    <img
      v-if="record.image !== undefined"
      :src="record.image || '/assets/my_store_ui/images/product-placeholder.svg'"
      :alt="record[entity.primary_field] || record.name"
      loading="lazy"
      @error="$event.target.src = '/assets/my_store_ui/images/product-placeholder.svg'"
    />
    <div class="ref-mobile-record-card__content">
      <h3>{{ record[entity.primary_field] || record.name }}</h3>
      <code v-if="record[entity.secondary_field]">{{ record[entity.secondary_field] }}</code>
      <dl>
        <template v-for="fieldname in entity.mobile_fields" :key="fieldname">
          <dt>{{ labelFor(fieldname) }}</dt><dd>{{ display(fieldname) }}</dd>
        </template>
      </dl>
    </div>
    <button type="button" disabled title="Actions will be added with detail pages" @click.stop>⋮</button>
  </article>
</template>
