<script setup>
/* Price Codes: the page the Product form's "Price Codes" button opens in a new
   tab. A code belongs to one product category, carries the Wholesale, Department
   and Retail prices a product of that code starts from, and owns the running
   number behind its SKUs. Categories can be added from here too, so a new
   category and its first code are one visit rather than two. */
import { computed, reactive, ref } from "vue";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import {
  addCategory, deletePriceCode, listCategories, listPriceCodes, savePriceCode,
} from "@/services/priceCodes.js";

const groups = ref([]);
const categories = ref([]);
const canManage = ref(false);
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, saving: false });
const search = ref("");
const showInactive = ref(false);

const draft = reactive({
  price_code: "", category: "", description: "",
  wholesale_price: null, department_price: null, retail_price: null,
});
const newCategory = ref("");
// The code being edited inline, keyed by name, with its own copy of the prices so
// a cancelled edit leaves the list untouched.
const editing = reactive({ name: "", description: "", wholesale_price: null, department_price: null, retail_price: null });

const totalCodes = computed(() => groups.value.reduce((sum, group) => sum + group.codes.length, 0));

async function load() {
  error.value = null;
  try {
    const [codeResult, categoryResult] = await Promise.all([
      listPriceCodes({ query: search.value, includeInactive: showInactive.value }),
      listCategories(),
    ]);
    groups.value = codeResult?.groups || [];
    canManage.value = Boolean(codeResult?.can_manage);
    categories.value = categoryResult?.categories || [];
  } catch (caught) {
    error.value = caught;
  } finally {
    loading.init = false;
  }
}

