<script setup>
import { ref, watch } from "vue";
import { getCustomerSalesAssignment } from "@/services/salesTeam.js";
import { getCustomerCommissionHistory } from "@/services/commission.js";
import SalesTeamCard from "@/components/sales/SalesTeamCard.vue";

const props = defineProps({ customer: { type: String, required: true } });

const assignment = ref(null);
const warnings = ref([]);
const loading = ref(false);
const transactions = ref([]);
const history = ref([]);
const error = ref("");

// A late response for a customer that is no longer open must never win.
let token = 0;

async function load() {
  const mine = ++token;
  loading.value = true;
  error.value = "";
  try {
    const [team, past] = await Promise.all([
      getCustomerSalesAssignment(props.customer),
      getCustomerCommissionHistory({ customer: props.customer }),
    ]);
    if (mine !== token) return;
    assignment.value = team.assigned ? team.assignment : null;
    warnings.value = team.warnings || [];
    transactions.value = past.transactions || [];
    history.value = past.assignment_history || [];
  } catch (caught) {
    if (mine !== token) return;
    error.value = caught?.message || "The sales team could not be loaded.";
    assignment.value = null;
  } finally {
    if (mine === token) loading.value = false;
  }
}

watch(() => props.customer, load, { immediate: true });

function money(value, currency) {
  const n = Number(value || 0);
  return `${currency || ""} ${n.toLocaleString(undefined, {
    minimumFractionDigits: 2, maximumFractionDigits: 2 })}`.trim();
}
</script>

<template>
  <div class="smj-customer-team">
    <SalesTeamCard
      :assignment="assignment"
      :loading="loading"
      :warnings="warnings"
      empty-message="No sales team is assigned to this customer."
    />
    <p v-if="error" class="smj-team-card__warning" role="alert">{{ error }}</p>

    <section v-if="transactions.length" class="rug-section-card">
      <header><h2>Recent orders and commission</h2></header>
      <div class="smj-table-scroll">
        <table class="rug-table" data-test="customer-team-transactions">
          <thead>
            <tr>
              <th>Date</th><th>Sales Order</th><th>Team</th><th>Source</th>
              <th class="is-num">Order Total</th><th class="is-num">Base</th>
              <th class="is-num">Rate</th><th class="is-num">Pool</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in transactions" :key="row.sales_order">
              <td>{{ row.date }}</td>
              <td><router-link :to="`/sales/orders/${encodeURIComponent(row.sales_order)}`">
                {{ row.sales_order }}</router-link></td>
              <td>{{ row.team_name }}</td>
              <td>
                {{ row.team_source }}
                <small v-if="row.override_reason">{{ row.override_reason }}</small>
              </td>
              <td class="is-num">{{ money(row.order_total, row.currency) }}</td>
              <td class="is-num">{{ money(row.commission_base, row.currency) }}</td>
              <td class="is-num">{{ row.commission_rate }}%</td>
              <td class="is-num">{{ money(row.commission_pool, row.currency) }}</td>
              <td>{{ row.is_draft ? "Draft" : row.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="smj-customer-team__note">
        Each row shows the team the order was raised with. Reassigning this customer
        does not change any of them.
      </p>
    </section>

    <section v-if="history.length" class="rug-section-card">
      <header><h2>Team assignment history</h2></header>
      <div class="smj-table-scroll">
        <table class="rug-table" data-test="customer-team-history">
          <thead><tr><th>Changed</th><th>By</th><th>From</th><th>To</th></tr></thead>
          <tbody>
            <tr v-for="(row, index) in history" :key="`${row.changed_on}-${index}`">
              <td>{{ row.changed_on }}</td>
              <td>{{ row.changed_by }}</td>
              <td>{{ row.previous_team || "—" }}</td>
              <td>{{ row.new_team || "—" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
