<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import ComboBox from "@/components/forms/ComboBox.vue";
import ImageUpload from "@/components/forms/ImageUpload.vue";
import OptionSelect from "@/components/forms/OptionSelect.vue";
import PriceCodeSelect from "@/components/forms/PriceCodeSelect.vue";
import { createProduct, getProduct, previewIdentifiers } from "@/services/productQuickEntry.js";
import { listPriceCodes, priceCodeAdminUrl } from "@/services/priceCodes.js";

const route = useRoute();
const router = useRouter();
const editName = computed(() => route.params.name || null);

const form = reactive({
  product_name: "", image: "", image_2: "", price_code: "", category: "",
  size: "", material: "", carpet_category: "",
  carton_qty: null, stock_location_1: "", stock_location_2: "", stock_location_3: "",
  restock_qty: null, cost_price: null, wholesale_price: null, department_price: null,
  retail_price: null,
});
const ids = reactive({ product_id: "", sku: "", price_code: "", cost_visible: true, batch: true, created: "" });
// Previews of the identifiers the next save would issue. Read-only, and re-read
// rather than reserved, so opening the form does not burn a number.
const preview = reactive({ product_id: "", sku: "" });
const opts = reactive({ warehouse: [], item_group: [] });
const priceCodes = ref([]);
const priceCodeGroups = ref([]);
const canManageCodes = ref(false);
const error = ref(null);
const notice = ref(null);
const loading = reactive({ init: true, saving: false });
const timers = {};

/* Carpets are the only category with Size, Material and a Carpet Category. The
   system decides this from the selected category -- there is no switch for the
   user to set. */
const isCarpet = computed(() => {
  const category = (form.category || "").trim().toLowerCase();
  if (!category) return false;
  return category === "carpets" || category.includes("carpet");
});

const selectedCode = computed(() =>
  priceCodes.value.find((code) => code.price_code === form.price_code) || null);

const skuPreview = computed(() => {
  if (editName.value) return ids.sku;
  if (selectedCode.value) return selectedCode.value.next_sku;
  return preview.sku || "Auto-generated on save";
});

const productIdPreview = computed(() =>
  (editName.value ? ids.product_id : preview.product_id || "Auto-generated on save"));

function openPriceCodeAdmin() {
  window.open(priceCodeAdminUrl(), "_blank", "noopener");
}

/* Choosing a code fills in its preset prices. They stay editable afterwards --
   the preset is a starting point, not a lock. */
function applyPriceCode() {
  const code = selectedCode.value;
  if (!code) return;
  form.wholesale_price = code.wholesale_price;
  form.department_price = code.department_price;
  form.retail_price = code.retail_price;
  if (!form.category) form.category = code.category;
}

async function loadOpts(kind) {
  try {
    const q = new URLSearchParams({ kind }).toString();
    const r = await fetch(`/api/method/my_store_ui.quick_entry.options.search?${q}`, { credentials: "same-origin", cache: "no-store" });
    const p = await r.json().catch(() => ({}));
    opts[kind] = p?.message?.options || [];
  } catch { opts[kind] = []; }
}

async function loadPriceCodes() {
  try {
    const result = await listPriceCodes();
    priceCodes.value = result?.codes || [];
    priceCodeGroups.value = result?.groups || [];
    canManageCodes.value = Boolean(result?.can_manage);
  } catch {
    priceCodes.value = [];
    priceCodeGroups.value = [];
    canManageCodes.value = false;
  }
}

async function loadPreview() {
  if (editName.value) return;
  try {
    const result = await previewIdentifiers(form.price_code);
    preview.product_id = result?.product_id || "";
    preview.sku = result?.sku || "";
  } catch { /* a preview that cannot be read simply stays as the placeholder */ }
}

async function init() {
  loading.init = true;
  error.value = null;
  await Promise.all([loadOpts("warehouse"), loadOpts("item_group"), loadPriceCodes()]);
  if (editName.value) {
    try {
      const p = await getProduct(editName.value);
      Object.assign(form, {
        product_name: p.product_name, image: p.image || "", image_2: p.image_2 || "",
        price_code: p.price_code || "", category: p.category || "",
        size: p.size || "", material: p.material || "", carpet_category: p.carpet_category || "",
        carton_qty: p.carton_qty, stock_location_1: p.stock_location_1 || "",
        stock_location_2: p.stock_location_2 || "", stock_location_3: p.stock_location_3 || "",
        restock_qty: p.restock_qty, cost_price: p.cost_price,
        wholesale_price: p.wholesale_price, department_price: p.department_price,
        retail_price: p.retail_price,
      });
      ids.product_id = p.product_id; ids.sku = p.sku; ids.price_code = p.price_code || "";
      ids.cost_visible = p.cost_visible;
      ids.batch = p.is_batch_managed; ids.created = p.created;
    } catch (caught) { error.value = caught; }
  } else {
    await loadPreview();
  }
  loading.init = false;
}

/* A code from another category would be refused on save, so clearing it when the
   category changes keeps the form honest rather than letting it fail later. */
watch(() => form.category, (category) => {
  if (!form.price_code) return;
  const code = selectedCode.value;
  if (code && category && code.category !== category) form.price_code = "";
});

watch(() => form.price_code, () => {
  applyPriceCode();
  loadPreview();
});

// The Price Codes page opens in another tab; pick up anything added there when
// this tab is looked at again.
function refreshOnFocus() {
  if (document.visibilityState === "visible") loadPriceCodes();
}

