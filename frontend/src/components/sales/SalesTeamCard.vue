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
  canOverride: { type: Boolean, default: false },
  historical: { type: Boolean, default: false },
  warnings: { type: Array, default: () => [] },
});
defineEmits(["edit", "override"]);

// The snapshot on a raised document calls the split `allocation_percentage`; the
// live master calls it `share_percentage`. One card renders both.
const members = computed(() =>
  (props.assignment?.members || []).map((m) => ({
    person: m.sales_person_name || m.sales_person,
    id: m.sales_person,
    role: m.role || m.team_role,
    share: Number(m.allocation_percentage ?? m.share_percentage ?? 0),
    amount: m.commission_amount,
  })));

const manager = computed(() => members.value.find((m) => m.role === "Sales Manager") || null);
const representatives = computed(() => members.value.filter((m) => m.role !== "Sales Manager"));
const total = computed(() =>
  Math.round(members.value.reduce((sum, m) => sum + m.share, 0) * 100) / 100);
const balanced = computed(() => Math.abs(total.value - 100) < 0.01);
const overridden = computed(() => props.assignment?.source === "Overridden");
const inactive = computed(() =>
  props.assignment && props.assignment.is_active === false);

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
      <div class="smj-team-card__actions">
        <button v-if="canOverride && !loading && !historical" type="button"
                data-test="team-override" @click="$emit('override')">
          Use another team
        </button>
        <button v-if="canEdit && !loading" type="button" @click="$emit('edit')">
          Edit assignment
        </button>
      </div>
    </header>

    <div v-if="loading" class="smj-team-card__state" role="status">Loading sales team…</div>

    <div v-else-if="idle" class="smj-team-card__state">{{ idleMessage }}</div>

    <template v-else-if="!assignment">
      <div class="smj-team-card__state">{{ emptyMessage }}</div>
      <p v-for="warning in warnings" :key="warning" class="smj-team-card__warning" role="status">
        {{ warning }}
      </p>
    </template>

    <template v-else>
      <p v-if="inactive" class="smj-team-card__warning" role="status" data-test="team-inactive">
        This team is no longer active. A new order needs an active team.
      </p>
      <p v-for="warning in warnings" :key="warning" class="smj-team-card__warning" role="status">
        {{ warning }}
      </p>

      <p class="smj-team-card__team">
        <span>Sales Team</span>
        <strong>{{ assignment.team_name || assignment.team }}</strong>
        <small v-if="assignment.team">Code {{ assignment.team }}</small>
      </p>

      <p class="smj-team-card__source" data-test="team-source">
        <span :class="overridden && 'is-overridden'">
          {{ overridden ? "Overridden for this order" : "Customer default" }}
        </span>
        <em v-if="overridden && assignment.override_reason">{{ assignment.override_reason }}</em>
      </p>

      <ul class="smj-team-card__members">
        <li v-if="manager" :key="manager.id" class="is-manager">
          <strong>{{ manager.person }}</strong>
          <span>Sales Manager</span>
          <em>{{ pct(manager.share) }}</em>
        </li>
        <li v-for="rep in representatives" :key="rep.id">
          <strong>{{ rep.person }}</strong>
          <span>{{ rep.role }}</span>
          <em>{{ pct(rep.share) }}</em>
        </li>
      </ul>

      <footer class="smj-team-card__totals">
        <span>Team Commission Rate <strong>{{ pct(assignment.commission_rate) }}</strong></span>
        <span :class="!balanced && 'is-warning'" data-test="team-total">
          Total Allocation <strong>{{ pct(total) }}</strong>
        </span>
      </footer>
    </template>
  </section>
</template>
