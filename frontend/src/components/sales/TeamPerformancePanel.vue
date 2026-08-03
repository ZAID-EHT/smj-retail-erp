<script setup>
import { ref, watch } from "vue";
import { getTeamPerformance } from "@/services/commission.js";

const props = defineProps({ team: { type: String, required: true } });

const data = ref(null);
const loading = ref(false);
const denied = ref(false);
const range = ref({ from_date: "", to_date: "" });

let token = 0;

async function load() {
  const mine = ++token;
  loading.value = true;
  denied.value = false;
  try {
    const result = await getTeamPerformance({ team: props.team, ...range.value });
    if (mine !== token) return;
    data.value = result;
  } catch (caught) {
    if (mine !== token) return;
    // Commission totals are permission-gated; an ordinary user simply sees nothing
    // rather than an error shouting at them.
    denied.value = true;
    data.value = null;
  } finally {
    if (mine === token) loading.value = false;
  }
}

watch(() => props.team, load, { immediate: true });

function money(value) {
  const n = Number(value || 0);
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
</script>

<template>
  <section v-if="!denied" class="rug-section-card smj-team-performance"
           data-test="team-performance">
    <header>
      <h2>Performance</h2>
      <p>Read from transaction snapshots, never from the current team rows.</p>
    </header>

    <div class="smj-team-performance__range">
      <label><span>From</span><input v-model="range.from_date" type="date" @change="load" /></label>
      <label><span>To</span><input v-model="range.to_date" type="date" @change="load" /></label>
    </div>

    <div v-if="loading" class="smj-team-card__state" role="status">Loading performance…</div>

    <div v-else-if="data" class="smj-team-performance__grid">
      <div><span>Assigned customers</span><strong>{{ data.assigned_customers }}</strong></div>
      <div><span>Active customers</span><strong>{{ data.active_customers }}</strong></div>
      <div><span>Sales orders</span><strong>{{ data.orders }}</strong></div>
      <div><span>Estimated commission</span><strong>{{ money(data.estimated_commission) }}</strong></div>
      <div><span>Invoiced sales</span><strong>{{ money(data.invoiced_sales) }}</strong></div>
      <div><span>Returns</span><strong>{{ money(data.returned_sales) }}</strong></div>
      <div><span>Earned commission</span><strong>{{ money(data.earned_commission) }}</strong></div>
      <div><span>Reversed</span><strong>{{ money(data.reversed_commission) }}</strong></div>
      <div class="is-total">
        <span>Net commission</span>
        <strong data-test="team-net-commission">{{ money(data.net_commission) }}</strong>
      </div>
    </div>
  </section>
</template>
