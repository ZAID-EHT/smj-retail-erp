import { computed, onBeforeUnmount, reactive, ref, unref, watch } from "vue";
import { useRoute } from "vue-router";

import { getEntityDetail } from "@/services/entityDetails.js";

export function useEntityDetail(entityKey) {
  const route = useRoute();
  const detail = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const permissionDenied = ref(false);
  const notFound = ref(false);
  let controller = null;

  const recordName = computed(() => String(route.params.name || ""));

  async function load() {
    controller?.abort();
    const activeController = new AbortController();
    controller = activeController;
    loading.value = true;
    error.value = null;
    permissionDenied.value = false;
    notFound.value = false;
    if (detail.value?.entity?.key !== unref(entityKey) || detail.value?.document?.name !== recordName.value) {
      detail.value = null;
    }
    try {
      detail.value = await getEntityDetail(unref(entityKey), recordName.value, activeController.signal);
    } catch (requestError) {
      if (requestError.name === "AbortError") return;
      permissionDenied.value = Boolean(requestError.permissionDenied && !requestError.notFound);
      notFound.value = Boolean(requestError.notFound);
      error.value = requestError;
    } finally {
      if (controller === activeController && !activeController.signal.aborted) loading.value = false;
    }
  }

  watch([() => route.fullPath, () => unref(entityKey)], load, { immediate: true });
  onBeforeUnmount(() => controller?.abort());

  return reactive({ detail, loading, error, permissionDenied, notFound, recordName, load });
}
