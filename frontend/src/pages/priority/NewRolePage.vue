<script setup>
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { onBeforeRouteLeave, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { createRoleWithPageAccess, getPageCatalogue } from "@/services/rolePages.js";

const router = useRouter();
const sections = ref([]);
const selected = ref(new Set());
const expanded = reactive({});
const form = reactive({
  role_name: "",
  disabled: false,
  desk_access: true,
  is_custom: false,
  access_level: "submit",
});
const loading = ref(true);
const saving = ref(false);
const error = ref(null);
const validation = ref("");
const dirty = ref(false);

const totalPages = computed(() => sections.value.reduce(
  (total, section) => total + selectableRows(section).length, 0,
));

function pageRows(section) {
  const rows = [{
    label: `${section.label} dashboard`, path: section.path,
    doctypes: section.doctypes || [], admin_only: section.admin_only,
  }];
  for (const link of section.links || []) {
    if (link.path !== section.path && !rows.some((row) => row.path === link.path)) rows.push(link);
  }
  return rows;
}

function selectableRows(section) {
  return pageRows(section).filter((row) => !section.admin_only && !row.admin_only);
}

function markDirty() {
  dirty.value = true;
  validation.value = "";
}

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const catalogue = await getPageCatalogue();
    sections.value = catalogue.sections;
    for (const section of sections.value) expanded[section.name] = false;
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.value = false;
  }
}

function toggle(path) {
  const next = new Set(selected.value);
  if (next.has(path)) next.delete(path); else next.add(path);
  selected.value = next;
  markDirty();
}

function toggleSection(section) {
  const paths = selectableRows(section).map((row) => row.path);
  if (!paths.length) return;
  const next = new Set(selected.value);
  const allOn = paths.every((path) => next.has(path));
  for (const path of paths) {
    if (allOn) next.delete(path); else next.add(path);
  }
  selected.value = next;
  if (!allOn) expanded[section.name] = true;
  markDirty();
}

function sectionState(section) {
  const paths = selectableRows(section).map((row) => row.path);
  if (!paths.length) return "locked";
  const on = paths.filter((path) => selected.value.has(path)).length;
  if (!on) return "none";
  return on === paths.length ? "all" : "some";
}

function countFor(section) {
  return selectableRows(section).filter((row) => selected.value.has(row.path)).length;
}

function requiredDoctypes(row) {
  return (row.doctypes || []).join(", ");
}

async function save() {
  if (saving.value) return;
  validation.value = "";
  error.value = null;
  const roleName = form.role_name.trim();
  if (!roleName) {
    validation.value = "Role Name is required.";
    return;
  }
  if (!selected.value.size) {
    validation.value = "Tick at least one page for this role.";
    return;
  }

  saving.value = true;
  try {
    const result = await createRoleWithPageAccess({
      role_name: roleName,
      disabled: Number(form.disabled),
      desk_access: Number(form.desk_access),
      is_custom: Number(form.is_custom),
      access_level: form.access_level,
      paths: [...selected.value],
    });
    dirty.value = false;
    await router.push(`/admin/roles/${encodeURIComponent(result.role)}`);
  } catch (caught) {
    error.value = caught;
  } finally {
    saving.value = false;
  }
}

function beforeUnload(event) {
  if (!dirty.value) return;
  event.preventDefault();
  event.returnValue = "";
}

onBeforeRouteLeave(() => !dirty.value || window.confirm("Leave this page? Unsaved role settings will be lost."));
window.addEventListener("beforeunload", beforeUnload);
onBeforeUnmount(() => window.removeEventListener("beforeunload", beforeUnload));
load();
</script>

