<script setup>
defineProps({ groups: { type: Array, default: () => [] }, loading: { type: Boolean, default: false } });
</script>

<template>
  <section class="ref-related-section">
    <header><h2>Related Documents</h2><span>Permission-filtered summaries</span></header>
    <div v-if="loading" class="ref-related-loading">Loading related records…</div>
    <div v-else-if="!groups.length" class="ref-child-empty">No related document types are available to your roles.</div>
    <div v-else class="ref-related-grid">
      <article v-for="group in groups" :key="group.doctype" class="ref-related-card">
        <header><div><strong>{{ group.title }}</strong><small>{{ group.doctype }}</small></div><b>{{ group.count }}{{ group.count_is_limited ? '+' : '' }}</b></header>
        <p v-if="!group.records.length">No records found.</p>
        <ul v-else>
          <li v-for="record in group.records" :key="record.name">
            <RouterLink v-if="record.custom_route" :to="record.custom_route">{{ record.name }}</RouterLink>
            <span v-else>{{ record.name }}</span>
            <small>{{ record.status || record.posting_date || record.transaction_date || '' }}</small>
            <a v-if="record.desk_route" :href="record.desk_route" title="Open in Standard Desk">Desk ↗</a>
          </li>
        </ul>
      </article>
    </div>
  </section>
</template>