async function create() {
  if (!draft.price_code.trim() || !draft.category) return;
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const saved = await savePriceCode({
      price_code: draft.price_code.trim().toUpperCase(),
      category: draft.category,
      description: draft.description,
      wholesale_price: draft.wholesale_price || 0,
      department_price: draft.department_price || 0,
      retail_price: draft.retail_price || 0,
    });
    notice.value = `Added ${saved.price_code}. Its first product becomes ${saved.next_sku}.`;
    Object.assign(draft, {
      price_code: "", description: "",
      wholesale_price: null, department_price: null, retail_price: null,
    });
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

function startEdit(code) {
  Object.assign(editing, {
    name: code.name,
    description: code.description,
    wholesale_price: code.wholesale_price,
    department_price: code.department_price,
    retail_price: code.retail_price,
  });
}

function cancelEdit() {
  editing.name = "";
}

async function applyEdit() {
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    await savePriceCode({
      description: editing.description,
      wholesale_price: editing.wholesale_price || 0,
      department_price: editing.department_price || 0,
      retail_price: editing.retail_price || 0,
    }, editing.name);
    notice.value = `Updated ${editing.name}.`;
    editing.name = "";
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

async function toggleActive(code) {
  loading.saving = true;
  error.value = null;
  try {
    await savePriceCode({ is_active: code.is_active ? 0 : 1 }, code.name);
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

async function remove(code) {
  // Deleting a code that products already carry is refused by the server; saying
  // so here first means the user is not surprised by the refusal.
  if (!window.confirm(`Delete ${code.name}? Products already using it will block the deletion.`)) return;
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    await deletePriceCode(code.name);
    notice.value = `Deleted ${code.name}.`;
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

async function createCategory() {
  const name = newCategory.value.trim();
  if (!name) return;
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const saved = await addCategory(name);
    notice.value = `Added category ${saved.category}.`;
    newCategory.value = "";
    draft.category = saved.category;
    await load();
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

load();
</script>

<template>
  <PageContainer>
    <main class="rug-page pca-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/admin">Administration</RouterLink><span>›</span><strong>Price Codes</strong></nav>
      <header class="rug-banner rug-banner--orange">
        <div>
          <span class="rug-badge">Product pricing</span>
          <h1>Price Codes</h1>
          <p>A code belongs to one product category and carries the Wholesale, Department and Retail prices its products start from. Each code numbers its own SKUs — CCA 1, CCA 2, and so on.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Could not complete that" :message="error.message" @retry="load" />
      <p v-if="notice" class="pca-notice" role="status">{{ notice }}</p>
      <div v-if="loading.init" class="rug-skeleton"><i v-for="n in 5" :key="n" /></div>

      <template v-else>
        <p v-if="!canManage" class="pca-hint">You can view these codes but only an administrator can change them.</p>

        <section v-if="canManage" class="rug-section-card">
          <header><div><h2>Add a price code</h2><p>The code and its category are fixed once created, because the code becomes part of every SKU issued from it.</p></div></header>
          <form class="rug-form-grid pca-form" @submit.prevent="create">
            <label><span>Price Code *</span><input v-model="draft.price_code" type="text" placeholder="CCA" required /></label>
            <label><span>Product Category *</span>
              <select v-model="draft.category" required>
                <option value="">Select…</option>
                <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
              </select>
            </label>
            <label class="pca-wide"><span>Description</span><input v-model="draft.description" type="text" placeholder="What this code covers" /></label>
            <label><span>Wholesale Price (LKR)</span><input v-model.number="draft.wholesale_price" type="number" min="0" step="any" /></label>
            <label><span>Department Price (LKR)</span><input v-model.number="draft.department_price" type="number" min="0" step="any" /></label>
            <label><span>Retail Price (LKR)</span><input v-model.number="draft.retail_price" type="number" min="0" step="any" /></label>
            <div class="pca-wide pca-actions">
              <button type="submit" class="rug-primary" :disabled="loading.saving || !draft.price_code.trim() || !draft.category">
                {{ loading.saving ? "Saving…" : "Add Price Code" }}
              </button>
            </div>
          </form>
        </section>

        <section v-if="canManage" class="rug-section-card">
          <header><div><h2>Add a product category</h2><p>Created as a standard Item Group, so it behaves exactly like a category made anywhere else.</p></div></header>
          <form class="pca-inline-form" @submit.prevent="createCategory">
            <input v-model="newCategory" type="text" placeholder="Home Appliances" />
            <button type="submit" class="rug-button rug-button--secondary" :disabled="loading.saving || !newCategory.trim()">Add Category</button>
          </form>
        </section>

        <section class="rug-section-card">
          <header>
            <div><h2>Existing codes</h2><p>{{ totalCodes }} code(s) across {{ groups.length }} categor{{ groups.length === 1 ? 'y' : 'ies' }}.</p></div>
          </header>
          <div class="pca-filters">
            <input v-model="search" type="search" placeholder="Search code, description or category…" @input="load" />
            <label class="pca-check"><input v-model="showInactive" type="checkbox" @change="load" /> Show inactive</label>
          </div>

          <p v-if="!groups.length" class="pca-hint">No price codes yet.</p>

          <div v-for="group in groups" :key="group.category" class="pca-group">
            <h3>{{ group.category }}</h3>
            <div class="pca-table-scroll">
              <table class="pca-table">
                <thead>
                  <tr>
                    <th>Code</th><th>Description</th><th>Wholesale</th><th>Department</th>
                    <th>Retail</th><th>Next SKU</th><th v-if="canManage">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="code in group.codes" :key="code.name" :class="{ 'pca-row--inactive': !code.is_active }">
                    <td><strong>{{ code.price_code }}</strong><em v-if="!code.is_active"> (inactive)</em></td>
                    <template v-if="editing.name === code.name">
                      <td><input v-model="editing.description" type="text" /></td>
                      <td><input v-model.number="editing.wholesale_price" type="number" min="0" step="any" /></td>
                      <td><input v-model.number="editing.department_price" type="number" min="0" step="any" /></td>
                      <td><input v-model.number="editing.retail_price" type="number" min="0" step="any" /></td>
                      <td>{{ code.next_sku }}</td>
                      <td class="pca-row-actions">
                        <button type="button" class="rug-primary" :disabled="loading.saving" @click="applyEdit">Save</button>
                        <button type="button" class="rug-button rug-button--secondary" @click="cancelEdit">Cancel</button>
                      </td>
                    </template>
                    <template v-else>
                      <td>{{ code.description || "—" }}</td>
                      <td>{{ code.wholesale_price }}</td>
                      <td>{{ code.department_price }}</td>
                      <td>{{ code.retail_price }}</td>
                      <td>{{ code.next_sku }}</td>
                      <td v-if="canManage" class="pca-row-actions">
                        <button type="button" class="rug-button rug-button--secondary" @click="startEdit(code)">Edit</button>
                        <button type="button" class="rug-button rug-button--secondary" :disabled="loading.saving" @click="toggleActive(code)">
                          {{ code.is_active ? "Deactivate" : "Activate" }}
                        </button>
                        <button type="button" class="rug-button rug-button--secondary pca-danger" :disabled="loading.saving" @click="remove(code)">Delete</button>
                      </td>
                    </template>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </template>
    </main>
  </PageContainer>
</template>

<style scoped>
.pca-form label,.pca-page label{display:grid;gap:.35rem;font-weight:700}
.pca-page :is(input,select){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.pca-wide{grid-column:1/-1}
.pca-actions{display:flex;justify-content:flex-end}
.pca-inline-form{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center}
.pca-inline-form input{flex:1 1 16rem}
.pca-filters{display:flex;gap:1rem;align-items:center;flex-wrap:wrap;margin-bottom:1rem}
.pca-filters input[type=search]{flex:1 1 18rem}
.pca-check{display:inline-flex;align-items:center;gap:.4rem;font-weight:500}
.pca-check input{min-height:20px;width:18px}
.pca-group{margin-top:1.4rem}
.pca-group h3{margin:0 0 .5rem;font-size:1rem}
/* Wide tables scroll inside their own box so the page never scrolls sideways. */
.pca-table-scroll{overflow-x:auto}
.pca-table{width:100%;border-collapse:collapse;min-width:44rem}
.pca-table :is(th,td){text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--ref-border-colour);font-weight:500}
.pca-table th{font-weight:700;color:var(--ref-secondary-text);font-size:.82rem;text-transform:uppercase;letter-spacing:.03em}
.pca-table input{min-height:36px}
.pca-row--inactive{opacity:.55}
.pca-row-actions{display:flex;gap:.35rem;flex-wrap:wrap}
.pca-danger{color:var(--ref-danger)}
.pca-notice{padding:.6rem 1rem;border-radius:.6rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
.pca-hint{color:var(--ref-secondary-text)}
</style>
