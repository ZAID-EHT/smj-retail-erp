<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  compareRoleProfiles,
  getEmailConfigurationStatus,
  getRestrictionOptions,
  getRoleOverview,
  getRolePermissionSummary,
  getRoleProfileChangeImpact,
  getRoleProfileOverview,
  getUserAccessOverview,
  revokeUserSessions,
  searchUsers,
  setUserRestrictions,
} from "@/services/accessManagement.js";

const TABS = [
  { key: "access", label: "Effective Access" },
  { key: "restrictions", label: "User Permissions" },
  { key: "roles", label: "Roles" },
  { key: "profiles", label: "Role Profiles" },
  { key: "email", label: "Email Delivery" },
];

const route = useRoute();
const router = useRouter();

const tab = ref(TABS.some((item) => item.key === route.params.tab) ? route.params.tab : "access");
const filters = reactive({ search: "", status: "", role: "", role_profile: "", user_type: "", never_logged_in: 0 });
const users = ref([]);
const selectedUser = ref(route.query.user || "");
const overview = ref(null);
const roles = ref(null);
const roleSummary = ref(null);
const profiles = ref(null);
const comparison = ref(null);
const impact = ref(null);
const email = ref(null);
const compare = reactive({ first: "", second: "" });
const restriction = reactive({ doctype: "Company", options: [], selected: [], search: "" });

const loading = reactive({ users: false, overview: false, roles: false, profiles: false, email: false, saving: false });
const error = ref(null);
const notice = ref(null);
let controller;
let searchTimer;

const selectedUserRow = computed(() => users.value.find((row) => row.name === selectedUser.value) || null);
const deniedCount = computed(
  () => (overview.value?.permissions || []).filter((row) => !row.read).length,
);
const restrictedDoctypes = computed(
  () => (overview.value?.restrictions || []).filter((row) => row.restricted),
);

function fail(caught) {
  if (caught?.name === "AbortError") return;
  error.value = caught;
}

async function loadUsers() {
  loading.users = true;
  try {
    const result = await searchUsers({ ...filters });
    users.value = result?.users || [];
    if (selectedUser.value && !users.value.some((row) => row.name === selectedUser.value)) {
      // Keep an explicitly selected user visible even when filters exclude them.
      users.value = [...users.value];
    }
  } catch (caught) {
    users.value = [];
    fail(caught);
  } finally {
    loading.users = false;
  }
}

async function loadOverview(user) {
  if (!user) {
    overview.value = null;
    return;
  }
  controller?.abort();
  controller = new AbortController();
  loading.overview = true;
  error.value = null;
  try {
    overview.value = await getUserAccessOverview(user, controller.signal);
    restriction.selected = (overview.value.restrictions || []).find((row) => row.doctype === restriction.doctype)?.values || [];
  } catch (caught) {
    overview.value = null;
    fail(caught);
  } finally {
    loading.overview = false;
  }
}

async function loadRoles() {
  loading.roles = true;
  try {
    roles.value = await getRoleOverview();
  } catch (caught) {
    fail(caught);
  } finally {
    loading.roles = false;
  }
}

async function loadProfiles() {
  loading.profiles = true;
  try {
    profiles.value = await getRoleProfileOverview();
  } catch (caught) {
    fail(caught);
  } finally {
    loading.profiles = false;
  }
}

async function loadEmail() {
  loading.email = true;
  try {
    email.value = await getEmailConfigurationStatus();
  } catch (caught) {
    fail(caught);
  } finally {
    loading.email = false;
  }
}

async function loadRestrictionOptions() {
  try {
    const result = await getRestrictionOptions(restriction.doctype, restriction.search);
    restriction.options = result?.options || [];
  } catch (caught) {
    restriction.options = [];
    fail(caught);
  }
}

function selectUser(user) {
  selectedUser.value = user;
  router.replace({ query: { ...route.query, user } }).catch(() => {});
  loadOverview(user);
}

function toggleRestrictionValue(value) {
  const index = restriction.selected.indexOf(value);
  if (index === -1) restriction.selected.push(value);
  else restriction.selected.splice(index, 1);
}

