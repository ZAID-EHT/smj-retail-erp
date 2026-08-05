<script setup>
/* Sales People: the page the customer form's "Add / edit / delete" button opens in
   a new tab, beside Assigned Sales Person.

   Adding, renaming and removing is a Sales Manager / System Manager action -- the
   same gate as reassigning a customer -- so the actions are rendered only when the
   server says this user may manage them, not merely disabled. Renaming carries the
   customers and documents already naming the person along with it; deleting is
   refused while anything still points at them, and disabling is the way out. */
import { computed, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  addSalesPerson, deleteSalesPerson, listSalesPersons, renameSalesPerson,
  setSalesPersonEnabled,
} from "@/services/salesTeam.js";

const people = ref([]);
const canManage = ref(false);
const newName = ref("");
const search = ref("");
const showDisabled = ref(false);
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, saving: false });
// The person being renamed inline, with their own copy of the name so a cancelled
// edit leaves the list untouched.
const editing = reactive({ name: "", value: "" });

const rows = computed(() => {
  const text = search.value.trim().toLowerCase();
  if (!text) return people.value;
  return people.value.filter((person) => person.sales_person_name.toLowerCase().includes(text));
});

async function load() {
  error.value = null;
  try {
    const result = await listSalesPersons({ includeDisabled: showDisabled.value });
    people.value = result?.sales_persons || [];
    canManage.value = Boolean(result?.can_manage);
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.init = false;
  }
}

async function run(action, message) {
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    await action();
    notice.value = message;
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

function create() {
  const value = newName.value.trim();
  if (!value) return;
  run(async () => { await addSalesPerson(value); newName.value = ""; }, `Added ${value}.`);
}

function startEdit(person) {
  editing.name = person.name;
  editing.value = person.sales_person_name;
}

function cancelEdit() {
  editing.name = "";
}

function applyEdit() {
  const value = editing.value.trim();
  const previous = editing.name;
  if (!value || value === previous) { editing.name = ""; return; }
  run(async () => { await renameSalesPerson(previous, value); editing.name = ""; },
    `Renamed ${previous} to ${value}.`);
}

function toggle(person) {
  run(() => setSalesPersonEnabled(person.name, !person.enabled),
    `${person.enabled ? "Disabled" : "Enabled"} ${person.sales_person_name}.`);
}

function remove(person) {
  // Deletion is refused while customers or documents still name the person;
  // saying so here means the refusal is not a surprise.
  if (!window.confirm(
    `Delete ${person.sales_person_name}? If customers or documents still name them, disable them instead.`,
  )) return;
  run(() => deleteSalesPerson(person.name), `Deleted ${person.sales_person_name}.`);
}

load();
</script>

<template>
  <PageContainer>
    <main class="rug-page spa-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/admin">Administration</RouterLink><span>›</span><strong>Sales People</strong></nav>
      <header class="rug-banner rug-banner--green">
        <div>
          <span class="rug-badge">Sales roster</span>
          <h1>Sales People</h1>
          <p>The people the Customer form can assign. Adding one here makes them selectable immediately; disabling hides them from new assignments without disturbing the customers and documents that already name them.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Could not complete that" :message="error.message" @retry="load" />
      <p v-if="notice" class="spa-notice" role="status">{{ notice }}</p>
      <div v-if="loading.init" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>

      <template v-else>
        <p v-if="!canManage" class="spa-hint">You can view this roster but only a Sales Manager or System Manager can change it.</p>

        <section class="rug-section-card">
          <header>
            <div>
              <h2>Sales people</h2>
              <p>Assigned on the Customer form. The commission split still follows the customer's sales manager and their team.</p>
            </div>
          </header>

          <form v-if="canManage" class="spa-inline-form" @submit.prevent="create">
            <input v-model="newName" type="text" placeholder="New sales person…" />
            <button type="submit" class="rug-primary" :disabled="loading.saving || !newName.trim()">
              {{ loading.saving ? "Saving…" : "Add" }}
            </button>
          </form>

          <div class="spa-filters">
            <input v-model="search" type="search" placeholder="Search sales people…" />
            <label class="spa-check"><input v-model="showDisabled" type="checkbox" @change="load" /> Show disabled</label>
          </div>

          <p v-if="!rows.length" class="spa-hint">Nothing to show here yet.</p>

          <ul v-else class="spa-list">
            <li v-for="person in rows" :key="person.name" :class="{ 'spa-row--off': !person.enabled }">
              <template v-if="editing.name === person.name">
                <input v-model="editing.value" class="spa-edit" type="text" @keyup.enter="applyEdit" />
                <span class="spa-row-actions">
                  <button type="button" class="rug-primary" :disabled="loading.saving" @click="applyEdit">Save</button>
                  <button type="button" class="rug-button rug-button--secondary" @click="cancelEdit">Cancel</button>
                </span>
              </template>
              <template v-else>
                <span class="spa-value">{{ person.sales_person_name }}<em v-if="!person.enabled"> (disabled)</em></span>
                <span v-if="canManage" class="spa-row-actions">
                  <button type="button" class="rug-button rug-button--secondary" @click="startEdit(person)">Edit</button>
                  <button type="button" class="rug-button rug-button--secondary" :disabled="loading.saving" @click="toggle(person)">
                    {{ person.enabled ? "Disable" : "Enable" }}
                  </button>
                  <button type="button" class="rug-button rug-button--secondary spa-danger" :disabled="loading.saving" @click="remove(person)">Delete</button>
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
.spa-page :is(input){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.spa-inline-form{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin-bottom:1rem}
.spa-inline-form input{flex:1 1 16rem}
.spa-filters{display:flex;gap:1rem;align-items:center;flex-wrap:wrap;margin-bottom:1rem}
.spa-filters input[type=search]{flex:1 1 18rem}
.spa-check{display:inline-flex;align-items:center;gap:.4rem;font-weight:500}
.spa-check input{min-height:20px;width:18px}
.spa-list{list-style:none;margin:0;padding:0;display:grid;gap:.4rem}
.spa-list li{display:flex;align-items:center;justify-content:space-between;gap:.75rem;flex-wrap:wrap;padding:.55rem .75rem;border:1px solid var(--ref-border-colour);border-radius:.6rem}
.spa-value{font-weight:600}
.spa-value em{font-style:normal;font-weight:500;color:var(--ref-secondary-text)}
.spa-edit{flex:1 1 14rem;min-height:36px}
.spa-row--off{opacity:.55}
.spa-row-actions{display:flex;gap:.35rem;flex-wrap:wrap}
.spa-danger{color:var(--ref-danger)}
.spa-notice{padding:.6rem 1rem;border-radius:.6rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
.spa-hint{color:var(--ref-secondary-text)}
</style>
