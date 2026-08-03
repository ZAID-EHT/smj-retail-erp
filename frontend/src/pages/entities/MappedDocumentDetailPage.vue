<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute } from "vue-router";

import EntityActions from "@/components/detail/EntityActions.vue";
import DocumentSalesTeamPanel from "@/components/detail/DocumentSalesTeamPanel.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import RecordNotFound from "@/components/feedback/RecordNotFound.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { getMappedDraftDetail } from "@/services/entityForms.js";

const route = useRoute();
const entityKey = computed(() => route.meta.entityKey);
const data = ref(null);
const error = ref(null);
const loading = ref(false);
const denied = ref(false);
const notFound = ref(false);
let controller;

// Only the selling documents carry a frozen team; a Payment Entry does not.
const teamDoctype = computed(
  () => ({ delivery_notes: "Delivery Note", sales_invoices: "Sales Invoice" })[entityKey.value] || "",
);
const backRoute = computed(
  () =>
    ({
      delivery_notes: "/sales/delivery-notes",
      sales_invoices: "/sales/invoices",
      payment_entries: "/finance/payments",
    })[entityKey.value] || "/home",
);
const loadErrorMessage = computed(() =>
  error.value?.authenticationRequired
    ? "Your session expired. Please sign in again."
    : "The document could not be loaded. Please retry.",
);

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  data.value = null;
  error.value = null;
  denied.value = false;
  notFound.value = false;
  try {
    data.value = await getMappedDraftDetail(entityKey.value, route.params.name, controller.signal);
  } catch (requestError) {
    if (requestError.name === "AbortError") return;
    denied.value = Boolean(requestError.permissionDenied && !requestError.notFound);
    notFound.value = Boolean(requestError.notFound);
    error.value = requestError;
  } finally {
    loading.value = false;
  }
}

watch(() => route.fullPath, load, { immediate: true });
onBeforeUnmount(() => controller?.abort());
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="denied" />
    <RecordNotFound
      v-else-if="notFound"
      :name="String(route.params.name || '')"
      :back-route="backRoute"
    />
    <ErrorState
      v-else-if="error"
      title="Unable to load document"
      :message="loadErrorMessage"
      action-label="Retry"
      @action="load"
    />
    <div v-else-if="loading || !data" class="ref-detail-loading">
      <span class="ref-spinner" />
      <strong>Loading document…</strong>
    </div>
    <div v-else class="ref-form-page">
      <header class="ref-entity-page__header">
        <div>
          <span class="ref-entity-page__eyebrow">RETAIL ERP DOCUMENT</span>
          <h1>{{ data.entity.title }} {{ data.document.name }}</h1>
          <p>{{ data.status || "Draft" }} · {{ data.document.party || data.document.customer }}</p>
        </div>
        <RouterLink
          v-if="data.permissions.can_write && data.docstatus === 0"
          class="ref-button ref-button--primary"
          :to="`${data.entity.back_route}/${encodeURIComponent(data.document.name)}/edit`"
        >
          Edit Draft
        </RouterLink>
      </header>

      <section class="ref-form-section">
        <h2>Totals</h2>
        <div class="ref-pricing-preview">
          <strong>Net: {{ data.totals.currency }} {{ Number(data.totals.net_total || 0).toLocaleString() }}</strong>
          <strong>Taxes: {{ data.totals.currency }} {{ Number(data.totals.taxes || 0).toLocaleString() }}</strong>
          <strong>Grand Total: {{ data.totals.currency }} {{ Number(data.totals.grand_total || 0).toLocaleString() }}</strong>
          <strong v-if="data.totals.paid_amount != null">Paid: {{ data.totals.currency }} {{ Number(data.totals.paid_amount || 0).toLocaleString() }}</strong>
        </div>
      </section>

      <section
        v-for="tableName in ['references', 'deductions']"
        v-if="data.document[tableName]?.length"
        :key="tableName"
        class="ref-editable-table"
      >
        <h2>{{ tableName === "references" ? "References" : "Deductions" }}</h2>
        <div class="ref-child-table-wrap">
          <table class="ref-child-table">
            <thead>
              <tr>
                <th
                  v-for="field in Object.keys(data.document[tableName][0]).filter((key) => !['name', 'column_break_2'].includes(key))"
                  :key="field"
                >
                  {{ field.replaceAll("_", " ") }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.document[tableName]" :key="row.name">
                <td
                  v-for="field in Object.keys(row).filter((key) => !['name', 'column_break_2'].includes(key))"
                  :key="field"
                >
                  {{ row[field] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="data.related?.length" class="ref-form-section">
        <h2>Related Documents</h2>
        <div class="ref-related-links">
          <RouterLink
            v-for="link in data.related"
            :key="`${link.doctype}-${link.name}`"
            class="ref-button ref-button--secondary"
            :to="link.route"
          >
            {{ link.label }}: {{ link.name }}
          </RouterLink>
        </div>
      </section>

      <section v-if="data.document.items" class="ref-editable-table">
        <h2>Items</h2>
        <div class="ref-child-table-wrap">
          <table class="ref-child-table">
            <thead><tr><th>Item</th><th>Quantity</th><th>Warehouse</th><th>Rate</th><th>Amount</th></tr></thead>
            <tbody>
              <tr v-for="row in data.document.items || []" :key="row.name">
                <td>{{ row.item_name || row.item_code }}</td>
                <td>{{ row.qty }} {{ row.uom }}</td>
                <td>{{ row.warehouse }}</td>
                <td>{{ row.rate }}</td>
                <td>{{ row.amount }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <DocumentSalesTeamPanel v-if="teamDoctype" :doctype="teamDoctype" :name="data.document.name" />

      <EntityActions :entity-key="entityKey" :document="data.document" @refresh="load" />
    </div>
  </PageContainer>
</template>