async function saveRestrictions() {
  if (!selectedUser.value) return;
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const result = await setUserRestrictions(selectedUser.value, restriction.doctype, restriction.selected);
    // Sync from the server response so the UI never shows an unsaved state.
    overview.value = { ...overview.value, restrictions: result.restrictions };
    restriction.selected = result.values || [];
    notice.value = `${restriction.doctype} restrictions saved for ${selectedUser.value}.`;
  } catch (caught) {
    fail(caught);
  } finally {
    loading.saving = false;
  }
}

async function revokeSessions() {
  if (!selectedUser.value) return;
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const result = await revokeUserSessions(selectedUser.value);
    notice.value = `Signed ${selectedUser.value} out of ${result.revoked_sessions} session(s).`;
    await loadOverview(selectedUser.value);
  } catch (caught) {
    fail(caught);
  } finally {
    loading.saving = false;
  }
}

async function showRoleSummary(role) {
  try {
    roleSummary.value = await getRolePermissionSummary(role);
  } catch (caught) {
    fail(caught);
  }
}

async function runComparison() {
  if (!compare.first || !compare.second) return;
  try {
    comparison.value = await compareRoleProfiles(compare.first, compare.second);
  } catch (caught) {
    fail(caught);
  }
}

async function showImpact(profile) {
  try {
    impact.value = await getRoleProfileChangeImpact(profile);
  } catch (caught) {
    fail(caught);
  }
}

function selectTab(key) {
  tab.value = key;
  router.replace({ params: { ...route.params, tab: key }, query: route.query }).catch(() => {});
}

function scheduleUserSearch() {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(loadUsers, 200);
}

watch(() => restriction.doctype, () => {
  restriction.selected = (overview.value?.restrictions || []).find((row) => row.doctype === restriction.doctype)?.values || [];
  loadRestrictionOptions();
});

watch(tab, (value) => {
  if (value === "roles" && !roles.value) loadRoles();
  if (value === "profiles" && !profiles.value) loadProfiles();
  if (value === "email" && !email.value) loadEmail();
  if (value === "restrictions" && !restriction.options.length) loadRestrictionOptions();
});

onBeforeUnmount(() => {
  controller?.abort();
  window.clearTimeout(searchTimer);
});

loadUsers();
if (selectedUser.value) loadOverview(selectedUser.value);
if (tab.value === "roles") loadRoles();
if (tab.value === "profiles") loadProfiles();
if (tab.value === "email") loadEmail();
if (tab.value === "restrictions") loadRestrictionOptions();
</script>

