<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";

import ErrorState from "@/components/feedback/ErrorState.vue";
import {
  SmjActualStockWarehouse,
  SmjAvailableStockCheck,
  SmjClose,
  SmjCreditGauge,
  SmjInventoryCubeLayers,
  SmjReserveCubeLock,
  SmjSalesCartPulse,
} from "@/components/icons";
import PageContainer from "@/components/layout/PageContainer.vue";
import ProductImageCarousel from "@/components/data/ProductImageCarousel.vue";
import { createSmartOrder, getCartPricing, getSmartSales, searchSmartCustomers } from "@/services/smartSales.js";
import { getCustomerCreditStatus } from "@/services/wholesale.js";
import { getCustomerSalesAssignment, searchSalesTeams } from "@/services/salesTeam.js";
import SalesTeamCard from "@/components/sales/SalesTeamCard.vue";

const router = useRouter();
const data = ref(null);
const error = ref(null);
const loading = ref(false);
const saving = ref(false);
const repricing = ref(false);
const search = ref("");
const group = ref("");
const warehouse = ref("");
const priceList = ref("");
const customerSearch = ref("");
const customers = ref([]);
const customer = ref("");
const credit = ref(null);
const notice = ref("");
const cart = reactive({});
let controller;
let timer;

const customerSelected = computed(() => Boolean(customer.value));

function availabilityOf(item) {
  return Number(item.available_to_sell ?? item.actual_qty ?? 0);
}
function isStockItem(item) {
  return item.is_stock_item !== 0; // undefined or 1 => treat as stock item
}
function outOfStock(item) {
  return isStockItem(item) && availabilityOf(item) <= 0;
}

/* Sales team + commission for the selected customer. Cleared the instant the
   customer changes so the previous customer's team is never shown. */
const salesTeam = ref(null);
const salesTeamLoading = ref(false);
const salesTeamWarnings = ref([]);
const canOverrideTeam = ref(false);

/* A team chosen for this one order. It never touches the customer master -- that
   is a separate, deliberate action on the customer form. */
const overrideTeam = ref("");
const overrideReason = ref("");
const overrideOpen = ref(false);
const overrideOptions = ref([]);
const overrideBusy = ref(false);
const overrideError = ref("");

// What the customer is actually assigned, kept separate so cancelling an override
// restores it without another round trip.
const customerDefaultTeam = ref(null);

async function loadSalesTeam() {
  salesTeam.value = null;
  customerDefaultTeam.value = null;
  salesTeamWarnings.value = [];
  clearOverride();
  if (!customer.value) { salesTeamLoading.value = false; return; }
  salesTeamLoading.value = true;
  const forCustomer = customer.value;
  try {
    const result = await getCustomerSalesAssignment(forCustomer);
    // Ignore a late response for a customer that is no longer selected.
    if (customer.value !== forCustomer) return;
    customerDefaultTeam.value = result.assigned ? result.assignment : null;
    salesTeam.value = customerDefaultTeam.value;
    salesTeamWarnings.value = result.warnings || [];
    canOverrideTeam.value = Boolean(result.can_override);
  } catch {
    if (customer.value === forCustomer) salesTeam.value = null;
  } finally {
    if (customer.value === forCustomer) salesTeamLoading.value = false;
  }
}

function clearOverride() {
  overrideTeam.value = "";
  overrideReason.value = "";
  overrideOpen.value = false;
  overrideError.value = "";
}

async function openOverride() {
  overrideOpen.value = true;
  overrideError.value = "";
  overrideBusy.value = true;
  try {
    overrideOptions.value = await searchSalesTeams({
      company: data.value?.company || "", active_only: "1", limit: 50,
    });
  } catch (caught) {
    overrideError.value = caught?.message || "Sales teams could not be loaded.";
  } finally {
    overrideBusy.value = false;
  }
}

function applyOverride() {
  if (!overrideTeam.value) { overrideError.value = "Choose a team."; return; }
  if (!overrideReason.value.trim()) {
    overrideError.value = "A reason is required when you use another customer's team.";
    return;
  }
  const chosen = overrideOptions.value.find((o) => o.value === overrideTeam.value);
  if (!chosen) { overrideError.value = "Choose a team."; return; }
  salesTeam.value = {
    team: chosen.value,
    team_name: chosen.label,
    sales_manager: chosen.sales_manager,
    commission_rate: chosen.commission_rate,
    is_active: chosen.is_active,
    members: chosen.members,
    source: "Overridden",
    override_reason: overrideReason.value.trim(),
  };
  overrideOpen.value = false;
  overrideError.value = "";
}

