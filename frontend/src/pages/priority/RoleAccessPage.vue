<script setup>
/* Role Access: name a role, tick the pages it may see.
   Ticking is not cosmetic -- saving also grants the role read on the DocTypes
   behind the ticked pages and removes it from the ones no longer ticked, so a
   brand-new role works immediately instead of showing empty screens. */
import { computed, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  clearRolePageAccess, createRole, getPageCatalogue, getRolePageAccess,
  listManageableRoles, saveRolePageAccess,
} from "@/services/rolePages.js";

const sections = ref([]);
const roles = ref([]);
const protectedRoles = ref([]);
const activeRole = ref("");
const selected = ref(new Set());
const readable = ref(new Set());
const configured = ref(false);
const newRoleName = ref("");
const expanded = reactive({});
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, role: false, saving: false });

const dirtyBaseline = ref("");
const isDirty = computed(() => signature() !== dirtyBaseline.value);
const totalPages = computed(() =>
  sections.value.reduce((sum, s) => sum + 1 + s.links.length, 0));

function signature() {
  return [...selected.value].sort().join("|");
}

async function load() {
  loading.init = true;
  error.value = null;
  try {
    const [catalogue, roleList] = await Promise.all([getPageCatalogue(), listManageableRoles()]);
    sections.value = catalogue.sections;
    roles.value = roleList.roles;
    protectedRoles.value = roleList.protected;
    for (const section of sections.value) expanded[section.name] = false;
  } catch (err) {
    error.value = err;
  } finally {
    loading.init = false;
  }
}

async function pickRole(role) {
  activeRole.value = role;
  selected.value = new Set();
  readable.value = new Set();
  notice.value = null;
  if (!role) return;
  loading.role = true;
  try {
    const access = await getRolePageAccess(role);
    selected.value = new Set(access.paths);
    readable.value = new Set(access.readable_doctypes);
    configured.value = access.configured;
    dirtyBaseline.value = signature();
    // Open the sections that already have something ticked, so the current
    // selection is visible without hunting for it.
    for (const section of sections.value) {
      expanded[section.name] = section.links.some((l) => selected.value.has(l.path))
        || selected.value.has(section.path);
    }
  } catch (err) {
    error.value = err;
  } finally {
    loading.role = false;
  }
}

function toggle(path) {
  const next = new Set(selected.value);
  if (next.has(path)) next.delete(path); else next.add(path);
  selected.value = next;
}

function toggleSection(section) {
  const paths = [section.path, ...section.links.map((l) => l.path)];
  const next = new Set(selected.value);
  const allOn = paths.every((p) => next.has(p));
  for (const p of paths) { if (allOn) next.delete(p); else next.add(p); }
  selected.value = next;
  if (!allOn) expanded[section.name] = true;
}

function sectionState(section) {
  const paths = [section.path, ...section.links.map((l) => l.path)];
  const on = paths.filter((p) => selected.value.has(p)).length;
  if (on === 0) return "none";
  return on === paths.length ? "all" : "some";
}

function countFor(section) {
  return section.links.filter((l) => selected.value.has(l.path)).length;
}

// A page whose data the role cannot read shows an empty screen. Saving grants
// the missing read, so this is a preview of what the save will do -- not a block.
function willGrant(link) {
  return (link.doctypes || []).filter((d) => !readable.value.has(d));
}

async function addRole() {
  const name = newRoleName.value.trim();
  if (!name) return;
  loading.saving = true;
  error.value = null;
  try {
    const result = await createRole(name);
    newRoleName.value = "";
    await load();
    await pickRole(result.role);
    notice.value = `Role "${result.role}" created. Tick the pages it should see, then save.`;
  } catch (err) {
    error.value = err;
  } finally {
    loading.saving = false;
  }
}

async function save() {
  if (!activeRole.value) return;
  loading.saving = true;
  error.value = null;
  try {
    const result = await saveRolePageAccess(activeRole.value, [...selected.value]);
    dirtyBaseline.value = signature();
    configured.value = true;
    const bits = [`${result.paths.length} page${result.paths.length === 1 ? "" : "s"} saved`];
    if (result.granted.length) bits.push(`granted read on ${result.granted.join(", ")}`);
    if (result.revoked.length) bits.push(`removed read on ${result.revoked.join(", ")}`);
    notice.value = `${bits.join(" · ")}. Anyone with this role sees the change after a reload.`;
    await pickRole(activeRole.value);
    await load();
  } catch (err) {
    error.value = err;
  } finally {
    loading.saving = false;
  }
}

async function removeLimit() {
  if (!activeRole.value) return;
  loading.saving = true;
  try {
    await clearRolePageAccess(activeRole.value);
    notice.value = `"${activeRole.value}" is no longer limited to a page list. Its menu goes back to following its permissions.`;
    await pickRole(activeRole.value);
    await load();
  } catch (err) {
    error.value = err;
  } finally {
    loading.saving = false;
  }
}

load();
</script>

