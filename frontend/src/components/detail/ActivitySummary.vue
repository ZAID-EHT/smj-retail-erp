<script setup>
import { formatDetailValue } from "@/services/detailFormatters.js";

defineProps({ activity: { type: Object, required: true } });
</script>

<template>
  <section class="ref-activity-summary">
    <h2>Activity Summary</h2>
    <dl>
      <div><dt>Created by</dt><dd>{{ activity.owner || '—' }}</dd></div>
      <div><dt>Created</dt><dd>{{ formatDetailValue(activity.created, 'datetime') }}</dd></div>
      <div><dt>Modified by</dt><dd>{{ activity.modified_by || '—' }}</dd></div>
      <div><dt>Last modified</dt><dd>{{ formatDetailValue(activity.modified, 'datetime') }}</dd></div>
    </dl>
    <p>Full comments, assignments and timeline activity will be added in a later approved stage.</p>
  </section>
</template>