async function save() {
  loading.saving = true;
  error.value = null;
  notice.value = null;
  try {
    const payload = { ...form };
    if (!ids.cost_visible) delete payload.cost_price;
    // Carpet-only attributes never travel for a non-carpet product.
    if (!isCarpet.value) {
      payload.size = "";
      payload.material = "";
      payload.carpet_category = "";
    }
    const result = await createProduct(payload, editName.value);
    notice.value = `Saved ${result.product_id} (SKU ${result.sku}).`;
    router.push(`/inventory/products/${encodeURIComponent(result.name)}`).catch(() => {});
  } catch (caught) { error.value = caught; }
  finally { loading.saving = false; }
}

onMounted(() => document.addEventListener("visibilitychange", refreshOnFocus));
onBeforeUnmount(() => {
  document.removeEventListener("visibilitychange", refreshOnFocus);
  Object.values(timers).forEach(window.clearTimeout);
});
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
          <header>
            <div><h2>Basic Information</h2></div>
            <button
              v-if="canManageCodes"
              type="button"
              class="pqf-codes-button"
              @click="openPriceCodeAdmin"
            >Price Codes</button>
          </header>
          <div class="rug-form-grid">
            <label><span>Product ID</span>
              <input :value="productIdPreview" type="text" readonly />
              <small v-if="!editName">Preview of the next ID. Settled when the product is saved.</small>
            </label>
            <!-- The SKU is issued by the price code, so the field offers the codes
                 themselves -- searchable and grouped by category -- rather than a
                 number nobody can choose. -->
            <label><span>SKU</span>
              <input v-if="editName" :value="ids.sku" type="text" readonly />
              <PriceCodeSelect
                v-else
                v-model="form.price_code"
                :groups="priceCodeGroups"
                :category="form.category"
              />
              <small v-if="editName">Issued from {{ ids.price_code || "the default series" }}; part of the product's identity and fixed.</small>
              <small v-else-if="form.price_code">Will be issued as <strong>{{ skuPreview }}</strong>, continuing the {{ form.price_code }} series.</small>
              <small v-else>Pick a price code to number this product within it, or leave it blank for the default series.</small>
            </label>
            <label><span>Product Name *</span><input v-model="form.product_name" type="text" required /></label>
            <ImageUpload v-model="form.image" label="Upload Image 1" />
            <ImageUpload v-model="form.image_2" label="Upload Image 2" />
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Product Classification</h2></div></header>
          <div class="rug-form-grid">
            <label><span>Product Category *</span>
              <ComboBox
                v-model="form.category"
                :options="opts.item_group"
                placeholder="Type to search a category…"
                no-options-text="No product category has been set up yet."
                required
              />
            </label>
            <label><span>Carton Qty</span><input v-model.number="form.carton_qty" type="number" min="0" step="any" /><small>Number of stock units in one carton.</small></label>
          </div>

          <!-- Carpets only. The system decides this from the category. -->
          <div v-if="isCarpet" class="rug-form-grid pqf-carpet">
            <OptionSelect v-model="form.size" option-type="Product Size" label="Size" searchable />
            <OptionSelect v-model="form.material" option-type="Product Material" label="Material" searchable />
            <OptionSelect v-model="form.carpet_category" option-type="Carpet Category" label="Carpet Category" searchable />
          </div>
        </section>

        <section class="rug-section-card">
          <header><div><h2>Stock Setup</h2><p v-if="ids.batch">Batch-managed product.</p></div></header>
          <div class="rug-form-grid">
            <label v-for="n in 3" :key="n"><span>Stock Location {{ n }}{{ n === 1 ? ' *' : '' }}</span>
              <ComboBox
                v-model="form['stock_location_' + n]"
                :options="opts.warehouse"
                :required="n === 1"
                placeholder="Type to search a location…"
                no-options-text="No stock location is available for this company."
              />
            </label>
            <label><span>Re-Stock Qty</span><input v-model.number="form.restock_qty" type="number" min="0" step="any" /><small>Suggested replenishment quantity.</small></label>
          </div>
        </section>

        <section class="rug-section-card">
          <header>
            <div>
              <h2>Pricing</h2>
              <p v-if="selectedCode">Filled in from price code {{ selectedCode.price_code }}. Change any of them for this product.</p>
            </div>
          </header>
          <div class="rug-form-grid">
            <label v-if="ids.cost_visible"><span>Cost Price (LKR)</span><input v-model.number="form.cost_price" type="number" min="0" step="any" /></label>
            <label><span>Wholesale Price (LKR)</span><input v-model.number="form.wholesale_price" type="number" min="0" step="any" /></label>
            <label><span>Department Price (LKR)</span><input v-model.number="form.department_price" type="number" min="0" step="any" /></label>
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
.pqf-codes-button{border:1px solid var(--ref-border-colour);border-radius:.6rem;background:var(--ref-card-background);color:var(--ref-primary-text);font-weight:700;padding:.4rem .9rem;cursor:pointer}
.pqf-codes-button:hover{border-color:var(--ref-accent, var(--ref-border-colour))}
.pqf-carpet{margin-top:1rem;padding-top:1rem;border-top:1px dashed var(--ref-border-colour)}
.pqf-thumbs{display:flex;gap:.6rem;margin-top:.6rem}
.pqf-thumbs img{width:80px;height:80px;object-fit:cover;border-radius:.6rem;border:1px solid var(--ref-border-colour)}
.pqf-actions{display:flex;justify-content:flex-end;gap:.6rem;padding-top:1rem}
.pqf-notice{padding:.6rem 1rem;border-radius:.6rem;background:var(--ref-success-background);color:var(--ref-success);font-weight:700}
</style>
