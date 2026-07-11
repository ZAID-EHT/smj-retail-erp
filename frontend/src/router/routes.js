import PlaceholderPage from "@/pages/PlaceholderPage.vue";

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

export const navigationModules = moduleRoutes
  .filter((route) => route.name !== "smart-sales")
  .map((route) => ({
    name: route.name,
    label: route.meta.title,
    path: route.path,
    accent: route.meta.accent,
    icon: route.meta.icon,
  }));
