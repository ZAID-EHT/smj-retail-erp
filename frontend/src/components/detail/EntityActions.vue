<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createMappedEntity, executeEntityAction, getEntityActions, getMappedEntityPreview } from "@/services/entityActions.js";
import { confirmAction } from "@/composables/confirm.js";
import { useToast } from "@/composables/toast.js";
const props = defineProps({ entityKey: { type: String, required: true }, document: { type: Object, required: true } });
const emit = defineEmits(["refresh"]); const route = useRoute(); const router = useRouter(); const toast = useToast();
const data = ref(null); const error = ref(null); const busy = ref(false); const preview = ref(null); let controller;
const labels = { sales_invoice: "Sales Invoice", payment_entry: "Payment Entry", return: "Return" };
async function load() { controller?.abort(); controller = new AbortController(); error.value = null; try { data.value = await getEntityActions(props.entityKey, props.document.name, controller.signal); } catch (e) { if (e.name !== "AbortError") error.value = e; } }
watch(() => props.document.modified, load, { immediate: true }); onBeforeUnmount(() => controller?.abort());
async function action(key) {
  if (busy.value) return;
  const text = key.replaceAll("_", " ");
  const label = `${text[0].toUpperCase()}${text.slice(1)}`;
  const confirmed = await confirmAction({ title: `${label} this document?`, confirmLabel: label, danger: key === "cancel" || key === "delete" });
  if (!confirmed) return;
  busy.value = true;
  try {
    const result = await executeEntityAction(props.entityKey, props.document.name, key, props.document.modified, {});
    toast.success(`${label} complete`, "The document was updated.");
    if (result.route && result.route !== route.path) await router.push(result.route);
    emit("refresh");
    await load();
  } catch (e) {
    error.value = e;
    toast.error("Action failed", e.message);
  } finally { busy.value = false; }
}
async function map(target) { if (busy.value) return; busy.value = true; try { preview.value = await getMappedEntityPreview(props.entityKey, props.document.name, target, null, props.document.modified); } catch (e) { error.value = e; } finally { busy.value = false; } }
async function createMap() { if (busy.value || !preview.value) return; busy.value = true; try { const selected = preview.value.items.map((item) => ({ name: item.source_row, qty: Number(item.transfer_qty) })); const result = await createMappedEntity(props.entityKey, props.document.name, preview.value.target, selected, props.document.modified, crypto.randomUUID()); preview.value = null; await router.push(result.route); } catch (e) { error.value = e; } finally { busy.value = false; } }
function print(format, pdf = false) { const query = new URLSearchParams({ doctype: data.value.doctype, name: props.document.name, format, no_letterhead: "0" }); window.open(pdf ? `/api/method/frappe.utils.print_format.download_pdf?${query}` : `/printview?${query}`, "_blank", "noopener"); }
</script>
<template><section v-if="data || error" class="ref-so-actions"><header><div><span class="ref-entity-page__eyebrow">DOCUMENT LIFECYCLE</span><h2>Actions</h2></div><span v-if="busy" class="ref-status-badge" data-status="blue">Working…</span></header><p v-if="error" class="ref-action-error">{{ error.message }}</p><div v-if="data" class="ref-so-actions__buttons"><button v-for="entry in data.actions" :key="entry.key" class="ref-button" :class="entry.key === 'submit' ? 'ref-button--primary' : entry.key.startsWith('create_') ? 'ref-button--green' : 'ref-button--secondary'" :disabled="busy" @click="entry.key.startsWith('create_') ? map(entry.key.replace(/^create_/, '')) : action(entry.key)">{{ entry.label }}</button><template v-if="data.print?.can_print"><button v-for="format in data.print.formats" :key="format.name" class="ref-button ref-button--secondary" :disabled="busy" @click="print(format.name)">Print {{ format.label }}</button><button class="ref-button ref-button--secondary" :disabled="busy" @click="print(data.print.formats[0]?.name || 'Standard', true)">Download PDF</button></template></div><div v-if="preview" class="ref-preview-modal" role="dialog" aria-modal="true"><div class="ref-preview-modal__backdrop" @click="preview = null"/><section><header><div><span class="ref-entity-page__eyebrow">MAPPED DOCUMENT PREVIEW</span><h2>{{ labels[preview.target] || preview.target_doctype }}</h2><p>{{ preview.source }} · {{ preview.customer }}</p></div><button type="button" @click="preview = null">×</button></header><div class="ref-preview-items"><label v-for="item in preview.items" :key="item.source_row"><strong>{{ item.item_name || item.item_code }}</strong><small>Available {{ item.remaining_qty ?? item.transfer_qty }} · Warehouse {{ item.warehouse || '—' }}</small><input v-model.number="item.transfer_qty" type="number" min="0.0001" :max="item.remaining_qty || undefined" step="any" /></label></div><footer><strong>{{ preview.currency }} {{ Number(preview.totals?.grand_total || 0).toLocaleString() }}</strong><button class="ref-button ref-button--secondary" type="button" :disabled="busy" @click="preview = null">Back</button><button class="ref-button ref-button--primary" type="button" :disabled="busy" @click="createMap">Create Draft</button></footer></section></div></section></template>
