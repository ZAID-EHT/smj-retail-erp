import PlaceholderPage from "@/pages/PlaceholderPage.vue";
import EntityDetailPage from "@/pages/entities/EntityDetailPage.vue";
import EntityFormPage from "@/pages/entities/EntityFormPage.vue";
import EntityListPage from "@/pages/entities/EntityListPage.vue";

export const moduleRoutes = [
  {
    path: "/home",
    name: "home",
    component: PlaceholderPage,
    meta: { title: "Home", description: "Dashboard, metrics, alerts and quick actions.", accent: "blue", icon: "home" },
  },
  {
    path: "/smart-sales",
    name: "smart-sales",
    component: PlaceholderPage,
    meta: { title: "Smart Sales", description: "Retail catalogue, customer selection and guided sales workflow.", accent: "blue", icon: "cart" },
  },
  {
    path: "/sales",
    name: "sales",
    component: PlaceholderPage,
    meta: { title: "Sales", description: "Customers, quotations, orders, delivery notes and invoices.", accent: "blue", icon: "sales" },
  },
  {
    path: "/purchases",
    name: "purchases",
    component: PlaceholderPage,
    meta: { title: "Purchases", description: "Suppliers, requests, orders, receipts and purchase invoices.", accent: "orange", icon: "bag" },
  },
  {
    path: "/inventory",
    name: "inventory",
    component: PlaceholderPage,
    meta: { title: "Inventory", description: "Products, warehouses, transfers, stock levels and traceability.", accent: "green", icon: "box" },
  },
  {
    path: "/finance",
    name: "finance",
    component: PlaceholderPage,
    meta: { title: "Finance", description: "Accounting, payments, receivables, payables and financial reports.", accent: "purple", icon: "finance" },
  },
  {
    path: "/operations",
    name: "operations",
    component: PlaceholderPage,
    meta: { title: "Operations", description: "Assets, manufacturing, quality, projects and support.", accent: "turquoise", icon: "settings" },
  },
  {
    path: "/crm",
    name: "crm",
    component: PlaceholderPage,
    meta: { title: "CRM", description: "Leads, opportunities, contacts, campaigns and appointments.", accent: "pink", icon: "users" },
  },
  {
    path: "/reports",
    name: "reports",
    component: PlaceholderPage,
    meta: { title: "Reports", description: "Permission-aware operational and financial reporting.", accent: "dark-blue", icon: "chart" },
  },
  {
    path: "/admin",
    name: "admin",
    component: PlaceholderPage,
    meta: { title: "Admin", description: "Users, roles, companies, integrations and system tools.", accent: "purple", icon: "shield" },
  },
];

export const entityRoutes = [
  {
    path: "/sales/customers",
    name: "customer-list",
    component: EntityListPage,
    meta: { title: "Customers", entityKey: "customers", accent: "blue" },
  },
  {
    path: "/sales/customers/new",
    name: "customer-new",
    component: EntityFormPage,
    meta: { title: "New Customer", entityKey: "customers", accent: "blue" },
  },
  {
    path: "/sales/customers/:name/edit",
    name: "customer-edit",
    component: EntityFormPage,
    meta: { title: "Edit Customer", entityKey: "customers", accent: "blue" },
  },
  {
    path: "/sales/customers/:name",
    name: "customer-detail",
    component: EntityDetailPage,
    meta: { title: "Customer", entityKey: "customers", backRoute: "/sales/customers", accent: "blue" },
  },
  {
    path: "/inventory/products",
    name: "item-list",
    component: EntityListPage,
    meta: { title: "Products", entityKey: "items", accent: "green" },
  },
  {
    path: "/inventory/products/new",
    name: "item-new",
    component: EntityFormPage,
    meta: { title: "New Product", entityKey: "items", accent: "green" },
  },
  {
    path: "/inventory/products/:name/edit",
    name: "item-edit",
    component: EntityFormPage,
    meta: { title: "Edit Product", entityKey: "items", accent: "green" },
  },
  {
    path: "/inventory/products/:name",
    name: "item-detail",
    component: EntityDetailPage,
    meta: { title: "Product", entityKey: "items", backRoute: "/inventory/products", accent: "green" },
  },
  {
    path: "/sales/orders",
    name: "sales-order-list",
    component: EntityListPage,
    meta: { title: "Sales Orders", entityKey: "sales_orders", accent: "blue" },
  },
  {
    path: "/sales/orders/new",
    name: "sales-order-new",
    component: EntityFormPage,
    meta: { title: "New Sales Order", entityKey: "sales_orders", accent: "blue" },
  },
  {
    path: "/sales/orders/:name/edit",
    name: "sales-order-edit",
    component: EntityFormPage,
    meta: { title: "Edit Sales Order", entityKey: "sales_orders", accent: "blue" },
  },
  {
    path: "/sales/orders/:name",
    name: "sales-order-detail",
    component: EntityDetailPage,
    meta: { title: "Sales Order", entityKey: "sales_orders", backRoute: "/sales/orders", accent: "blue" },
  },
];

export const navigationModules = moduleRoutes
  .filter((route) => route.name !== "smart-sales")
  .map((route) => ({
    name: route.name,
    label: route.meta.title,
    path: route.path,
    accent: route.meta.accent,
    icon: route.meta.icon,
  }));
