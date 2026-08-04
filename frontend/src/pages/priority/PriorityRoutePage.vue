<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ErrorState from "@/components/feedback/ErrorState.vue";
import PermissionDenied from "@/components/feedback/PermissionDenied.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import UniversalDetailPage from "@/pages/generated/UniversalDetailPage.vue";
import UniversalFormPage from "@/pages/generated/UniversalFormPage.vue";
import UniversalListPage from "@/pages/generated/UniversalListPage.vue";
import PriorityReportPage from "@/pages/priority/PriorityReportPage.vue";
import WholesaleTransactionsPage from "@/pages/priority/WholesaleTransactionsPage.vue";
import PaymentReconciliationPage from "@/pages/priority/PaymentReconciliationPage.vue";
import BankReconciliationPage from "@/pages/priority/BankReconciliationPage.vue";
import BankClearancePage from "@/pages/priority/BankClearancePage.vue";
import PeggedCurrenciesPage from "@/pages/priority/PeggedCurrenciesPage.vue";
import SalesFunnelPage from "@/pages/priority/SalesFunnelPage.vue";
import WarehouseCapacityPage from "@/pages/priority/WarehouseCapacityPage.vue";
import PriorityReportHubPage from "@/pages/priority/PriorityReportHubPage.vue";
import PrioritySpecialPage from "@/pages/priority/PrioritySpecialPage.vue";
import PriorityTreePage from "@/pages/priority/PriorityTreePage.vue";
import AccountsWorkspacePage from "@/pages/priority/AccountsWorkspacePage.vue";
import HendersonAnalysisPage from "@/pages/priority/HendersonAnalysisPage.vue";
import PrintFormatAdminPage from "@/pages/priority/PrintFormatAdminPage.vue";
import WarehouseStockPage from "@/pages/priority/WarehouseStockPage.vue";
import SalesTeamsPage from "@/pages/priority/SalesTeamsPage.vue";
import CommissionRegisterPage from "@/pages/priority/CommissionRegisterPage.vue";
import CommissionPolicyPage from "@/pages/priority/CommissionPolicyPage.vue";
import CommissionPeriodsPage from "@/pages/priority/CommissionPeriodsPage.vue";
import HistoricalCommissionReviewPage from "@/pages/priority/HistoricalCommissionReviewPage.vue";
import { getPriorityRouteDefinition } from "@/services/priority.js";

const route = useRoute();
const router = useRouter();
const definition = ref(null);
const error = ref(null);
let controller;
const recordName = computed(() => definition.value?.params?.name || "");

async function load() {
  controller?.abort();
  controller = new AbortController();
  definition.value = null;
  error.value = null;
  try {
    const result = await getPriorityRouteDefinition(route.path, controller.signal);
    if (result.redirect) {
      await router.replace(result.redirect);
      return;
    }
    definition.value = result;
  } catch (caught) {
    if (caught.name !== "AbortError") error.value = caught;
  }
}

watch(() => route.fullPath, load, { immediate: true });
onBeforeUnmount(() => controller?.abort());
</script>

<template>
  <PermissionDenied v-if="error?.permissionDenied" />
  <PageContainer v-else-if="error"><ErrorState title="Unable to load page" :message="error.message" @retry="load" /></PageContainer>
  <UniversalListPage v-else-if="definition?.component === 'entity' && definition.mode === 'list'" :feature-key="definition.feature" :base-path="definition.base_path" />
  <UniversalFormPage v-else-if="definition?.component === 'entity' && ['new', 'edit'].includes(definition.mode)" :feature-key="definition.feature" :base-path="definition.base_path" :record-name="recordName" :defaults="definition.defaults" />
  <UniversalDetailPage v-else-if="definition?.component === 'entity' && definition.mode === 'detail'" :feature-key="definition.feature" :base-path="definition.base_path" :record-name="recordName" />
  <PriorityTreePage v-else-if="definition?.component === 'tree'" :definition="definition" />
  <WholesaleTransactionsPage v-else-if="definition?.component === 'register'" />
  <AccountsWorkspacePage v-else-if="definition?.component === 'accounts_workspace'" />
  <HendersonAnalysisPage v-else-if="definition?.component === 'henderson_analysis'" />
  <PrintFormatAdminPage v-else-if="definition?.component === 'print_format_admin'" />
  <WarehouseStockPage v-else-if="definition?.component === 'warehouse_stock'" />
  <SalesTeamsPage v-else-if="definition?.component === 'sales_teams'" />
  <CommissionRegisterPage v-else-if="definition?.component === 'commission_register'" />
  <CommissionPolicyPage v-else-if="definition?.component === 'commission_policy'" />
  <CommissionPeriodsPage v-else-if="definition?.component === 'commission_periods'" />
  <HistoricalCommissionReviewPage v-else-if="definition?.component === 'commission_historical_review'" />
  <PaymentReconciliationPage v-else-if="definition?.component === 'payment_reconciliation'" />
  <BankReconciliationPage v-else-if="definition?.component === 'bank_reconciliation'" />
  <BankClearancePage v-else-if="definition?.component === 'bank_clearance'" />
  <PeggedCurrenciesPage v-else-if="definition?.component === 'pegged_currencies'" />
	<UniversalFormPage v-else-if="definition?.component === 'single'" :feature-key="definition.feature" :base-path="route.path" :record-name="definition.doctype" stay-on-save />
  <SalesFunnelPage v-else-if="definition?.component === 'sales_funnel'" />
  <WarehouseCapacityPage v-else-if="definition?.component === 'warehouse_capacity'" />
  <PriorityReportHubPage v-else-if="definition?.component === 'report_hub'" :group="definition.group" />
  <PriorityReportPage v-else-if="definition?.component === 'report'" :report-name="definition.report" />
  <PrioritySpecialPage v-else-if="definition?.component === 'special'" :definition="definition" />
  <PageContainer v-else><div class="rug-skeleton"><i v-for="n in 8" :key="n" /></div></PageContainer>
</template>
