<script setup>
import { reactive, ref } from "vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import { listHistoricalReview, recordHistoricalDecision } from "@/services/commissionAdmin.js";

const data = ref(null);
const loading = ref(false);
const denied = ref(false);
const error = ref("");
const notice = ref("");
const filters = reactive({ status: "", doctype_filter: "" });

// A late response for filters the user has already changed must never win.
let token = 0;

async function load() {
  const mine = ++token;
  loading.value = true;
  error.value = "";
  try {
    const result = await listHistoricalReview({ ...filters });
    if (mine !== token) return;
    data.value = result;
  } catch (caught) {
    if (mine !== token) return;
    if (caught?.response?.status === 403) denied.value = true;
    else error.value = caught?.message || "The review list could not be loaded.";
  } finally {
    if (mine === token) loading.value = false;
  }
}
load();

async function decide(row, status) {
  const reason = window.prompt(`Why is ${row.source_name} being marked "${status}"?`);
  if (!reason) return;
  let team = "";
  if (status === "Assigned") {
    team = window.prompt("Which team does the evidence on the document support?") || "";
    if (!team) return;
  }
  error.value = "";
  try {
    await recordHistoricalDecision({
      source_doctype: row.source_doctype, source_name: row.source_name,
      status, reason, team, confidence: status === "Assigned" ? "Evidence on document" : "",
    });
    notice.value = `${row.source_name} recorded as ${status}.`;
    await load();
  } catch (caught) {
    error.value = caught?.message || "The decision could not be recorded.";
  }
}

function money(value) {
  return Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="denied" />
    <main v-else class="rug-page smj-historical">
      <header class="rug-banner rug-banner--green">
        <div>
          <span class="rug-badge">Sales</span>
          <h1>Historical Commission Review</h1>
          <p>
            Documents raised before the sales team feature existed. A human decides
            each one; nothing is assigned automatically.
          </p>
        </div>
        <div class="rug-banner-actions">
          <button type="button" @click="load">Refresh</button>
        </div>
      </header>

      <p v-if="notice" class="smj-sales-notice" role="status">{{ notice }}</p>
      <p v-if="error" class="smj-team-card__warning" role="alert">{{ error }}</p>
      <p v-if="data?.note" class="smj-commissions__scope" data-test="historical-note">
        {{ data.note }}
      </p>

      <section class="rug-section-card">
        <div class="rug-form-grid">
          <label><span>Status</span>
            <select v-model="filters.status" @change="load">
              <option value="">Any</option>
              <option v-for="s in data?.statuses || []" :key="s" :value="s">{{ s }}</option>
            </select>
          </label>
          <label><span>Document</span>
            <select v-model="filters.doctype_filter" @change="load">
              <option value="">Both</option>
              <option value="Sales Order">Sales Order</option>
              <option value="Sales Invoice">Sales Invoice</option>
            </select>
          </label>
        </div>
      </section>

      <section class="rug-section-card">
        <div v-if="loading" class="smj-team-card__state" role="status">Loading documents…</div>
        <div v-else-if="!data?.rows?.length" class="smj-team-card__state">
          Nothing is awaiting historical review.
        </div>
        <div v-else class="smj-table-scroll">
          <table class="rug-table smj-commissions__table" data-test="historical-table">
            <thead>
              <tr>
                <th>Document</th><th>Date</th><th>Customer</th><th class="is-num">Total</th>
                <th>Sales People On Document</th><th>Customer's Team Today</th>
                <th>Evidence</th><th>Suggested</th><th>Status</th><th>Reviewer</th><th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.rows" :key="`${row.source_doctype}-${row.source_name}`">
                <td>{{ row.source_name }}<small>{{ row.source_doctype }}</small></td>
                <td>{{ row.date }}</td>
                <td>{{ row.customer_name }}</td>
                <td class="is-num">{{ money(row.grand_total) }}</td>
                <td>
                  <template v-if="row.existing_sales_persons.length">
                    <span v-for="p in row.existing_sales_persons" :key="p.sales_person">
                      {{ p.sales_person }} ({{ p.allocated_percentage }}%)
                    </span>
                  </template>
                  <em v-else>none</em>
                </td>
                <td>
                  {{ row.customer_current_team || "—" }}
                  <small>not evidence</small>
                </td>
                <td>{{ row.has_reliable_evidence ? "Yes" : "No" }}</td>
                <td>{{ row.suggested_team || "—" }}</td>
                <td><span class="smj-pill" :data-status="row.status">{{ row.status }}</span></td>
                <td>{{ row.reviewer || "—" }}</td>
                <td class="smj-historical__actions">
                  <button v-if="row.has_reliable_evidence" type="button"
                          data-test="historical-assign" @click="decide(row, 'Assigned')">Assign</button>
                  <button type="button" data-test="historical-exclude"
                          @click="decide(row, 'Excluded')">Exclude</button>
                  <button type="button" @click="decide(row, 'No Reliable Evidence')">No evidence</button>
                  <button type="button" @click="decide(row, 'Escalated')">Escalate</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </PageContainer>
</template>
