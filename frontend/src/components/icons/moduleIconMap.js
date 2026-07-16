import SmjAdminShieldKey from "./SmjAdminShieldKey.vue";
import SmjCrmPeopleLink from "./SmjCrmPeopleLink.vue";
import SmjFinanceWalletLedger from "./SmjFinanceWalletLedger.vue";
import SmjHomeBuilding from "./SmjHomeBuilding.vue";
import SmjInventoryCubeLayers from "./SmjInventoryCubeLayers.vue";
import SmjOperationsGearFlow from "./SmjOperationsGearFlow.vue";
import SmjPurchaseBagArrow from "./SmjPurchaseBagArrow.vue";
import SmjReportsBarsSpark from "./SmjReportsBarsSpark.vue";
import SmjSalesCartPulse from "./SmjSalesCartPulse.vue";

// Maps the route meta.icon string (already present on every module route)
// to its SMJ icon component, so the module navigation gets real iconography
// without any change to the route registry.
export const moduleIconMap = {
  home: SmjHomeBuilding,
  cart: SmjSalesCartPulse,
  sales: SmjSalesCartPulse,
  bag: SmjPurchaseBagArrow,
  box: SmjInventoryCubeLayers,
  finance: SmjFinanceWalletLedger,
  settings: SmjOperationsGearFlow,
  users: SmjCrmPeopleLink,
  chart: SmjReportsBarsSpark,
  shield: SmjAdminShieldKey,
};

export function moduleIcon(name) {
  return moduleIconMap[name] || SmjHomeBuilding;
}
