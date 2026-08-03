<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import {
  getSalesTeam, listSalesTeams, saveSalesTeam, searchSalesPersons,
} from "@/services/salesTeam.js";
import TeamPerformancePanel from "@/components/sales/TeamPerformancePanel.vue";

const route = useRoute();
const router = useRouter();

/* The list and the form share this page so the "New Sales Team" button never
   depends on a second route resolving. ?team=new or ?team=<name> opens the form. */
const editing = computed(() => route.query.team || "");
const isForm = computed(() => Boolean(editing.value));

const filters = reactive({ search: "", is_active: "", sales_manager: "", page: 1 });
const sort = reactive({ field: "team_name", order: "asc" });
const data = ref(null);
const loading = ref(false);
const error = ref(null);
const denied = ref(false);
let controller = null;

const form = reactive({ team: null, roles: [], companies: [], canManage: false, isNew: true });
const formLoading = ref(false);
const saving = ref(false);
const formError = ref("");
const notice = ref("");
const personOptions = ref([]);

function loadList() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  denied.value = false;
  listSalesTeams({ ...filters, sort_field: sort.field, sort_order: sort.order }, controller.signal)
    .then((result) => { data.value = result; })
    .catch((err) => {
      if (err.name === "AbortError") return;
      if (err.response?.status === 403) denied.value = true;
      else error.value = err;
    })
    .finally(() => { loading.value = false; });
}

function loadForm() {
  formLoading.value = true;
  formError.value = "";
  const name = editing.value === "new" ? "" : editing.value;
  getSalesTeam(name)
    .then((result) => {
      form.team = result.team;
      form.roles = result.roles;
      form.canManage = result.can_manage;
      form.companies = result.companies || [];
      form.isNew = result.is_new;
    })
    .catch((err) => { formError.value = err.message; })
    .finally(() => { formLoading.value = false; });
}

function refresh() { if (isForm.value) loadForm(); else loadList(); }
refresh();
watch(() => route.fullPath, refresh);
onBeforeUnmount(() => controller?.abort());

searchSalesPersons("").then((rows) => { personOptions.value = rows; }).catch(() => {});

/* --- form helpers --- */
const activeTotal = computed(() => {
  const rows = form.team?.members || [];
  const sum = rows.filter((r) => r.is_active)
    .reduce((total, r) => total + (Number(r.share_percentage) || 0), 0);
  return Math.round(sum * 100) / 100;
});
const balanced = computed(() => Math.abs(activeTotal.value - 100) < 0.01);
const duplicatePerson = computed(() => {
  const seen = new Set();
  for (const row of form.team?.members || []) {
    if (!row.sales_person) continue;
    if (seen.has(row.sales_person)) return row.sales_person;
    seen.add(row.sales_person);
  }
  return "";
});
const activeManagers = computed(() =>
  (form.team?.members || []).filter((r) => r.is_active && r.team_role === "Sales Manager").length);

const blockingReason = computed(() => {
  if (!form.team?.team_name?.trim()) return "Enter a team name.";
  if ((form.team?.members || []).some((r) => !r.sales_person)) return "Choose a person for every row.";
  if (duplicatePerson.value) return `${duplicatePerson.value} appears more than once.`;
  if (activeManagers.value === 0) return "The team needs one active Sales Manager.";
  if (activeManagers.value > 1) return "Only one active Sales Manager is allowed.";
  if (!balanced.value) return `Active shares total ${activeTotal.value}%. They must total 100%.`;
  return "";
});

function addMember() {
  form.team.members.push({
    sales_person: "", team_role: "Sales Representative", share_percentage: 0,
    is_active: true, effective_from: form.team.effective_from, effective_to: null,
  });
}
function removeMember(index) { form.team.members.splice(index, 1); }

function save() {
  if (blockingReason.value) return;
  saving.value = true;
  formError.value = "";
  saveSalesTeam(form.team, form.isNew ? "" : form.team.name)
    .then((result) => {
      notice.value = `Saved ${result.team.team_name} (${result.name}).`;
      router.push({ path: "/sales/teams" });
    })
    .catch((err) => { formError.value = err.message; })
    .finally(() => { saving.value = false; });
}

function setSort(field) {
  if (sort.field === field) sort.order = sort.order === "asc" ? "desc" : "asc";
  else { sort.field = field; sort.order = "asc"; }
  loadList();
}
function applyFilters() { filters.page = 1; loadList(); }
function goPage(delta) {
  const next = filters.page + delta;
  if (next < 1 || next > (data.value?.pagination?.pages || 1)) return;
  filters.page = next;
  loadList();
}
</script>