<template>
  <PageContainer>
    <main class="rug-page nrp-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/admin">Administration</RouterLink><span>›</span>
        <RouterLink to="/admin/roles">Roles</RouterLink><span>›</span><strong>New Role</strong>
      </nav>

      <header class="rug-banner rug-banner--purple">
        <div>
          <span class="rug-badge">Roles</span>
          <h1>New Role</h1>
          <p>Name the role, choose what its users may do, then tick the Retail ERP pages they can open.</p>
        </div>
        <div class="rug-banner-actions">
          <button type="button" :disabled="saving" @click="router.push('/admin/roles')">Cancel</button>
          <button class="rug-primary" type="button" :disabled="saving || loading" @click="save">
            {{ saving ? "Creating…" : "Create role" }}
          </button>
        </div>
      </header>

      <ErrorState v-if="error && loading" title="Could not load role pages" :message="error.message" />
      <p v-else-if="loading" class="nrp-state">Loading available pages…</p>

      <form v-else @submit.prevent="save" @change="markDirty">
        <div v-if="error" class="rug-inline-error" role="alert">
          <strong>Unable to create role</strong><span>{{ error.message }}</span>
        </div>
        <div v-if="validation" class="rug-inline-error" role="alert">
          <strong>Check the role</strong><span>{{ validation }}</span>
        </div>

        <section class="rug-section-card nrp-details">
          <header><div><h2>Role details</h2><p>Only the core Role settings are shown here.</p></div></header>
          <label class="nrp-name">
            <span>Role Name <em>*</em></span>
            <input v-model="form.role_name" type="text" maxlength="140" required placeholder="Cashier" @input="markDirty" />
          </label>
          <div class="nrp-flags">
            <label><input v-model="form.disabled" type="checkbox" /><span><strong>Disabled</strong><small>Do not allow this role to be assigned to users yet.</small></span></label>
            <label><input v-model="form.desk_access" type="checkbox" /><span><strong>Desk Access</strong><small>Allow users with this role to be System Users.</small></span></label>
            <label><input v-model="form.is_custom" type="checkbox" /><span><strong>Is Custom</strong><small>Mark this as a site-specific custom role.</small></span></label>
          </div>
        </section>

        <section class="rug-section-card nrp-permissions">
          <header><div><h2>What can this role do?</h2><p>The chosen level applies to the data behind every page ticked below.</p></div></header>
          <div class="nrp-levels">
            <label :data-active="form.access_level === 'view'">
              <input v-model="form.access_level" type="radio" value="view" />
              <span><strong>View</strong><small>Open pages and read records.</small></span>
            </label>
            <label :data-active="form.access_level === 'edit'">
              <input v-model="form.access_level" type="radio" value="edit" />
              <span><strong>Add &amp; edit</strong><small>View, create, and update draft records.</small></span>
            </label>
            <label :data-active="form.access_level === 'submit'">
              <input v-model="form.access_level" type="radio" value="submit" />
              <span><strong>Submit</strong><small>View, create, edit, and submit records.</small></span>
            </label>
          </div>
        </section>

        <section class="rug-section-card nrp-access">
          <header>
            <div><h2>Page access</h2><p>Ticking a page also grants the matching data permissions, so the page works immediately.</p></div>
            <strong>{{ selected.size }} of {{ totalPages }} selected</strong>
          </header>

          <div class="nrp-tree">
            <article v-for="section in sections" :key="section.name" class="nrp-section" :data-state="sectionState(section)">
              <div class="nrp-section__head">
                <button type="button" class="nrp-toggle" :aria-expanded="expanded[section.name]" @click="expanded[section.name] = !expanded[section.name]">
                  <span class="nrp-caret" aria-hidden="true">{{ expanded[section.name] ? "▾" : "▸" }}</span>
                  <strong>{{ section.label }}</strong>
                  <small v-if="section.admin_only">System Manager only</small>
                  <small v-else>{{ countFor(section) }}/{{ selectableRows(section).length }}</small>
                </button>
                <label class="nrp-check nrp-check--section">
                  <input
                    type="checkbox"
                    :disabled="section.admin_only"
                    :checked="sectionState(section) === 'all'"
                    :indeterminate.prop="sectionState(section) === 'some'"
                    @change="toggleSection(section)"
                  />
                  <span>All</span>
                </label>
              </div>

              <ul v-if="expanded[section.name]" class="nrp-links">
                <li v-for="row in pageRows(section)" :key="row.path">
                  <label class="nrp-check" :data-locked="section.admin_only || row.admin_only">
                    <input
                      type="checkbox"
                      :disabled="section.admin_only || row.admin_only"
                      :checked="selected.has(row.path)"
                      @change="toggle(row.path)"
                    />
                    <span>{{ row.label }}</span>
                    <code>{{ row.path }}</code>
                    <em v-if="section.admin_only || row.admin_only">System Manager only</em>
                    <em v-else-if="selected.has(row.path) && requiredDoctypes(row)">grants {{ requiredDoctypes(row) }}</em>
                  </label>
                </li>
              </ul>
            </article>
          </div>
        </section>

        <div class="nrp-actions">
          <button type="button" class="rug-button rug-button--secondary" :disabled="saving" @click="router.push('/admin/roles')">Cancel</button>
          <button type="submit" class="rug-primary" :disabled="saving">{{ saving ? "Creating…" : "Create role" }}</button>
        </div>
      </form>
    </main>
  </PageContainer>