function cancelOverride() {
  clearOverride();
  salesTeam.value = customerDefaultTeam.value;
}

async function loadCredit() {
  credit.value = null;
  if (!customer.value) return;
  try {
    credit.value = await getCustomerCreditStatus(customer.value, data.value?.company);
  } catch {
    credit.value = null;
  }
}

const cartRows = computed(() => Object.values(cart));
const cartQuantity = computed(() => cartRows.value.reduce((sum, row) => sum + Number(row.qty || 0), 0));
const total = computed(() => cartRows.value.reduce((sum, row) => sum + Number(row.qty) * Number(row.rate || 0), 0));
const selectedCustomer = computed(() => customers.value.find((row) => row.name === customer.value));

/* Credit gate. A Credit Customer whose available credit cannot cover this cart is
   prompted to clear pending dues before the order is created. The server enforces
   the same rule -- this only explains it before the user hits Create. */
const creditShortfall = computed(() => {
  const status = credit.value;
  if (!status || !status.is_credit_customer) return 0;
  if (status.available_credit === null || status.available_credit === undefined) return 0;
  return Math.max(total.value - Number(status.available_credit || 0), 0);
});
const creditBlocked = computed(() => creditShortfall.value > 0 || !!credit.value?.has_overdue);
const showCreditPrompt = ref(false);
const stockSummary = computed(() => (data.value?.items || []).reduce(
  (summary, item) => ({
    actual: summary.actual + Number(item.actual_qty || 0),
    reserved: summary.reserved + Number(item.reserved_qty || 0),
    available: summary.available + Number(item.available_to_sell ?? item.actual_qty ?? 0),
  }),
  { actual: 0, reserved: 0, available: 0 },
));

async function load() {
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = null;
  try {
    data.value = await getSmartSales({
      page: 1,
      page_length: 48,
      search: search.value,
      item_group: group.value,
      warehouse: warehouse.value,
      price_list: priceList.value,
      customer: customer.value,
    }, controller.signal);
    // Deliberately not defaulted. This select filters the catalogue's stock
    // figures, and pinning it to whichever warehouse happens to sort first
    // hides every unit held anywhere else: a purchase received into one
    // warehouse looked like it had never arrived. Empty means "all
    // warehouses", which is the honest total. A warehouse is still required
    // to create the order, and createOrder() enforces that.
    priceList.value = data.value.price_list || priceList.value || "";
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    loading.value = false;
  }
}

function schedule() {
  clearTimeout(timer);
  timer = setTimeout(load, 300);
}

/* Single customer field: typing searches, the list shows the closest matches, and
   choosing one sets the customer. There is no separate "choose customer" select. */
const suggestionsOpen = ref(false);
const customerLoading = ref(false);
const activeSuggestion = ref(0);
let customerTimer;
let blurTimer;

async function findCustomers() {
  const term = customerSearch.value.trim();
  if (term.length < 2) {
    customers.value = [];
    customerLoading.value = false;
    return;
  }
  customerLoading.value = true;
  try {
    customers.value = await searchSmartCustomers(term, controller?.signal);
    activeSuggestion.value = 0;
  } catch (caught) {
    if (caught.name !== "AbortError") customers.value = [];
  } finally {
    customerLoading.value = false;
  }
}

function onCustomerInput() {
  suggestionsOpen.value = true;
  // The chosen customer is only cleared once the text no longer matches it, so
  // editing the text does not silently drop the selection mid-keystroke.
  if (customer.value && customerSearch.value !== selectedLabel()) {
    customer.value = "";
    credit.value = null;
    salesTeam.value = null;
  }
  window.clearTimeout(customerTimer);
  customerTimer = window.setTimeout(findCustomers, 250);
}

function onCustomerFocus() {
  suggestionsOpen.value = true;
  if (customerSearch.value.trim().length >= 2 && !customers.value.length) findCustomers();
}

function closeSuggestionsSoon() {
  // Delay so a click on an option is registered before the list closes.
  blurTimer = window.setTimeout(() => { suggestionsOpen.value = false; }, 120);
}

