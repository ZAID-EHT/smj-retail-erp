<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import DataTable from "@/components/data/DataTable.vue";
import FilterBar from "@/components/data/FilterBar.vue";
import MobileRecordCard from "@/components/data/MobileRecordCard.vue";
import Pagination from "@/components/data/Pagination.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { canCreate } from "@/services/permissions.js";
import { useEntityList } from "@/stores/entityList.js";

const route = useRoute();
const router = useRouter();
const entityKey = computed(() => route.meta.entityKey);
const state = useEntityList(entityKey);
const currentSort = computed(() => route.query.sort || state.entity?.default_sort?.field || "");
const currentOrder = computed(() => route.query.order || state.entity?.default_sort?.order || "asc");

function updateSearch(value) {
  if (String(route.query.q || "") === value) return;
  state.updateQuery({ q: value });
}

function changeSort(fieldname) {
  const order = currentSort.value === fieldname && currentOrder.value === "asc" ? "desc" : "asc";
  state.updateQuery({ sort: fieldname, order });
}

function openRecord(record) {
  const target = state.entity.detail_route.replace("{name}", encodeURIComponent(record.name));
  router.push(target);
}
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="state.permissionDenied" />
    <ErrorState
      v-else-if="state.error"
      title="Unable to load records"
      :message="state.error.message"
    />
    <div v-else-if="state.entity" class="ref-entity-page">
      <header class="ref-entity-page__header">
        <div>
          <span class="ref-entity-page__eyebrow">LIVE ERPNEXT RECORDS</span>
          <h1>{{ state.entity.title }}</h1>
          <p>{{ state.entity.description }}</p>
        </div>
        <button
          v-if="canCreate(state.permissions)"
          class="ref-button ref-button--primary"
          type="button"
          disabled
          title="Create forms will be implemented in a later approved stage"
        >
          + Create {{ state.entity.title.replace(/s$/, "") }}
        </button>
      </header>

      <FilterBar
        :entity="state.entity"
        :loading="state.loading"
        :filters="state.filters"
        :request="state.request"
        @search="updateSearch"
        @filter="state.setFilter"
        @refresh="state.load"
        @clear="state.clearFilters"
        @page-size="(size) => state.updateQuery({ page_size: size })"
      />

      <div class="ref-list-summary">
        <span><b>{{ state.pagination.total }}</b> records</span>
        <span v-if="state.loading" role="status">Refreshing…</span>
      </div>

      <div v-if="state.loading && !state.records.length" class="ref-list-skeleton" role="status" aria-label="Loading records">
        <span v-for="index in 7" :key="index"></span>
      </div>
      <div v-else-if="!state.records.length" class="ref-empty-state">
        <span aria-hidden="true">⌕</span><h2>No records found</h2><p>Try changing your search or filters.</p>
        <button type="button" @click="state.clearFilters">Clear filters</button>
      </div>
      <template v-else>
        <div :class="['ref-record-results', { 'is-loading': state.loading }]">
          <DataTable
            :entity="state.entity"
            :records="state.records"
            :sort-field="currentSort"
            :sort-order="currentOrder"
            @row="openRecord"
            @sort="changeSort"
          />
          <div class="ref-mobile-record-list">
            <MobileRecordCard
              v-for="record in state.records"
              :key="record.name"
              :entity="state.entity"
              :record="record"
              @open="openRecord(record)"
            />
          </div>
        </div>
        <Pagination
          :pagination="state.pagination"
          @page="(page) => state.updateQuery({ page }, false)"
        />
      </template>
    </div>

    <div v-else class="ref-list-skeleton ref-list-skeleton--page" role="status" aria-label="Loading list">
      <span v-for="index in 9" :key="index"></span>
    </div>
  </PageContainer>
</template>