</template>

<style scoped>
.nrp-page form{display:grid;gap:1rem}
.nrp-state{color:var(--ref-secondary-text)}
.nrp-details,.nrp-permissions,.nrp-access{display:grid;gap:1rem}
.nrp-details>header,.nrp-permissions>header,.nrp-access>header{display:flex;justify-content:space-between;align-items:start;gap:1rem}
.nrp-details h2,.nrp-permissions h2,.nrp-access h2{margin:0}
.nrp-details header p,.nrp-permissions header p,.nrp-access header p{margin:.25rem 0 0;color:var(--ref-secondary-text)}
.nrp-name{display:grid;gap:.4rem;max-width:34rem;font-weight:700}
.nrp-name em{color:var(--ref-danger-text,#8c2f2a);font-style:normal}
.nrp-name input{min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.nrp-flags,.nrp-levels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem}
.nrp-flags label,.nrp-levels label{display:flex;align-items:flex-start;gap:.65rem;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:.85rem;cursor:pointer}
.nrp-levels label[data-active=true]{border-color:var(--ref-accent-purple,#6b4ea8);background:var(--ref-purple-background,#f5f0ff)}
.nrp-flags input,.nrp-levels input,.nrp-check input{flex:0 0 auto;width:1.05rem;height:1.05rem;min-height:0;accent-color:var(--ref-accent-purple,#6b4ea8)}
.nrp-flags span,.nrp-levels span{display:grid;gap:.2rem}
.nrp-flags small,.nrp-levels small{color:var(--ref-secondary-text);font-weight:400;line-height:1.35}
.nrp-tree{display:grid;gap:.6rem}
.nrp-section{border:1px solid var(--ref-border-colour);border-radius:.75rem;background:var(--ref-card-background);overflow:hidden}
.nrp-section[data-state=all]{border-color:var(--ref-accent-purple,#6b4ea8)}
.nrp-section[data-state=locked]{opacity:.7}
.nrp-section__head{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.55rem .9rem}
.nrp-toggle{display:flex;align-items:center;gap:.6rem;background:none;border:0;padding:.2rem;cursor:pointer;color:inherit;font:inherit;flex:1;text-align:left}
.nrp-toggle small{color:var(--ref-secondary-text);font-weight:400}
.nrp-caret{width:1rem;color:var(--ref-secondary-text)}
.nrp-links{list-style:none;margin:0;padding:.45rem .9rem .8rem 2.2rem;display:grid;gap:.45rem;border-top:1px solid var(--ref-border-colour)}
.nrp-check{display:flex;align-items:center;gap:.55rem;font-weight:400;cursor:pointer}
.nrp-check--section{font-weight:700}
.nrp-check code{font-size:.78rem;color:var(--ref-secondary-text)}
.nrp-check em{font-size:.78rem;color:var(--ref-secondary-text);font-style:normal}
.nrp-check[data-locked=true]{cursor:not-allowed;color:var(--ref-secondary-text)}
.nrp-actions{display:flex;justify-content:flex-end;gap:.75rem;flex-wrap:wrap}
@media(max-width:760px){.nrp-flags,.nrp-levels{grid-template-columns:1fr}.nrp-access>header{display:grid}.nrp-check{align-items:flex-start;flex-wrap:wrap}.nrp-check code,.nrp-check em{flex-basis:calc(100% - 1.6rem);margin-left:1.6rem}}
</style>
