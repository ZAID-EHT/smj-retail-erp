import { computed, onBeforeUnmount, reactive, ref, unref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getEntityList } from "@/services/entities.js";

function filtersFromQuery(query) {
  const filters = {};
  Object.entries(query).forEach(([key, value]) => {
    if (!key.startsWith("f_") || value === "") return;
    const filterKey = key.slice(2);
    if (filterKey.endsWith("_from") || filterKey.endsWith("_to")) {
      const boundary = filterKey.endsWith("_from") ? "from" : "to";
      const fieldname = filterKey.slice(0, -(boundary.length + 1));
      filters[fieldname] ||= {};
      filters[fieldname][boundary] = value;
    } else {
      filters[filterKey] = value;
    }
  });
  return filters;
}

export function useEntityList(entityKey) {
  const route = useRoute();
  const router = useRouter();
  const entity = ref(null);
  const permissions = ref({});
  const records = ref([]);
  const pagination = ref({ page: 1, page_size: 20, total: 0, pages: 1 });
  const loading = ref(false);
  const error = ref(null);
  const permissionDenied = ref(false);
  const filters = computed(() => filtersFromQuery(route.query));
  let controller = null;

  const request = computed(() => ({
    entity_key: unref(entityKey),
    search: route.query.q || "",
    filters: filters.value,
    sort_field: route.query.sort || undefined,
    sort_order: route.query.order || undefined,
    page: Number(route.query.page || 1),
    page_size: Number(route.query.page_size || 20),
  }));

  async function load() {
    controller?.abort();
    const activeController = new AbortController();
    controller = activeController;
    loading.value = true;
    error.value = null;
    permissionDenied.value = false;
    if (entity.value?.key !== unref(entityKey)) {
      entity.value = null;
      records.value = [];
    }
    try {
      const response = await getEntityList(request.value, activeController.signal);
      entity.value = response.entity;
      permissions.value = response.permissions;
      records.value = response.records;
      pagination.value = response.pagination;
    } catch (requestError) {
      if (requestError.name === "AbortError") return;
      records.value = [];
      permissionDenied.value = Boolean(requestError.permissionDenied);
      error.value = requestError;
    } finally {
      if (controller === activeController && !activeController.signal.aborted) loading.value = false;
    }
  }

  function updateQuery(patch, resetPage = true) {
    const query = { ...route.query, ...patch };
    Object.keys(query).forEach((key) => {
      if (query[key] === "" || query[key] == null) delete query[key];
    });
    if (resetPage) delete query.page;
    return router.replace({ query });
  }

  function setFilter(fieldname, value, boundary = null) {
    const key = boundary ? `f_${fieldname}_${boundary}` : `f_${fieldname}`;
    return updateQuery({ [key]: value });
  }

  function clearFilters() {
    const query = {};
    ["sort", "order", "page_size"].forEach((key) => {
      if (route.query[key]) query[key] = route.query[key];
    });
    return router.replace({ query });
  }

  watch([() => route.fullPath, () => unref(entityKey)], load, { immediate: true });
  onBeforeUnmount(() => controller?.abort());

  return reactive({
    entity,
    permissions,
    records,
    pagination,
    loading,
    error,
    permissionDenied,
    filters,
    request,
    load,
    updateQuery,
    setFilter,
    clearFilters,
  });
}
