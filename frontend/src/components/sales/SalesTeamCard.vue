<script setup>
import { computed } from "vue";

const props = defineProps({
  assignment: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  // Shown before anything has been chosen (e.g. before a customer is selected).
  idle: { type: Boolean, default: false },
  idleMessage: { type: String, default: "Select a customer to load the assigned sales team." },
  emptyMessage: { type: String, default: "No sales team is assigned to this customer." },
  canEdit: { type: Boolean, default: false },
  historical: { type: Boolean, default: false },
});
defineEmits(["edit"]);

const members = computed(() => props.assignment?.members || []);
const total = computed(() =>
  Math.round(members.value.reduce((sum, m) => sum + Number(m.share_percentage || 0), 0) * 100) / 100);
const balanced = computed(() => Math.abs(total.value - 100) < 0.01);

function pct(value) {
  const n = Number(value || 0);
  return `${Number.isInteger(n) ? n : n.toFixed(2)}%`;
}
</script>

<template>
  <section class="smj-team-card rug-section-card" aria-labelledby="smj-team-card-title">
    <header>
      <div>
        <h2 id="smj-team-card-title">Sales Team and Commission</h2>
        <p v-if="historical">Recorded when this document was raised.</p>
      </div>
      <button v-if="canEdit && !loading" type="button" @click="$emit('edit')">
        Edit assignment
      </button>
    </header>

    <div v-if="loading" class="smj-team-card__state" role="status">Loading sales team…</div>

    <div v-else-if="idle" class="smj-team-card__state">{{ idleMessage }}</div>

    <div v-else-if="!assignment" class="smj-team-card__state">{{ emptyMessage }}</div>

    <template v-else>
      <p class="smj-team-card__team">
        <span>Sales Team</span>
        <strong>{{ assignment.team_name || assignment.team }}</strong>
      </p>

      <ul class="smj-team-card__members">
        <li v-for="member in members" :key="member.sales_person">
          <strong>{{ member.sales_person }}</strong>
          <span>{{ member.role }}</span>
          <em>{{ pct(member.share_percentage) }}</em>
        </li>
      </ul>

      <footer class="smj-team-card__totals">
        <span>Team Commission Rate <strong>{{ pct(assignment.commission_rate) }}</strong></span>
        <span :class="!balanced && 'is-warning'">
          Total Allocation <strong>{{ pct(total) }}</strong>
        </span>
      </footer>
    </template>
  </section>
</template>
