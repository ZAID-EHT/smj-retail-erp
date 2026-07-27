<script setup>
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { createProduct, getProduct } from "@/services/productQuickEntry.js";

const route = useRoute();
const router = useRouter();
const editName = computed(() => route.params.name || null);

const form = reactive({
  product_name: "", image: "", image_2: "", size: "", category: "", material: "",
  carton_qty: null, stock_location_1: "", stock_location_2: "", stock_location_3: "",
  restock_qty: null, cost_price: null, margin: null, wholesale_price: null,
  retail_price: null,
});
const ids = reactive({ product_id: "", sku: "", cost_visible: true, batch: true, created: "" });
const opts = reactive({ warehouse: [], item_group: [] });
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, saving: false });
const timers = {};

async function loadOpts(kind) {
  try {
    const q = new URLSearchParams({ kind }).toString();
    const r = await fetch(`/api/method/my_store_ui.quick_entry.options.search?${q}`, { credentials: "same-origin", cache: "no-store" });
    const p = await r.json().catch(() => ({}));
    opts[kind] = p?.message?.options || [];
  } catch { opts[kind] = []; }
}

async function init() {
  loading.init = true;
  error.value = null;
  await Promise.all([loadOpts("warehouse"), loadOpts("item_group")]);
  if (editName.value) {
    try {
      const p = await getProduct(editName.value);
      Object.assign(form, {
        product_name: p.product_name, image: p.image || "", image_2: p.image_2 || "",
        size: p.size || "", category: p.category || "", material: p.material || "",
        carton_qty: p.carton_qty, stock_location_1: p.stock_location_1 || "",
        stock_location_2: p.stock_location_2 || "", stock_location_3: p.stock_location_3 || "",
        restock_qty: p.restock_qty, cost_price: p.cost_price, margin: p.margin,
        wholesale_price: p.wholesale_price, retail_price: p.retail_price,
      });
      ids.product_id = p.product_id; ids.sku = p.sku; ids.cost_visible = p.cost_visible;
      ids.batch = p.is_batch_managed; ids.created = p.created;
    } catch (caught) { error.value = caught; }
  }
  loading.init = false;
}

async function save() {
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const payload = { ...form };
    if (!ids.cost_visible) delete payload.cost_price;
    const result = await createProduct(payload, editName.value);
    notice.value = `Saved ${result.product_id} (SKU ${result.sku}).`;
    router.push(`/inventory/products/${encodeURIComponent(result.name)}`).catch(() => {});
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

onBeforeUnmount(() => Object.values(timers).forEach(window.clearTimeout));
init();
</script>

<template>
  <PageContainer>
    <main class="rug-page pqf-page">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb"><RouterLink to="/inventory/products">Products</RouterLink><span>›</span><strong>{{ editName ? "Edit Product" : "New Product" }}</strong></nav>
      <header class="rug-banner rug-banner--orange">
        <div>
          <span class="rug-badge">Product quick-create</span>
          <h1>{{ editName ? "Edit Product" : "New Product" }}</h1>
          <p>Prices sync to standard Item Price lists; new stock products are batch-managed.</p>
        </div>
      </header>

      <ErrorState v-if="error" title="Could not save product" :message="error.message" @retry="init" />
      <p v-if="notice" class="pqf-notice" role="status">{{ notice }}</p>
      <div v-if="loading.init" class="rug-skeleton"><i v-for="n in 6" :key="n" /></div>

      <form v-else class="pqf-form" @submit.prevent="save">
        <section class="rug-section-card">
          <header><div><h2>Basic Information</h2></div></header>
          <div class="rug-form-grid">
            <label><span>Product ID</span><input :value="editName ? ids.product_id : 'Auto-generated'" type="text" readonly /></label>
            <label><span>SKU</span><input :value="editName ? ids.sku : 'Auto-generated'" type="text" readonly /></label>
            <label><span>Product Name *</span><input v-model="form.product_name" type="text" required /></label>
            <label><span>Upload Image 1 (URL)</span><input v-model="form.image" type="text" placeholder="/files/…" /></label>
            <label><span>Upload Image 2 (URL)</span><input v-model="form.image_2" type="text" placeholder="/files/…" /></label>
          </div>
          <div v-if="form.image || form.image_2" class="pqf-thumbs">
            <img v-if="form.image" :src="form.image" alt="Image 1" />
            <img v-if="form.image_2" :src="form.image_2" alt="Image 2" />
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Product Classification</h2></div></header>
          <div class="rug-form-grid">
            <label><span>Size</span><input v-model="form.size" type="text" /></label>
            <label><span>Category *</span>
              <input v-model="form.category" list="pqf-groups" type="search" autocomplete="off" required />
              <datalist id="pqf-groups"><option v-for="g in opts.item_group" :key="g" :value="g" /></datalist>
            </label>
            <label><span>Material</span><input v-model="form.material" type="text" /></label>
            <label><span>Carton Qty</span><input v-model.number="form.carton_qty" type="number" min="0" step="any" /><small>Number of stock units in one carton.</small></label>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Stock Setup</h2><p v-if="ids.batch">Batch-managed product.</p></div></header>
          <div class="rug-form-grid">
            <label v-for="n in 3" :key="n"><span>Stock Location {{ n }}{{ n === 1 ? ' *' : '' }}</span>
              <input v-model="form['stock_location_' + n]" :list="'pqf-wh'" type="search" autocomplete="off" :required="n === 1" />
            </label>
            <datalist id="pqf-wh"><option v-for="w in opts.warehouse" :key="w" :value="w" /></datalist>
            <label><span>Re-Stock Qty</span><input v-model.number="form.restock_qty" type="number" min="0" step="any" /><small>Suggested replenishment quantity.</small></label>
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Pricing</h2></div></header>
          <div class="rug-form-grid">
            <label v-if="ids.cost_visible"><span>Cost Price (LKR)</span><input v-model.number="form.cost_price" type="number" min="0" step="any" /></label>
            <label><span>Margin %</span><input v-model.number="form.margin" type="number" min="0" step="any" /></label>
            <label><span>Wholesale Price (LKR)</span><input v-model.number="form.wholesale_price" type="number" min="0" step="any" /></label>
            <label><span>Retail Price (LKR)</span><input v-model.number="form.retail_price" type="number" min="0" step="any" /></label>
          </div>
        </section>

        <footer class="pqf-actions">
          <button type="button" class="rug-button rug-button--secondary" @click="router.back()">Cancel</button>
          <button type="submit" class="rug-primary" :disabled="loading.saving || !form.product_name">{{ loading.saving ? "Saving…" : "Save Product" }}</button>
        </footer>
      </form>
    </main>
  </PageContainer>
</template>

<style scoped>
.pqf-form label{display:grid;gap:.35rem;font-weight:700}
.pqf-form label :is(input,select){min-height:44px;border:1px solid var(--ref-border-colour);border-radius:.75rem;padding:0 .8rem;background:var(--ref-card-background);color:var(--ref-primary-text)}
.pqf-form label input[readonly]{opacity:.7;font-style:italic}
.pqf-form label small{font-weight:500;color:var(--ref-secondary-text)}
.pqf-thumbs{display:flex;gap:.6rem;margin-top:.6rem}
.pqf-thumbs img{width:80px;height:80px;object-fit:cover;border-radius:.6rem;border:1px solid var(--ref-border-colour)}
.pqf-actions{display:flex;justify-content:flex-end;gap:.6rem;padding-top:1rem}
.pqf-notice{padding:.6rem 1rem;border-radius:.6rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
</style>