function selectedLabel() {
  const row = customers.value.find((c) => c.name === customer.value);
  return row ? row.customer_name : customerSearch.value;
}

function pickCustomer(row) {
  window.clearTimeout(blurTimer);
  customer.value = row.name;
  customerSearch.value = row.customer_name;
  suggestionsOpen.value = false;
  // watch(customer, onCustomerChange) reloads pricing, credit and the catalogue.
}

function clearCustomer() {
  window.clearTimeout(blurTimer);
  customer.value = "";
  customerSearch.value = "";
  customers.value = [];
  credit.value = null;
  salesTeam.value = null;
  salesTeamLoading.value = false;
  suggestionsOpen.value = false;
}

function onCustomerKeydown(event) {
  if (event.key === "ArrowDown" || event.key === "ArrowUp") {
    if (!suggestionsOpen.value) suggestionsOpen.value = true;
    if (!customers.value.length) return;
    event.preventDefault();
    const step = event.key === "ArrowDown" ? 1 : -1;
    const count = customers.value.length;
    activeSuggestion.value = (activeSuggestion.value + step + count) % count;
    return;
  }
  if (event.key === "Enter" && suggestionsOpen.value && customers.value.length) {
    event.preventDefault();
    pickCustomer(customers.value[activeSuggestion.value]);
    return;
  }
  if (event.key === "Escape") suggestionsOpen.value = false;
}

// Authoritative repricing + stock re-check through the backend pricing engine.
// Called when the customer changes or a line is added, so the cart never keeps a
// previous customer's prices and never holds an unavailable line.
async function repriceCart() {
  if (!customerSelected.value || !cartRows.value.length) return;
  repricing.value = true;
  try {
    const result = await getCartPricing({
      customer: customer.value,
      company: data.value?.company || "",
      warehouse: warehouse.value,
      price_list: priceList.value,
      items: cartRows.value.map(({ item_code, qty }) => ({ item_code, qty })),
    });
    const byCode = new Map((result.lines || []).map((line) => [line.item_code, line]));
    for (const row of cartRows.value) {
      const line = byCode.get(row.item_code);
      if (!line) {
        delete cart[row.item_code];
        continue;
      }
      row.rate = line.rate;
      row.price_list_rate = line.price_list_rate;
      row.source = line.source;
      row.available_to_sell = line.available_to_sell;
      row.stock_status = line.stock_status;
      if (line.stock_status === "out_of_stock") {
        delete cart[row.item_code];
        notice.value = `${row.item_name} was removed — no available stock.`;
      } else if (line.max_qty != null && row.qty > line.max_qty) {
        row.qty = line.max_qty;
        notice.value = `${row.item_name} quantity reduced to the available ${line.max_qty}.`;
      }
    }
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  } finally {
    repricing.value = false;
  }
}

/* The two image slots the product form offers, in order, with the empty ones
   dropped so a product carrying only the second still shows it. */
function productImages(item) {
  return [item.image, item.image_2].filter(Boolean);
}

function add(item) {
  error.value = null;
  if (!customerSelected.value) {
    notice.value = "Select a customer to begin the order.";
    return;
  }
  if (outOfStock(item)) {
    notice.value = `${item.item_name} is out of stock.`;
    return;
  }
  notice.value = "";
  if (!cart[item.item_code]) {
    cart[item.item_code] = {
      item_code: item.item_code,
      item_name: item.item_name,
      rate: item.rate,
      price_list_rate: item.rate,
      qty: 1,
      source: null,
      available_to_sell: availabilityOf(item),
    };
  } else {
    cart[item.item_code].qty += 1;
  }
  repriceCart();
}

async function onCustomerChange() {
  notice.value = cartRows.value.length ? "Repricing the cart for the selected customer…" : "";
  // Clear the old team immediately, before anything is awaited.
  salesTeam.value = null;
  salesTeamLoading.value = Boolean(customer.value);
  await Promise.all([loadCredit(), loadSalesTeam()]);
  await load();
  await repriceCart();
  if (cartRows.value.length) notice.value = "Cart prices updated for the selected customer.";
}