<template>
  <PageContainer>
    <PermissionDenied v-if="denied" />
    <main v-else class="rug-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span>
        <RouterLink to="/sales/teams">Sales Teams</RouterLink>
        <template v-if="isForm"><span>›</span><strong>{{ form.isNew ? "New Team" : editing }}</strong></template>
      </nav>

      <header class="rug-banner rug-banner--green">
        <div>
          <span class="rug-badge">Sales</span>
          <h1>{{ isForm ? (form.isNew ? "New Sales Team" : "Edit Sales Team") : "Sales Teams" }}</h1>
          <p>A sales manager, their representatives, and how the commission is shared.</p>
        </div>
        <div class="rug-banner-actions">
          <RouterLink
            v-if="!isForm && data?.can_manage"
            class="rug-primary priority-button-link"
            active-class=""
            exact-active-class=""
            :to="{ path: '/sales/teams', query: { team: 'new' } }"
          >New Sales Team</RouterLink>
          <button v-if="!isForm" type="button" @click="loadList">Refresh</button>
          <RouterLink v-if="isForm" class="priority-button-link" active-class="" exact-active-class="" :to="{ path: '/sales/teams' }">Back to list</RouterLink>
        </div>
      </header>

      <p v-if="notice" class="smj-sales-notice" role="status">{{ notice }}</p>

      <!-- ------------------------------- LIST ------------------------------- -->
      <template v-if="!isForm">
        <ErrorState v-if="error" title="Unable to load sales teams" :message="error.message" @retry="loadList" />

        <section class="rug-section-card">
          <div class="rug-form-grid">
            <label><span>Search</span>
              <input v-model="filters.search" type="search" placeholder="Team, code or manager" @change="applyFilters" />
            </label>
            <label><span>Status</span>
              <select v-model="filters.is_active" @change="applyFilters">
                <option value="">All</option><option value="1">Active</option><option value="0">Inactive</option>
              </select>
            </label>
            <label><span>Sales Manager</span>
              <select v-model="filters.sales_manager" @change="applyFilters">
                <option value="">All managers</option>
                <option v-for="m in data?.managers || []" :key="m" :value="m">{{ m }}</option>
              </select>
            </label>
          </div>
        </section>

        <div v-if="loading" class="rug-skeleton"><i v-for="n in 5" :key="n" /></div>

        <section v-else-if="!data?.rows?.length" class="rug-section-card">
          <div class="rug-empty">
            <h2>No sales teams yet</h2>
            <p v-if="data?.can_manage">Use “New Sales Team” to create the first one.</p>
            <p v-else>No sales team has been set up.</p>
          </div>
        </section>

        <section v-else class="rug-section-card">
          <div class="rug-table-region">
            <table>
              <thead>
                <tr>
                  <th><button type="button" class="smj-sort" @click="setSort('team_name')">Team</button></th>
                  <th><button type="button" class="smj-sort" @click="setSort('sales_manager')">Sales Manager</button></th>
                  <th>Members</th>
                  <th><button type="button" class="smj-sort" @click="setSort('commission_rate')">Commission</button></th>
                  <th><button type="button" class="smj-sort" @click="setSort('effective_from')">Effective From</button></th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in data.rows" :key="row.name" @click="router.push({ path: '/sales/teams', query: { team: row.name } })">
                  <td data-label="Team"><strong>{{ row.team_name }}</strong><small> {{ row.name }}</small></td>
                  <td data-label="Sales Manager">{{ row.sales_manager || "—" }}</td>
                  <td data-label="Members">{{ row.member_count }}</td>
                  <td data-label="Commission">{{ Number(row.commission_rate || 0) }}%</td>
                  <td data-label="Effective From">{{ row.effective_from || "—" }}</td>
                  <td data-label="Status"><span class="rug-status">{{ row.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <footer class="smj-pager">
            <span>{{ data.pagination.total }} team(s) · page {{ data.pagination.page }} of {{ data.pagination.pages }}</span>
            <span>
              <button type="button" :disabled="data.pagination.page <= 1" @click="goPage(-1)">Previous</button>
              <button type="button" :disabled="data.pagination.page >= data.pagination.pages" @click="goPage(1)">Next</button>
            </span>
          </footer>
        </section>
      </template>

      <!-- ------------------------------- FORM ------------------------------- -->
      <template v-else>
        <div v-if="formLoading" class="rug-skeleton"><i v-for="n in 5" :key="n" /></div>

        <template v-else-if="form.team">
          <p v-if="formError" class="rug-inline-error" role="alert">{{ formError }}</p>
          <p v-if="!form.canManage" class="smj-accounts-note" role="status">
            You can view this team but not change it.
          </p>

          <section class="rug-section-card">
            <header><h2>Team</h2></header>
            <div class="rug-form-grid">
              <label><span>Team Name</span>
                <input v-model="form.team.team_name" type="text" :disabled="!form.canManage" />
              </label>
              <label><span>Team Code</span>
                <input :value="form.team.team_code" type="text" readonly />
              </label>
              <label><span>Team Commission Rate (%)</span>
                <input v-model.number="form.team.commission_rate" type="number" min="0" max="100" step="any" :disabled="!form.canManage" />
              </label>
              <label><span>Restrict to Company</span>
                <select v-model="form.team.company" :disabled="!form.canManage" data-test="team-company">
                  <option value="">Every company</option>
                  <option v-for="option in form.companies || []" :key="option" :value="option">
                    {{ option }}
                  </option>
                </select>
              </label>
              <label><span>Effective From</span>
                <input v-model="form.team.effective_from" type="date" :disabled="!form.canManage" />
              </label>
              <label><span>Effective To</span>
                <input v-model="form.team.effective_to" type="date" :disabled="!form.canManage" />
              </label>
              <label><span>Status</span>
                <select v-model="form.team.is_active" :disabled="!form.canManage">
                  <option :value="true">Active</option><option :value="false">Inactive</option>
                </select>
              </label>
            </div>
          </section>

          <section class="rug-section-card">
            <header>
              <div>
                <h2>Team Members</h2>
                <p>Active shares must total 100%.</p>
              </div>
              <button v-if="form.canManage" type="button" @click="addMember">Add representative</button>
            </header>

            <div class="rug-table-region">
              <table>
                <thead>
                  <tr><th>Person</th><th>Role in Team</th><th>Share %</th><th>Active</th><th v-if="form.canManage"></th></tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in form.team.members" :key="index">
                    <td data-label="Person">
                      <input v-model="row.sales_person" list="smj-sales-persons" type="search" :disabled="!form.canManage" :aria-label="`Person for row ${index + 1}`" />
                    </td>
                    <td data-label="Role">
                      <select v-model="row.team_role" :disabled="!form.canManage" :aria-label="`Role for row ${index + 1}`">
                        <option v-for="r in form.roles" :key="r" :value="r">{{ r }}</option>
                      </select>
                    </td>
                    <td data-label="Share %">
                      <input v-model.number="row.share_percentage" type="number" min="0" max="100" step="any" :disabled="!form.canManage" :aria-label="`Share for row ${index + 1}`" />
                    </td>
                    <td data-label="Active">
                      <input v-model="row.is_active" type="checkbox" :disabled="!form.canManage" :aria-label="`Active for row ${index + 1}`" />
                    </td>
                    <td v-if="form.canManage">
                      <button type="button" :aria-label="`Remove row ${index + 1}`" @click="removeMember(index)">Remove</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <datalist id="smj-sales-persons">
              <option v-for="p in personOptions" :key="p.value" :value="p.value">{{ p.label }}</option>
            </datalist>

            <p class="smj-team-total" :class="balanced ? 'is-ok' : 'is-bad'" role="status">
              Total allocation: <strong>{{ activeTotal }}%</strong>
              <span v-if="!balanced"> — must be 100%</span>
            </p>
            <p v-if="blockingReason" class="rug-inline-error" role="alert">{{ blockingReason }}</p>
          </section>

          <!-- Only for a team that exists; a new one has nothing to report on yet. -->
          <TeamPerformancePanel v-if="!form.isNew && editing !== 'new'" :team="editing" />

          <section class="rug-section-card">
            <header><h2>Notes</h2></header>
            <textarea v-model="form.team.notes" rows="3" :disabled="!form.canManage" aria-label="Notes"></textarea>
          </section>

          <footer class="smj-form-actions">
            <RouterLink class="priority-button-link" active-class="" exact-active-class="" :to="{ path: '/sales/teams' }">Cancel</RouterLink>
            <button
              v-if="form.canManage"
              type="button"
              class="rug-primary"
              :disabled="saving || Boolean(blockingReason)"
              :title="blockingReason"
              @click="save"
            >{{ saving ? "Saving…" : "Save Sales Team" }}</button>
          </footer>
        </template>
      </template>
    </main>
  </PageContainer>
</template>