<template>
  <PageContainer>
    <main class="rug-page rap-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Administration</RouterLink><span>›</span><strong>Role Access</strong>
      </nav>
      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Roles</span>
          <h1>Role Access</h1>
          <p>Make a role, then tick the pages it can see. Ticking a page also gives that role permission to the data behind it, so the role works straight away.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Could not complete that" :message="error.message" @retry="load" />
      <p v-if="notice" class="rap-notice" role="status">{{ notice }}</p>

      <p v-if="loading.init" class="rap-state">Loading roles and pages…</p>

      <template v-else>
        <section class="rap-create">
          <label>
            <span>New role</span>
            <input
              v-model="newRoleName"
              type="text"
              placeholder="Cashier"
              maxlength="140"
              @keydown.enter.prevent="addRole"
            />
          </label>
          <button class="rug-primary" type="button" :disabled="!newRoleName.trim() || loading.saving" @click="addRole">
            {{ loading.saving ? "Working…" : "Create role" }}
          </button>
        </section>

        <section class="rap-pick">
          <label>
            <span>Role to set up</span>
            <select :value="activeRole" @change="pickRole($event.target.value)">
              <option value="">Choose a role…</option>
              <option v-for="role in roles" :key="role.role" :value="role.role">
                {{ role.role }}{{ role.configured ? " — limited" : "" }}{{ role.user_count ? ` (${role.user_count} user${role.user_count === 1 ? "" : "s"})` : "" }}
              </option>
            </select>
          </label>
          <p class="rap-hint">
            {{ protectedRoles.join(", ") }} cannot be limited here — locking them would make the system unusable.
          </p>
        </section>

        <p v-if="loading.role" class="rap-state">Loading that role…</p>

        <template v-else-if="activeRole">
          <section class="rap-summary">
            <p>
              <strong>{{ selected.size }}</strong> of {{ totalPages }} pages ticked for <strong>{{ activeRole }}</strong>.
              <template v-if="!configured"> This role is not limited yet — its menu currently follows its permissions.</template>
            </p>
            <p v-if="configured && selected.size === 0" class="rap-warn">
              Nothing is ticked. Saving now leaves anyone with this role unable to open any page.
            </p>
          </section>

          <section class="rap-tree">
            <article v-for="section in sections" :key="section.name" class="rap-section" :data-state="sectionState(section)">
              <div class="rap-section__head">
                <button
                  class="rap-toggle"
                  type="button"
                  :aria-expanded="expanded[section.name]"
                  @click="expanded[section.name] = !expanded[section.name]"
                >
                  <span class="rap-caret" aria-hidden="true">{{ expanded[section.name] ? "▾" : "▸" }}</span>
                  <strong>{{ section.label }}</strong>
                  <small>{{ countFor(section) }}/{{ section.links.length }}</small>
                </button>
                <label class="rap-check rap-check--section">
                  <input
                    type="checkbox"
                    :checked="sectionState(section) === 'all'"
                    :indeterminate.prop="sectionState(section) === 'some'"
                    @change="toggleSection(section)"
                  />
                  <span>All</span>
                </label>
              </div>

              <ul v-if="expanded[section.name]" class="rap-links">
                <li>
                  <label class="rap-check">
                    <input type="checkbox" :checked="selected.has(section.path)" @change="toggle(section.path)" />
                    <span>{{ section.label }} dashboard</span>
                    <code>{{ section.path }}</code>
                  </label>
                </li>
                <li v-for="link in section.links" :key="link.path">
                  <label class="rap-check">
                    <input type="checkbox" :checked="selected.has(link.path)" @change="toggle(link.path)" />
                    <span>{{ link.label }}</span>
                    <code>{{ link.path }}</code>
                    <em v-if="selected.has(link.path) && willGrant(link).length" class="rap-grant">
                      will grant read on {{ willGrant(link).join(", ") }}
                    </em>
                  </label>
                </li>
              </ul>
            </article>
          </section>

          <section class="rap-actions">
            <button class="rug-primary" type="button" :disabled="loading.saving || !isDirty" @click="save">
              {{ loading.saving ? "Saving…" : isDirty ? "Save role access" : "Saved" }}
            </button>
            <button
              v-if="configured"
              class="rug-button rug-button--secondary"
              type="button"
              :disabled="loading.saving"
              @click="removeLimit"
            >Remove the limit</button>
          </section>
        </template>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.rap-page label{display:grid;gap:.4rem;font-weight:700}
.rap-page input[type=text],.rap-page select{min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.rap-state{color:var(--ref-secondary-text)}
.rap-notice{background:var(--ref-blue-background);border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:.7rem 1rem;margin:0 0 1rem}
.rap-warn{color:var(--ref-danger-text,#8C2F2A);font-weight:700}
.rap-create,.rap-pick{display:flex;flex-wrap:wrap;gap:1rem;align-items:end;margin-bottom:1.25rem}
.rap-create label,.rap-pick label{min-width:min(320px,100%)}
.rap-hint{flex:1 1 100%;margin:0;font-size:.85rem;color:var(--ref-secondary-text);font-weight:400}
.rap-summary{margin-bottom:1rem}
.rap-tree{display:grid;gap:.6rem;margin-bottom:1.5rem}
.rap-section{border:1px solid var(--ref-border-colour);border-radius:.75rem;background:var(--ref-card-background);overflow:hidden}
.rap-section[data-state=all]{border-color:var(--ref-accent-purple,#6b4ea8)}
.rap-section__head{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.55rem .9rem}
.rap-toggle{display:flex;align-items:center;gap:.6rem;background:none;border:0;padding:.2rem;cursor:pointer;color:inherit;font:inherit;flex:1;text-align:left}
.rap-toggle small{color:var(--ref-secondary-text);font-weight:400}
.rap-caret{width:1rem;display:inline-block;color:var(--ref-secondary-text)}
.rap-links{list-style:none;margin:0;padding:.2rem .9rem .8rem 2.2rem;display:grid;gap:.35rem;border-top:1px solid var(--ref-border-colour)}
.rap-check{display:flex;align-items:center;gap:.55rem;font-weight:400;cursor:pointer}
.rap-check--section{font-weight:700;cursor:pointer}
.rap-check input{min-height:0;width:1.05rem;height:1.05rem;accent-color:var(--ref-accent-purple,#6b4ea8)}
.rap-check code{font-size:.78rem;color:var(--ref-secondary-text)}
.rap-grant{font-size:.78rem;color:var(--ref-secondary-text);font-style:normal}
.rap-actions{display:flex;gap:.75rem;flex-wrap:wrap}
</style>
