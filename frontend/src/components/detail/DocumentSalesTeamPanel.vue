<script setup>
import { ref, watch } from "vue";
import { getDocumentSalesTeam } from "@/services/salesTeam.js";

const props = defineProps({
  doctype: { type: String, required: true },
  name: { type: String, required: true },
});

const assignment = ref(null);
const members = ref([]);
const commission = ref(null);
const loading = ref(false);

let token = 0;

async function load() {
  const mine = ++token;
  loading.value = true;
  try {
    const result = await getDocumentSalesTeam(props.doctype, props.name);
    if (mine !== token) return;
    assignment.value = result.assigned ? result.assignment : null;
    members.value = result.members || [];
    commission.value = result.commission || null;
  } catch {
    if (mine === token) { assignment.value = null; members.value = []; }
  } finally {
    if (mine === token) loading.value = false;
  }
}

watch(() => [props.doctype, props.name], load, { immediate: true });

function money(value) {
  const n = Number(value || 0);
  return `${commission.value?.currency || ""} ${n.toLocaleString(undefined, {
    minimumFractionDigits: 2, maximumFractionDigits: 2 })}`.trim();
}
function pct(value) {
  const n = Number(value || 0);
  return `${Number.isInteger(n) ? n : n.toFixed(2)}%`;
}
</script>

<template>
  <section v-if="loading || assignment" class="rug-section-card smj-doc-team"
           data-test="document-sales-team">
    <header>
      <h2>Sales Team and Commission</h2>
      <p>Frozen when this document was raised. Later changes to the team never reach it.</p>
    </header>

    <div v-if="loading" class="smj-team-card__state" role="status">Loading sales team…</div>

    <template v-else>
      <p class="smj-team-card__team">
        <span>Sales Team</span>
        <strong>{{ assignment.team_name || assignment.team }}</strong>
        <small>Code {{ assignment.team }}</small>
      </p>

      <p class="smj-team-card__source">
        <span :class="assignment.source === 'Overridden' && 'is-overridden'">
          {{ assignment.source }}
        </span>
        <em v-if="assignment.override_reason">{{ assignment.override_reason }}</em>
      </p>

      <div v-if="commission" class="smj-commissions__totals">
        <span>Commission base <strong>{{ money(commission.base) }}</strong></span>
        <span>Team rate <strong>{{ pct(commission.rate) }}</strong></span>
        <span>Commission pool <strong>{{ money(commission.pool) }}</strong></span>
        <span>Status <strong>{{ commission.status }}</strong></span>
      </div>

      <div class="smj-table-scroll">
        <table class="rug-table" data-test="document-team-members">
          <thead>
            <tr>
              <th>Team Member</th><th>Role</th>
              <th class="is-num">Allocation</th><th class="is-num">Commission</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in members" :key="row.sales_person">
              <td>{{ row.sales_person_name || row.sales_person }}</td>
              <td>{{ row.team_role }}</td>
              <td class="is-num">{{ pct(row.allocation_percentage) }}</td>
              <td class="is-num"><strong>{{ money(row.commission_amount) }}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="assignment.captured_on" class="smj-customer-team__note">
        Frozen on {{ assignment.captured_on }} by {{ assignment.captured_by }}.
      </p>
    </template>
  </section>
</template>
