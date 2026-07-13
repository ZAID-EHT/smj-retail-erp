<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import ActivitySummary from "@/components/detail/ActivitySummary.vue";
import DetailSection from "@/components/detail/DetailSection.vue";
import DetailSummaryCard from "@/components/detail/DetailSummaryCard.vue";
import ReadOnlyChildTable from "@/components/detail/ReadOnlyChildTable.vue";
import RelatedDocuments from "@/components/detail/RelatedDocuments.vue";
import SalesOrderActions from "@/components/detail/SalesOrderActions.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import RecordNotFound from "@/components/feedback/RecordNotFound.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { detailStatusClass, formatDetailValue } from "@/services/detailFormatters.js";
import { useEntityDetail } from "@/stores/entityDetail.js";

const route = useRoute();
const entityKey = computed(() => route.meta.entityKey);
const state = useEntityDetail(entityKey);
const data = computed(() => state.detail);
const currency = computed(() => data.value?.document?.currency || data.value?.document?.default_currency || "LKR");
const status = computed(() => data.value?.document?.[data.value.entity.status_field]);
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="state.permissionDenied" message="You do not have permission to view this record." />
    <RecordNotFound v-else-if="state.notFound" :name="state.recordName" :back-route="route.meta.backRoute" />
    <ErrorState
      v-else-if="state.error"
      :title="state.error.authenticationRequired ? 'Session expired' : 'Unable to load record'"
      :message="state.error.authenticationRequired ? 'Please sign in again, then reopen this record.' : state.error.message"
    />
    <div v-else-if="data" class="ref-detail-page">
      <header class="ref-detail-header">
        <img
          v-if="data.entity.image_field"
          :src="data.document[data.entity.image_field] || '/assets/my_store_ui/images/product-placeholder.svg'"
          :alt="data.document[data.entity.title_field]"
          @error="$event.target.src = '/assets/my_store_ui/images/product-placeholder.svg'"
        />
        <div class="ref-detail-header__copy">
          <span class="ref-entity-page__eyebrow">LIVE ERPNEXT RECORD</span>
          <h1>{{ data.document[data.entity.title_field] }}</h1>
          <code v-if="data.document[data.entity.subtitle_field] !== data.document[data.entity.title_field]">{{ data.document[data.entity.subtitle_field] }}</code>
          <div class="ref-detail-badges">
            <span class="ref-status-badge" :data-status="detailStatusClass(status, data.entity.status_type)">
              {{ formatDetailValue(status, data.entity.status_type) }}
            </span>
            <span v-if="data.entity.key === 'items'" class="ref-status-badge" data-status="blue">
              {{ data.document.is_stock_item ? 'Stock Item' : 'Non-stock Item' }}
            </span>
          </div>
        </div>
        <div class="ref-detail-actions">
          <RouterLink class="ref-button ref-button--secondary" :to="data.entity.back_route">← Back</RouterLink>
          <button type="button" class="ref-button ref-button--secondary" :disabled="state.loading" @click="state.load">↻ Refresh</button>
          <button v-if="data.permissions.can_print" type="button" class="ref-button ref-button--secondary" disabled title="Print support is planned">Print</button>
          <RouterLink v-if="data.permissions.can_write && (!data.entity.draft_only || data.document.docstatus === 0)" class="ref-button ref-button--primary" :to="`${data.entity.back_route}/${encodeURIComponent(data.document.name)}/edit`">Edit</RouterLink>
          <a v-if="data.entity.desk_route" class="ref-button ref-button--secondary" :href="data.entity.desk_route">Standard Desk ↗</a>
        </div>
      </header>

      <div class="ref-detail-summary-grid">
        <DetailSummaryCard v-for="field in data.summary" :key="field.fieldname" :field="field" :currency="currency" />
      </div>

      <div class="ref-detail-sections-grid">
        <DetailSection v-for="section in data.sections" :key="section.key" :section="section" :currency="currency" />
      </div>

      <ReadOnlyChildTable v-for="table in data.child_tables" :key="table.fieldname" :table="table" :currency="currency" />
      <RelatedDocuments :groups="data.related" />
      <SalesOrderActions v-if="data.entity.key === 'sales_orders'" :document="data.document" @refresh="state.load" />
      <ActivitySummary :activity="data.activity" />
    </div>
    <div v-else class="ref-detail-loading" role="status" aria-live="polite">
      <span class="ref-spinner"></span><strong>Loading record details…</strong>
      <i v-for="index in 6" :key="index"></i>
    </div>
  </PageContainer>
</template>