<template>
  <PageContainer>
    <main class="rug-page access-control-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Admin</RouterLink><span>›</span><strong>Access Control</strong>
      </nav>

      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Backend-evaluated permissions</span>
          <h1>Access Control</h1>
          <p>
            Effective access, restrictions, roles and delivery status. Every result is evaluated on the
            server for the selected user — nothing here is inferred in the browser.
          </p>
        </div>
        <div class="rug-banner-actions">
          <RouterLink class="rug-primary" to="/admin/users">Manage Users</RouterLink>
        </div>
      </header>

      <nav class="ac-tabs" role="tablist" aria-label="Access control sections">
        <button
          v-for="item in TABS"
          :key="item.key"
          type="button"
          role="tab"
          :aria-selected="tab === item.key"
          :class="{ 'is-active': tab === item.key }"
          @click="selectTab(item.key)"
        >{{ item.label }}</button>
      </nav>

      <ErrorState
        v-if="error"
        title="Unable to load access data"
        :message="error.message"
        @retry="loadOverview(selectedUser)"
      />
      <p v-if="notice" class="ac-notice" role="status">{{ notice }}</p>

      <!-- ------------------------------------------------ users + effective access -->
      <section v-show="tab === 'access' || tab === 'restrictions'" class="rug-section-card">
        <header>
          <div>
            <h2>Select a user</h2>
            <p>Permission-filtered directory. You only see accounts you are entitled to administer.</p>
          </div>
        </header>
        <div class="rug-form-grid">
          <label>
            <span>Search</span>
            <input v-model="filters.search" type="search" autocomplete="off" placeholder="Name or email" @input="scheduleUserSearch" />
          </label>
          <label>
            <span>Status</span>
            <select v-model="filters.status" @change="loadUsers">
              <option value="">All</option><option value="enabled">Enabled</option><option value="disabled">Disabled</option>
            </select>
          </label>
          <label>
            <span>User type</span>
            <select v-model="filters.user_type" @change="loadUsers">
              <option value="">All</option><option value="System User">System User</option><option value="Website User">Website User</option>
            </select>
          </label>
          <label>
            <span>Role</span>
            <input v-model="filters.role" type="search" autocomplete="off" placeholder="e.g. Sales User" @input="scheduleUserSearch" />
          </label>
          <label>
            <span>Role Profile</span>
            <input v-model="filters.role_profile" type="search" autocomplete="off" @input="scheduleUserSearch" />
          </label>
          <label class="ac-check">
            <input v-model="filters.never_logged_in" type="checkbox" :true-value="1" :false-value="0" @change="loadUsers" />
            <span>Never logged in</span>
          </label>
        </div>

        <div v-if="loading.users" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>
        <div v-else-if="!users.length" class="ru-empty">No users match these filters.</div>
        <div v-else class="rug-table-wrap">
          <table>
            <thead>
              <tr><th>Full name</th><th>Email</th><th>Status</th><th>Type</th><th>Role Profile</th><th>Roles</th><th>Last login</th><th></th></tr>
            </thead>
            <tbody>
              <tr v-for="row in users" :key="row.name" :class="{ 'is-selected': row.name === selectedUser }">
                <td>{{ row.full_name || "—" }}</td>
                <td>{{ row.name }}</td>
                <td><span class="ac-pill" :class="row.enabled ? 'is-good' : 'is-bad'">{{ row.enabled ? "Enabled" : "Disabled" }}</span></td>
                <td>{{ row.user_type || "—" }}</td>
                <td>{{ row.role_profile_name || "—" }}</td>
                <td>{{ row.effective_role_count }}</td>
                <td>{{ row.last_login || "Never" }}</td>
                <td><button type="button" class="ac-link" @click="selectUser(row.name)">View access</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <template v-if="tab === 'access'">
        <div v-if="loading.overview" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>
        <section v-else-if="overview" class="rug-section-card">
          <header>
            <div>
              <h2>{{ overview.full_name || overview.user }}</h2>
              <p>{{ overview.user }} — evaluated server-side with <code>frappe.has_permission</code> for this user.</p>
            </div>
            <div class="rug-banner-actions">
              <button
                type="button"
                class="rug-primary"
                :disabled="loading.saving || overview.account.protected"
                :title="overview.account.protected ? 'Protected system account' : ''"
                @click="revokeSessions"
              >Revoke sessions ({{ overview.account.active_sessions }})</button>
            </div>
          </header>

          <dl class="ac-facts">
            <div><dt>Status</dt><dd><span class="ac-pill" :class="overview.account.enabled ? 'is-good' : 'is-bad'">{{ overview.account.status }}</span></dd></div>
            <div><dt>User type</dt><dd>{{ overview.account.user_type || "—" }}</dd></div>
            <div><dt>Role Profile</dt><dd>{{ overview.role_profile || "—" }}</dd></div>
            <div><dt>Last login</dt><dd>{{ overview.account.last_login || "Never" }}</dd></div>
            <div><dt>Active sessions</dt><dd>{{ overview.account.active_sessions }}</dd></div>
            <div><dt>Protected</dt><dd>{{ overview.account.protected ? "Yes" : "No" }}</dd></div>
          </dl>

          <p v-if="overview.role_profile" class="ac-hint">
            <strong>{{ overview.role_profile }}</strong> is assigned, and a Role Profile is authoritative in
            ERPNext — its roles are re-applied on every save, so direct roles do not apply while it is set.
            Remove the profile first if this user needs a role it does not include.
          </p>

          <h3>Effective roles ({{ overview.effective_roles.length }})</h3>
          <p class="ac-roles">
            <span v-for="role in overview.effective_roles" :key="role" class="ac-tag" :class="{ 'is-risk': (roles?.high_risk_roles || []).includes(role) }">{{ role }}</span>
          </p>

          <h3>Restrictions</h3>
          <p v-if="!restrictedDoctypes.length" class="ru-empty">No User Permission restrictions — this user sees all permitted records.</p>
          <p v-else class="ac-roles">
            <span v-for="row in restrictedDoctypes" :key="row.doctype" class="ac-tag is-restrict">{{ row.doctype }}: {{ row.values.join(", ") }}</span>
          </p>

          <h3>Document permissions <small>({{ deniedCount }} of {{ overview.permissions.length }} not readable)</small></h3>
          <div class="rug-table-wrap">
            <table>
              <thead>
                <tr><th>DocType</th><th>Read</th><th>Create</th><th>Write</th><th>Submit</th><th>Cancel</th><th>Amend</th><th>Print</th><th>Export</th><th>Delete</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in overview.permissions" :key="row.doctype">
                  <td>{{ row.doctype }}</td>
                  <td v-for="key in ['read','create','write','submit','cancel','amend','print','export','delete']" :key="key">
                    <span class="ac-flag" :class="row[key] ? 'is-yes' : 'is-no'" :aria-label="row[key] ? 'Allowed' : 'Denied'">{{ row[key] ? "✓" : "✕" }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
        <p v-else class="ru-empty">Select a user above to see their effective access.</p>
      </template>

      <!-- ------------------------------------------------------------ restrictions -->
      <section v-if="tab === 'restrictions'" class="rug-section-card">
        <header>
          <div>
            <h2>User Permissions</h2>
            <p>Standard <code>User Permission</code> records, so ERPNext's own permission conditions apply everywhere.</p>
          </div>
        </header>
        <p v-if="!selectedUser" class="ru-empty">Select a user above first.</p>
        <template v-else>
          <div class="rug-form-grid">
            <label>
              <span>Restrict by</span>
              <select v-model="restriction.doctype">
                <option v-for="row in overview?.restrictions || []" :key="row.doctype" :value="row.doctype">{{ row.doctype }}</option>
              </select>
            </label>
            <label>
              <span>Find values</span>
              <input v-model="restriction.search" type="search" autocomplete="off" @input="loadRestrictionOptions" />
            </label>
          </div>
          <p class="ac-hint">
            Selecting nothing means <strong>no restriction</strong> — the user sees every {{ restriction.doctype }} they otherwise have access to.
          </p>
          <div v-if="!restriction.options.length" class="ru-empty">No {{ restriction.doctype }} records available to you.</div>
          <ul v-else class="ac-options">
            <li v-for="option in restriction.options" :key="option">
              <label>
                <input type="checkbox" :checked="restriction.selected.includes(option)" @change="toggleRestrictionValue(option)" />
                <span>{{ option }}</span>
              </label>
            </li>
          </ul>
          <footer class="ac-actions">
            <button type="button" class="rug-primary" :disabled="loading.saving" @click="saveRestrictions">
              {{ loading.saving ? "Saving…" : `Save ${restriction.doctype} restrictions` }}
            </button>
          </footer>
        </template>
      </section>

      <!-- ------------------------------------------------------------------- roles -->
      <section v-if="tab === 'roles'" class="rug-section-card">
        <header>
          <div><h2>Roles</h2><p>Real assignment counts, straight from <code>Has Role</code>.</p></div>
          <div class="rug-banner-actions"><RouterLink class="rug-primary" to="/admin/roles">Manage Roles</RouterLink></div>
        </header>
        <div v-if="loading.roles" class="rug-skeleton"><i v-for="n in 5" :key="n" /></div>
        <div v-else-if="roles" class="rug-table-wrap">
          <table>
            <thead><tr><th>Role</th><th>Users</th><th>Role Profiles</th><th>Desk</th><th>Risk</th><th></th></tr></thead>
            <tbody>
              <tr v-for="row in roles.roles" :key="row.role">
                <td>{{ row.role }}</td>
                <td>{{ row.assigned_users }}</td>
                <td>{{ row.role_profiles }}</td>
                <td>{{ row.desk_access ? "Yes" : "No" }}</td>
                <td>
                  <span v-if="row.high_risk" class="ac-pill is-bad">High risk</span>
                  <span v-else-if="row.protected" class="ac-pill">Protected</span>
                  <span v-else>—</span>
                </td>
                <td><button type="button" class="ac-link" @click="showRoleSummary(row.role)">What it grants</button></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="roleSummary" class="ac-detail">
          <h3>{{ roleSummary.role }} <span v-if="roleSummary.high_risk" class="ac-pill is-bad">High risk</span></h3>
          <p>{{ roleSummary.assigned_users }} user(s), {{ roleSummary.role_profiles }} role profile(s).</p>
          <ul>
            <li v-for="row in roleSummary.doctype_permissions" :key="row.doctype">
              <strong>{{ row.doctype }}</strong>: {{ row.granted.join(", ") }}
            </li>
          </ul>
        </div>
      </section>

      <!-- ---------------------------------------------------------- role profiles -->
      <section v-if="tab === 'profiles'" class="rug-section-card">
        <header>
          <div><h2>Role Profiles</h2><p>Bundles of roles, with the users each one currently affects.</p></div>
          <div class="rug-banner-actions"><RouterLink class="rug-primary" to="/admin/role-profiles">Manage Role Profiles</RouterLink></div>
        </header>
        <div v-if="loading.profiles" class="rug-skeleton"><i v-for="n in 4" :key="n" /></div>
        <template v-else-if="profiles">
          <div class="rug-table-wrap">
            <table>
              <thead><tr><th>Role Profile</th><th>Roles</th><th>Assigned users</th><th>High-risk roles</th><th></th></tr></thead>
              <tbody>
                <tr v-for="row in profiles.profiles" :key="row.role_profile">
                  <td>{{ row.role_profile }}</td>
                  <td>{{ row.roles.join(", ") || "—" }}</td>
                  <td>{{ row.assigned_users }}</td>
                  <td>{{ row.high_risk_roles.join(", ") || "—" }}</td>
                  <td><button type="button" class="ac-link" @click="showImpact(row.role_profile)">Change impact</button></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="rug-form-grid">
            <label>
              <span>Compare</span>
              <select v-model="compare.first"><option value="">Select…</option><option v-for="row in profiles.profiles" :key="row.role_profile" :value="row.role_profile">{{ row.role_profile }}</option></select>
            </label>
            <label>
              <span>With</span>
              <select v-model="compare.second"><option value="">Select…</option><option v-for="row in profiles.profiles" :key="row.role_profile" :value="row.role_profile">{{ row.role_profile }}</option></select>
            </label>
            <label class="ac-check">
              <button type="button" class="rug-primary" :disabled="!compare.first || !compare.second" @click="runComparison">Compare</button>
            </label>
          </div>
          <div v-if="comparison" class="ac-detail">
            <h3>{{ comparison.first }} vs {{ comparison.second }}</h3>
            <p><strong>Shared:</strong> {{ comparison.shared.join(", ") || "none" }}</p>
            <p><strong>Only in {{ comparison.first }}:</strong> {{ comparison.only_in_first.join(", ") || "none" }}</p>
            <p><strong>Only in {{ comparison.second }}:</strong> {{ comparison.only_in_second.join(", ") || "none" }}</p>
            <p v-if="comparison.high_risk_difference.length" class="ac-warn">
              High-risk difference: {{ comparison.high_risk_difference.join(", ") }}
            </p>
          </div>
          <div v-if="impact" class="ac-detail">
            <h3>Impact — {{ impact.role_profile }}</h3>
            <p v-if="impact.warning" class="ac-warn">{{ impact.warning }}</p>
            <p>Roles: {{ impact.roles.join(", ") || "none" }}</p>
            <ul><li v-for="user in impact.affected_users" :key="user.name">{{ user.full_name || user.name }} ({{ user.enabled ? "enabled" : "disabled" }})</li></ul>
          </div>
        </template>
      </section>

      <!-- ------------------------------------------------------------------- email -->
      <section v-if="tab === 'email'" class="rug-section-card">
        <header><div><h2>Email Delivery</h2><p>Whether a welcome or reset email can actually be delivered. Credentials are never shown.</p></div></header>
        <div v-if="loading.email" class="rug-skeleton"><i v-for="n in 3" :key="n" /></div>
        <template v-else-if="email">
          <p class="ac-status" :class="email.can_send_welcome_email ? 'is-good' : 'is-bad'">
            {{ email.can_send_welcome_email ? "Email delivery is available." : email.message }}
          </p>
          <dl class="ac-facts">
            <div><dt>Outgoing account configured</dt><dd>{{ email.outgoing_configured ? "Yes" : "No" }}</dd></div>
            <div><dt>Outgoing enabled</dt><dd>{{ email.outgoing_enabled ? "Yes" : "No" }}</dd></div>
            <div><dt>Default outgoing account</dt><dd>{{ email.default_outgoing_account || "None" }}</dd></div>
            <div><dt>Site-config SMTP fallback</dt><dd>{{ email.site_config_fallback ? "Yes" : "No" }}</dd></div>
          </dl>
          <div v-if="email.accounts.length" class="rug-table-wrap">
            <table>
              <thead><tr><th>Account</th><th>Email</th><th>Default outgoing</th><th>Credentials</th></tr></thead>
              <tbody>
                <tr v-for="row in email.accounts" :key="row.name">
                  <td>{{ row.name }}</td><td>{{ row.email_id }}</td>
                  <td>{{ row.default_outgoing ? "Yes" : "No" }}</td>
                  <td><span class="ac-pill" :class="row.awaiting_password ? 'is-bad' : 'is-good'">{{ row.awaiting_password ? "Awaiting password" : "Set" }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="ru-empty">No outgoing Email Account exists on this site.</p>
        </template>
      </section>
    </main>
  </PageContainer>
</template>

<style scoped>
.access-control-page label{display:grid;gap:.4rem;color:var(--ref-primary-text);font-weight:700}
.access-control-page label :is(input[type="search"],input[type="text"],select){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text);width:100%}
.ac-tabs{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}
.ac-tabs button{min-height:44px;padding:0 1rem;border:1px solid var(--ref-border-colour);border-radius:999px;background:var(--ref-card-background);color:var(--ref-primary-text);font-weight:700;cursor:pointer}
.ac-tabs button.is-active{background:var(--ref-accent-purple,#6b46c1);color:#fff;border-color:transparent}
.ac-tabs button:focus-visible,.ac-link:focus-visible{outline:3px solid var(--ref-accent-purple,#6b46c1);outline-offset:2px}
.ac-check{display:flex;align-items:end;gap:.5rem}
.ac-check input{min-height:24px;width:24px}
.ac-notice{padding:.75rem 1rem;border-radius:.75rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
.ac-pill{display:inline-flex;padding:.25rem .6rem;border-radius:999px;background:var(--ref-border-colour);font-weight:800;font-size:.85rem}
.ac-pill.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.ac-pill.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
.ac-tag{display:inline-flex;margin:.2rem;padding:.25rem .6rem;border-radius:999px;background:var(--ref-border-colour);font-weight:700;font-size:.85rem}
.ac-tag.is-risk{background:var(--ref-warning-background);color:var(--ref-danger)}
.ac-tag.is-restrict{background:var(--ref-success-background);color:var(--ref-success)}
.ac-roles{display:flex;flex-wrap:wrap;gap:.15rem}
.ac-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin:1rem 0}
.ac-facts dt{font-size:.85rem;color:var(--ref-secondary-text);font-weight:700}
.ac-facts dd{margin:.25rem 0 0;font-weight:800}
.ac-flag{font-weight:900}
.ac-flag.is-yes{color:var(--ref-success)}
.ac-flag.is-no{color:var(--ref-danger)}
.ac-link{min-height:44px;padding:0 .75rem;border:1px solid var(--ref-border-colour);border-radius:.65rem;background:var(--ref-card-background);color:var(--ref-primary-text);font-weight:700;cursor:pointer}
.ac-options{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.5rem}
.ac-options label{display:flex;align-items:center;gap:.5rem;min-height:44px;padding:0 .6rem;border:1px solid var(--ref-border-colour);border-radius:.65rem}
.ac-options input{width:22px;height:22px}
.ac-actions{display:flex;justify-content:flex-end;padding-top:1rem}
.ac-detail{margin-top:1rem;padding:1rem;border:1px solid var(--ref-border-colour);border-radius:.75rem}
.ac-hint{color:var(--ref-secondary-text)}
.ac-warn{color:var(--ref-danger);font-weight:800}
.ac-status{padding:.75rem 1rem;border-radius:.75rem;font-weight:800}
.ac-status.is-good{background:var(--ref-success-background);color:var(--ref-success)}
.ac-status.is-bad{background:var(--ref-warning-background);color:var(--ref-danger)}
tr.is-selected{background:var(--ref-success-background)}
@media (max-width:640px){.ac-facts{grid-template-columns:1fr 1fr}}
</style>
