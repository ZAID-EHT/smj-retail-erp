<script setup>
import { computed, nextTick, onBeforeUnmount, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { SmjClose } from "@/components/icons";
import { getQuickCreateActions } from "@/services/quickCreate.js";

const router = useRouter();
const open = ref(false);
const loading = ref(false);
const error = ref("");
const groups = ref([]);
const search = ref("");
const activeIndex = ref(-1);
const triggerRef = ref(null);
const searchRef = ref(null);
const dropdownStyle = reactive({ top: "0px", left: "0px", right: "auto" });
let loaded = false;

const filteredGroups = computed(() => {
  const query = search.value.trim().toLowerCase();
  if (!query) return groups.value;
  return groups.value
    .map((group) => ({
      ...group,
      items: group.items.filter(
        (item) => `${item.label} ${item.doctype} ${item.group}`.toLowerCase().includes(query),
      ),
    }))
    .filter((group) => group.items.length);
});

// Flat list of the currently visible items, for arrow-key navigation.
const flatItems = computed(() => filteredGroups.value.flatMap((group) => group.items));

async function loadActions() {
  if (loaded) return;
  loading.value = true;
  error.value = "";
  try {
    groups.value = await getQuickCreateActions();
    loaded = true;
  } catch (caught) {
    error.value = caught.message || "Unable to load create actions.";
  } finally {
    loading.value = false;
  }
}

function position() {
  const rect = triggerRef.value?.getBoundingClientRect();
  if (!rect) return;
  const width = Math.min(520, window.innerWidth - 24);
  const overflowsRight = rect.left + width > window.innerWidth - 12;
  dropdownStyle.top = `${rect.bottom + 8}px`;
  if (overflowsRight) {
    dropdownStyle.left = "auto";
    dropdownStyle.right = `${Math.max(12, window.innerWidth - rect.right)}px`;
  } else {
    dropdownStyle.left = `${rect.left}px`;
    dropdownStyle.right = "auto";
  }
}

async function toggle() {
  if (open.value) {
    close();
    return;
  }
  open.value = true;
  activeIndex.value = -1;
  search.value = "";
  await loadActions();
  position();
  await nextTick();
  searchRef.value?.focus();
}

function close() {
  if (!open.value) return;
  open.value = false;
  triggerRef.value?.focus();
}

function navigate(item) {
  close();
  router.push(item.path);
}

function onKeydown(event) {
  if (!open.value) return;
  if (event.key === "Escape") {
    event.preventDefault();
    close();
  } else if (event.key === "ArrowDown") {
    event.preventDefault();
    activeIndex.value = Math.min(activeIndex.value + 1, flatItems.value.length - 1);
    scrollActiveIntoView();
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    activeIndex.value = Math.max(activeIndex.value - 1, 0);
    scrollActiveIntoView();
  } else if (event.key === "Enter" && activeIndex.value >= 0) {
    event.preventDefault();
    const item = flatItems.value[activeIndex.value];
    if (item) navigate(item);
  }
}

function scrollActiveIntoView() {
  nextTick(() => {
    document.querySelector(".smj-quick-create__item.is-active")?.scrollIntoView({ block: "nearest" });
  });
}

function onDocumentClick(event) {
  if (!open.value) return;
  if (triggerRef.value?.contains(event.target)) return;
  if (event.target.closest?.(".smj-quick-create__panel")) return;
  open.value = false;
}

function onWindowChange() {
  if (open.value) position();
}

window.addEventListener("keydown", onKeydown);
window.addEventListener("click", onDocumentClick);
window.addEventListener("resize", onWindowChange);
window.addEventListener("scroll", onWindowChange, true);
onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeydown);
  window.removeEventListener("click", onDocumentClick);
  window.removeEventListener("resize", onWindowChange);
  window.removeEventListener("scroll", onWindowChange, true);
});
</script>

<template>
  <div class="smj-quick-create">
    <button
      ref="triggerRef"
      class="smj-quick-create__trigger"
      type="button"
      :aria-expanded="open"
      aria-haspopup="menu"
      @click="toggle"
    >
      <span aria-hidden="true" class="smj-quick-create__plus">+</span>
      <span class="smj-quick-create__label">Create</span>
    </button>

    <Teleport to="body">
      <div
        v-if="open"
        class="smj-quick-create__panel"
        role="menu"
        aria-label="Create a new record"
        :style="dropdownStyle"
      >
        <header class="smj-quick-create__panel-header">
          <strong>Create</strong>
          <button class="ref-icon-button" type="button" aria-label="Close create menu" @click="close">
            <SmjClose size="16" decorative />
          </button>
        </header>
        <div class="smj-quick-create__search">
          <input
            ref="searchRef"
            v-model="search"
            type="search"
            placeholder="Search actions…"
            aria-label="Search create actions"
            autocomplete="off"
          />
        </div>
        <p v-if="loading" class="smj-quick-create__status">Loading…</p>
        <p v-else-if="error" class="smj-quick-create__status is-error" role="alert">{{ error }}</p>
        <p v-else-if="!flatItems.length" class="smj-quick-create__status">
          {{ search ? "No matching actions." : "You do not have permission to create records." }}
        </p>
        <div v-else class="smj-quick-create__groups">
          <section v-for="group in filteredGroups" :key="group.group">
            <h4>{{ group.group }}</h4>
            <button
              v-for="item in group.items"
              :key="item.path"
              type="button"
              role="menuitem"
              class="smj-quick-create__item"
              :class="{ 'is-active': flatItems[activeIndex]?.path === item.path }"
              @click="navigate(item)"
            >
              <span class="smj-quick-create__item-plus" aria-hidden="true">+</span>
              <span>{{ item.label }}</span>
            </button>
          </section>
        </div>
      </div>
    </Teleport>
  </div>
</template>