async function save() {
  if (saving.value) return;
  // Credit customers over their limit (or in arrears) are prompted to clear dues.
  if (creditBlocked.value && !showCreditPrompt.value) {
    showCreditPrompt.value = true;
    return;
  }
  if (!customer.value || !warehouse.value || !cartRows.value.length) {
    error.value = new Error("Choose a customer and warehouse, then add at least one product.");
    return;
  }
  saving.value = true;
  error.value = null;
  try {
    const result = await createSmartOrder({
      request_id: crypto.randomUUID(),
      customer: customer.value,
      company: data.value.company,
      warehouse: warehouse.value,
      price_list: priceList.value,
      items: cartRows.value.map(({ item_code, qty }) => ({ item_code, qty })),
      // Only sent when a team other than the customer's own was chosen. The server
      // re-authorises it either way.
      sales_team: overrideTeam.value || "",
      sales_team_override_reason: overrideTeam.value ? overrideReason.value.trim() : "",
    });
    await router.push(result.route);
  } catch (caught) {
    error.value = caught;
  } finally {
    saving.value = false;
  }
}

const sourceLabels = {
  pricing_rule: "Pricing Rule",
  customer_price_list: "Customer price list",
  price_list: "Price list",
  unpriced: "No price set",
};

watch([group, warehouse, priceList], load);
watch(customer, onCustomerChange);
load();
onBeforeUnmount(() => {
  clearTimeout(timer);
  window.clearTimeout(customerTimer);
  window.clearTimeout(blurTimer);
  controller?.abort();
});
</script>

