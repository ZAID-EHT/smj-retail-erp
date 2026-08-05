<script setup>
/* Dropdown Options: the page the "Add / delete" button beside a dropdown opens in
   a new tab. ?type= selects which list is being edited, so the button lands the
   admin on exactly the list they clicked from. */
import { computed, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  addOption, deleteOption, listAllOptions, renameOption, setOptionActive,
} from "@/services/retailOptions.js";

const route = useRoute();

const types = ref([]);
const optionsByType = ref({});
const usage = ref({});
const canManage = ref(false);
const activeType = ref("");
const newValue = ref("");
const search = ref("");
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, saving: false });
// The option being renamed inline, with its own copy of the value so a cancelled
// edit leaves the list untouched.
const editing = reactive({ name: "", value: "" });

const rows = computed(() => {
  const all = optionsByType.value[activeType.value] || [];
  const text = search.value.trim().toLowerCase();
  if (!text) return all;
  return all.filter((row) => row.option_value.toLowerCase().includes(text));
});

async function load() {
  error.value = null;
  try {
    const result = await listAllOptions();
    types.value = result?.types || [];
    optionsByType.value = result?.options || {};
    usage.value = result?.usage || {};
    canManage.value = Boolean(result?.can_manage);
    // ?type= from the form's button wins; otherwise stay where the user was, or
    // start on the first list.
    const requested = String(route.query.type || "");
    if (requested && types.value.includes(requested)) activeType.value = requested;
    else if (!activeType.value || !types.value.includes(activeType.value)) {
      activeType.value = types.value[0] || "";
    }
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.init = false;
  }
}

async function create() {
  const value = newValue.value.trim();
  if (!value) return;
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    await addOption(activeType.value, value);
    notice.value = `Added ${value} to ${activeType.value}.`;
    newValue.value = "";
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

function startEdit(row) {
  editing.name = row.name;
  editing.value = row.option_value;
}

function cancelEdit() {
  editing.name = "";
}

async function applyEdit(row) {
  const value = editing.value.trim();
  if (!value || value === row.option_value) { editing.name = ""; return; }
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const result = await renameOption(row.name, value);
    // Renaming moves the records that carried the old value onto the new one; how
    // many is worth saying, because it is the part that is not visible on screen.
    notice.value = result?.updated
      ? `Renamed ${row.option_value} to ${value}, and updated ${result.updated} record(s) using it.`
      : `Renamed ${row.option_value} to ${value}.`;
    editing.name = "";
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

async function toggle(row) {
  loading.saving = true;
  error.value = null;
  try {
    await setOptionActive(row.name, !row.is_active);
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

async function remove(row) {
  // Deletion is refused when records already carry the value; deactivating is the
  // way out, and the confirmation says so rather than letting the error explain it.
  if (!window.confirm(`Delete "${row.option_value}"? If records already use it, deactivate it instead.`)) return;
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    await deleteOption(row.name);
    notice.value = `Deleted ${row.option_value}.`;
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

watch(() => route.query.type, () => load());
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page ola-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/admin">Administration</RouterLink><span>›</span><strong>Dropdown Options</strong></nav>
      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Form options</span>
          <h1>Dropdown Options</h1>
          <p>The choices the Customer and Product forms offer. Adding one here makes it selectable immediately; deactivating hides it from new records without disturbing the ones that already use it.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Could not complete that" :message="error.message" @retry="load" />
      <p v-if="notice" class="ola-notice" role="status">{{ notice }}</p>
      <div v-if="loading.init" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>

      <template v-else>
        <p v-if="!canManage" class="ola-hint">You can view these options but only an administrator can change them.</p>

        <nav class="ola-tabs" aria-label="Option type">
          <button
            v-for="type in types"
            :key="type"
            type="button"
            class="ola-tab"
            :class="{ 'ola-tab--active': type === activeType }"
            @click="activeType = type"
          >
            {{ type }}
            <em>{{ (optionsByType[type] || []).length }}</em>
          </button>
        </nav>

        <section class="rug-section-card">
          <header>
            <div>
              <h2>{{ activeType }}</h2>
              <p v-if="usage[activeType]">Used by the {{ usage[activeType] }} form.</p>
            </div>
          </header>

          <form v-if="canManage" class="ola-inline-form" @submit.prevent="create">
            <input v-model="newValue" type="text" :placeholder="`New ${activeType.toLowerCase()}…`" />
            <button type="submit" class="rug-primary" :disabled="loading.saving || !newValue.trim()">
              {{ loading.saving ? "Saving…" : "Add" }}
            </button>
          </form>

          <div class="ola-filters">
            <input v-model="search" type="search" :placeholder="`Search ${activeType.toLowerCase()}…`" />
          </div>

          <p v-if="!rows.length" class="ola-hint">Nothing to show here yet.</p>

          <ul v-else class="ola-list">
            <li v-for="row in rows" :key="row.name" :class="{ 'ola-row--inactive': !row.is_active }">
              <template v-if="editing.name === row.name">
                <input v-model="editing.value" class="ola-edit" type="text" @keyup.enter="applyEdit(row)" />
                <span class="ola-row-actions">
                  <button type="button" class="rug-primary" :disabled="loading.saving" @click="applyEdit(row)">Save</button>
                  <button type="button" class="rug-button rug-button--secondary" @click="cancelEdit">Cancel</button>
                </span>
              </template>
              <template v-else>
                <span class="ola-value">{{ row.option_value }}<em v-if="!row.is_active"> (inactive)</em></span>
                <span v-if="canManage" class="ola-row-actions">
                  <button type="button" class="rug-button rug-button--secondary" @click="startEdit(row)">Edit</button>
                  <button type="button" class="rug-button rug-button--secondary" :disabled="loading.saving" @click="toggle(row)">
                    {{ row.is_active ? "Deactivate" : "Activate" }}
                  </button>
                  <button type="button" class="rug-button rug-button--secondary ola-danger" :disabled="loading.saving" @click="remove(row)">Delete</button>
                </span>
              </template>
            </li>
          </ul>
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.ola-page :is(input){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.ola-tabs{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}
.ola-tab{display:inline-flex;align-items:center;gap:.4rem;border:1px solid var(--ref-border-colour);border-radius:999px;background:var(--ref-card-background);color:var(--ref-primary-text);font-weight:700;padding:.4rem .9rem;cursor:pointer}
.ola-tab em{font-style:normal;font-weight:500;color:var(--ref-secondary-text)}
.ola-tab--active{border-color:var(--ref-accent, var(--ref-primary-text));box-shadow:inset 0 0 0 1px var(--ref-accent, transparent)}
.ola-inline-form{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin-bottom:1rem}
.ola-inline-form input{flex:1 1 16rem}
.ola-filters{margin-bottom:1rem}
.ola-filters input{width:100%}
.ola-list{list-style:none;margin:0;padding:0;display:grid;gap:.4rem}
.ola-list li{display:flex;align-items:center;justify-content:space-between;gap:.75rem;flex-wrap:wrap;padding:.55rem .75rem;border:1px solid var(--ref-border-colour);border-radius:.6rem}
.ola-value{font-weight:600}
.ola-value em{font-style:normal;font-weight:500;color:var(--ref-secondary-text)}
.ola-edit{flex:1 1 14rem;min-height:36px}
.ola-row--inactive{opacity:.55}
.ola-row-actions{display:flex;gap:.35rem;flex-wrap:wrap}
.ola-danger{color:var(--ref-danger)}
.ola-notice{padding:.6rem 1rem;border-radius:.6rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
.ola-hint{color:var(--ref-secondary-text)}
</style>