<template>
  <PageContainer>
    <ErrorState
      v-if="error && !data"
      title="Unable to load Smart Sales"
      :message="error.message"
      @retry="load"
    />
    <main v-else class="rug-page smj-sales-workspace">
      <nav class="rug-breadcrumbs" aria-label="Breadcrumb">
        <RouterLink to="/home">Home</RouterLink><span>›</span><strong>Smart Sales</strong>
      </nav>

      <header class="rug-banner rug-banner--green">
        <div>
          <span class="rug-badge">Wholesale catalogue &amp; cart</span>
          <h1>Smart Sales</h1>
          <p>Select a customer, check live credit and stock, then create a standard ERPNext Draft Sales Order.</p>
        </div>
        <button
          class="rug-primary"
          type="button"
          :disabled="saving || !customerSelected || !data?.can_create_sales_order || !cartRows.length"
          @click="save"
        >
          {{ saving ? "Creating order…" : "Create Draft Order" }}
        </button>
      </header>

      <div v-if="error" class="rug-inline-error" role="alert">{{ error.message }}</div>
      <div v-else-if="notice" class="smj-sales-notice" role="status">{{ notice }}</div>

      <section class="smj-sales-kpis" aria-label="Current sale summary">
        <article>
          <span class="smj-sales-kpis__icon"><SmjSalesCartPulse size="20" decorative /></span>
          <div><small>Cart lines</small><strong>{{ cartRows.length }}</strong><em>{{ cartQuantity }} total quantity</em></div>
        </article>
        <article>
          <span class="smj-sales-kpis__icon"><SmjActualStockWarehouse size="20" decorative /></span>
          <div><small>Actual stock shown</small><strong>{{ stockSummary.actual.toLocaleString() }}</strong><em>{{ warehouse || "across all warehouses" }}</em></div>
        </article>
        <article>
          <span class="smj-sales-kpis__icon"><SmjReserveCubeLock size="20" decorative /></span>
          <div><small>Reserved stock</small><strong>{{ stockSummary.reserved.toLocaleString() }}</strong><em>ERPNext reservations</em></div>
        </article>
        <article>
          <span class="smj-sales-kpis__icon"><SmjAvailableStockCheck size="20" decorative /></span>
          <div><small>Available to sell</small><strong>{{ stockSummary.available.toLocaleString() }}</strong><em>Actual minus reserved</em></div>
        </article>
      </section>

      <!-- Credit customer over limit or in arrears: prompt to clear dues first. -->
      <div v-if="showCreditPrompt" class="smj-print-modal" role="dialog" aria-modal="true" aria-labelledby="smj-credit-title" @click.self="showCreditPrompt = false">
        <section class="smj-credit-dialog">
          <header>
            <div>
              <h2 id="smj-credit-title">Credit limit reached</h2>
              <p>{{ selectedCustomer?.customer_name || customer }}</p>
            </div>
            <button type="button" class="smj-print-modal__close" aria-label="Close" @click="showCreditPrompt = false">×</button>
          </header>
          <div class="smj-print-modal__body">
            <p class="smj-credit-dialog__lead">
              Pending dues must be cleared before new credit entries can be made for this customer.
            </p>
            <dl class="smj-credit-dialog__facts">
              <div><dt>Outstanding</dt><dd>{{ data?.currency }} {{ Number(credit?.current_outstanding || 0).toLocaleString() }}</dd></div>
              <div v-if="credit?.credit_limit"><dt>Credit limit</dt><dd>{{ Number(credit.credit_limit).toLocaleString() }}</dd></div>
              <div v-if="credit?.available_credit !== null"><dt>Available credit</dt><dd>{{ Number(credit?.available_credit || 0).toLocaleString() }}</dd></div>
              <div><dt>This order</dt><dd>{{ Number(total).toLocaleString() }}</dd></div>
              <div v-if="creditShortfall > 0" class="is-danger"><dt>Short by</dt><dd>{{ Number(creditShortfall).toLocaleString() }}</dd></div>
              <div v-if="credit?.has_overdue" class="is-danger"><dt>Overdue</dt><dd>{{ Number(credit?.overdue_amount || 0).toLocaleString() }}</dd></div>
            </dl>
            <p class="smj-credit-dialog__note">
              Record a payment against the outstanding invoices, or ask a manager to approve this order.
            </p>
          </div>
          <footer>
            <span class="smj-print-modal__actions">
              <button type="button" @click="showCreditPrompt = false">Back to cart</button>
              <RouterLink class="rug-primary priority-button-link" :to="`/finance/payments/receive/new?party=${encodeURIComponent(customer)}`">Record payment</RouterLink>
            </span>
          </footer>
        </section>
      </div>

      <!-- Required by the business: a plain red warning until a customer is chosen.
           It disappears the moment a valid customer is selected. -->
      <div v-if="!customerSelected" class="smj-sales-customer-required" role="alert">
        <strong>Select a customer before you start this sale.</strong>
        <span>Prices, credit limits and stock availability all depend on the customer.</span>
      </div>

      <section class="rug-section-card smj-sale-context">
        <header>
          <div><h2>Sale setup</h2><p>Customer, warehouse and pricing context for this order.</p></div>
          <span v-if="selectedCustomer" class="rug-value-badge">{{ selectedCustomer.customer_name }}</span>
        </header>
        <div class="priority-sales-controls">
          <label class="smj-customer-picker">
            <span>Customer</span>
            <span class="smj-customer-picker__control">
              <input
                v-model="customerSearch"
                type="text"
                role="combobox"
                aria-autocomplete="list"
                aria-controls="smj-customer-options"
                :aria-expanded="suggestionsOpen"
                :placeholder="customerSelected ? '' : 'Start typing a name, mobile or customer ID…'"
                autocomplete="off"
                @input="onCustomerInput"
                @focus="onCustomerFocus"
                @keydown="onCustomerKeydown"
                @blur="closeSuggestionsSoon"
              />
              <button
                v-if="customerSelected || customerSearch"
                type="button"
                class="smj-customer-picker__clear"
                aria-label="Clear customer"
                @mousedown.prevent="clearCustomer"
              >&times;</button>
            </span>

            <ul v-if="suggestionsOpen" id="smj-customer-options" class="smj-customer-picker__list" role="listbox">
              <li v-if="customerLoading" class="is-state">Searching&hellip;</li>
              <li v-else-if="!customers.length" class="is-state">
                {{ customerSearch.trim().length < 2 ? "Keep typing to search customers." : "No matching customer." }}
              </li>
              <template v-else>
                <li
                  v-for="(row, index) in customers"
                  :key="row.name"
                  role="option"
                  :aria-selected="index === activeSuggestion"
                  :class="index === activeSuggestion && 'is-active'"
                  @mousedown.prevent="pickCustomer(row)"
                  @mousemove="activeSuggestion = index"
                >
                  <strong>{{ row.customer_name }}</strong>
                  <small>{{ row.name }}<template v-if="row.mobile_no"> &middot; {{ row.mobile_no }}</template></small>
                </li>
              </template>
            </ul>
          </label>
          <label>
            <span>Warehouse</span>
            <select v-model="warehouse"><option value="">All warehouses</option><option v-for="value in data?.warehouses || []" :key="value">{{ value }}</option></select>
          </label>
          <label>
            <span>Price List</span>
            <select v-model="priceList" :disabled="Boolean(data?.customer_price_list)">
              <option v-for="value in data?.price_lists || []" :key="value">{{ value }}</option>
            </select>
          </label>
        </div>
        <p v-if="data?.customer_price_list" class="smj-sale-context__pricelist">
          Pricing this order against <strong>{{ data.customer_price_list }}</strong> (this customer's price list).
        </p>

        <div
          v-if="credit"
          class="priority-credit-strip"
          :class="{ 'is-warning': credit.has_overdue || (credit.available_credit !== null && credit.available_credit <= 0) }"
        >
          <span class="smj-credit-heading"><SmjCreditGauge size="17" decorative /><strong>{{ credit.credit_type || "Credit type not set" }}</strong></span>
          <span>Outstanding <strong>{{ data?.currency }} {{ Number(credit.current_outstanding || 0).toLocaleString() }}</strong></span>
          <span v-if="credit.credit_limit">Limit <strong>{{ Number(credit.credit_limit).toLocaleString() }}</strong></span>
          <span v-if="credit.available_credit !== null">Available <strong>{{ Number(credit.available_credit).toLocaleString() }}</strong></span>
          <span v-if="credit.has_overdue" class="priority-credit-overdue">Overdue {{ Number(credit.overdue_amount).toLocaleString() }}</span>
        </div>
      </section>

      <!-- Sales team and commission for the selected customer, directly below
           Sale setup and above the catalogue so it never overlaps either. -->
      <SalesTeamCard
        :assignment="salesTeam"
        :loading="salesTeamLoading"
        :idle="!customerSelected"
        :warnings="salesTeamWarnings"
        :can-edit="Boolean(customerSelected)"
        :can-override="canOverrideTeam && Boolean(customerSelected)"
        @edit="router.push(`/sales/customers/${encodeURIComponent(customer)}/edit`)"
        @override="openOverride"
      />

      <!-- Choosing another team applies to this order only. Changing the customer's
           own team is a separate action on the customer form. -->
      <section v-if="overrideOpen" class="rug-section-card smj-team-override"
               role="dialog" aria-labelledby="smj-team-override-title">
        <header>
          <h2 id="smj-team-override-title">Use another sales team for this order</h2>
          <p>The customer keeps their own team. Only this order changes.</p>
        </header>
        <div v-if="overrideBusy" class="smj-team-card__state" role="status">Loading teams…</div>
        <template v-else>
          <label>
            <span>Sales team</span>
            <select v-model="overrideTeam" data-test="override-team">
              <option value="">Select a team</option>
              <option v-for="option in overrideOptions" :key="option.value" :value="option.value">
                {{ option.label }} — {{ option.member_count }} members
              </option>
            </select>
          </label>
          <label>
            <span>Reason</span>
            <textarea v-model="overrideReason" rows="2" data-test="override-reason"
                      placeholder="Why is another team taking this order?"></textarea>
          </label>
          <p v-if="overrideError" class="smj-team-card__warning" role="alert">{{ overrideError }}</p>
          <div class="smj-team-override__actions">
            <button type="button" class="rug-button" data-test="override-apply"
                    @click="applyOverride">Use this team</button>
            <button type="button" @click="cancelOverride">Cancel</button>
          </div>
        </template>
      </section>

      <div class="priority-sales-layout">
        <section class="rug-section-card smj-catalogue">
          <header>
            <div><h2>Product catalogue</h2><p>Live ERPNext prices and warehouse availability.</p></div>
            <span class="rug-value-badge">{{ data?.items?.length || 0 }} results</span>
          </header>
          <div v-if="!customerSelected" class="smj-catalogue-lock" role="status">
            <SmjSalesCartPulse size="22" decorative />
            <strong>Select a customer to begin the order</strong>
            <span>Products, prices and the cart unlock once a customer is chosen.</span>
          </div>
          <div class="priority-sales-controls smj-catalogue-filters">
            <label><span>Search products</span><input v-model="search" type="search" placeholder="Item code, name, group or brand…" @input="schedule" /></label>
            <label><span>Item Group</span><select v-model="group"><option value="">All groups</option><option v-for="value in data?.item_groups || []" :key="value">{{ value }}</option></select></label>
          </div>
          <div v-if="loading" class="rug-skeleton"><i v-for="n in 8" :key="n" /></div>
          <div v-else-if="!data?.items?.length" class="rug-empty"><SmjInventoryCubeLayers size="28" decorative /><h2>No products found</h2><p>Change the search, group or warehouse.</p></div>
          <div v-else class="priority-product-grid">
            <!-- The card carries the image carousel, whose arrows are buttons of
                 their own, so the card itself cannot also be a button. It keeps the
                 click-anywhere-to-add behaviour through the role and key handlers,
                 and `add` refuses an out-of-stock or customerless click regardless. -->
            <article
              v-for="item in data.items"
              :key="item.item_code"
              class="smj-product-card"
              :class="{ 'is-out': outOfStock(item), 'is-locked': !customerSelected }"
              role="button"
              :tabindex="!customerSelected || outOfStock(item) ? -1 : 0"
              :aria-disabled="!customerSelected || outOfStock(item)"
              @click="add(item)"
              @keydown.enter.prevent="add(item)"
              @keydown.space.prevent="add(item)"
            >
              <span v-if="outOfStock(item)" class="smj-stock-badge smj-stock-badge--out">Out of Stock</span>
              <ProductImageCarousel
                v-if="productImages(item).length"
                class="smj-product-images"
                :images="productImages(item)"
                :alt="item.item_name"
                isolate
              />
              <span v-else class="priority-product-placeholder"><SmjInventoryCubeLayers size="26" decorative /></span>
              <strong>{{ item.item_name }}</strong>
              <small>{{ item.item_code }} · {{ item.item_group }}</small>
              <b>{{ data.currency }} {{ Number(item.rate || 0).toFixed(2) }}</b>
              <em>{{ Number(item.available_to_sell ?? item.actual_qty ?? 0) }} {{ item.stock_uom }} available</em>
              <span class="smj-stock-triplet">
                <small>Actual <b>{{ Number(item.actual_qty ?? 0) }}</b></small>
                <small>Reserved <b>{{ Number(item.reserved_qty ?? 0) }}</b></small>
              </span>
              <!-- Carton size is shown for reference only. Wholesale customers may
                   order below a full carton, so this never gates the order. -->
              <small v-if="Number(item.carton_qty || 0) > 1" class="smj-carton-note">
                Carton = {{ Number(item.carton_qty) }} {{ item.stock_uom }}
              </small>
              <span class="smj-product-add">{{ outOfStock(item) ? "Unavailable" : "+ Add to cart" }}</span>
            </article>
          </div>
        </section>

        <aside class="rug-section-card priority-cart">
          <header>
            <div><h2>Cart</h2><p>{{ cartRows.length }} product lines · {{ cartQuantity }} units{{ repricing ? " · repricing…" : "" }}</p></div>
            <SmjSalesCartPulse size="22" decorative />
          </header>
          <div v-if="!cartRows.length" class="smj-cart-empty">
            <SmjSalesCartPulse size="30" decorative />
            <strong>Your cart is empty</strong>
            <span>{{ customerSelected ? "Select products from the catalogue." : "Select a customer first." }}</span>
          </div>
          <article v-for="row in cartRows" :key="row.item_code">
            <div>
              <strong>{{ row.item_name }}</strong>
              <small>{{ row.item_code }}</small>
              <b>{{ data?.currency }} {{ Number(row.rate || 0).toFixed(2) }}</b>
              <em v-if="row.source" class="smj-cart-source">{{ sourceLabels[row.source] || row.source }}</em>
            </div>
            <label><span class="sr-only">Quantity for {{ row.item_name }}</span><input v-model.number="row.qty" type="number" min="0.001" step="0.001" @change="repriceCart" /></label>
            <button type="button" :aria-label="`Remove ${row.item_name}`" @click="delete cart[row.item_code]"><SmjClose size="14" decorative /></button>
          </article>
          <footer>
            <span>Estimated total</span>
            <strong>{{ data?.currency }} {{ total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</strong>
          </footer>
          <button class="smj-cart-submit" type="button" :disabled="saving || !customerSelected || !data?.can_create_sales_order || !cartRows.length" @click="save">
            {{ saving ? "Creating order…" : "Create Draft Sales Order" }}
          </button>
        </aside>
      </div>
    </main>
  </PageContainer>
</template>
