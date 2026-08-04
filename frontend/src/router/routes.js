import ModuleDashboardPage from "@/pages/priority/ModuleDashboardPage.vue";
import HomeDashboardPage from "@/pages/priority/HomeDashboardPage.vue";
import PriorityReportHubPage from "@/pages/priority/PriorityReportHubPage.vue";
import SmartSalesPage from "@/pages/priority/SmartSalesPage.vue";
import EntityDetailPage from "@/pages/entities/EntityDetailPage.vue";
import EntityFormPage from "@/pages/entities/EntityFormPage.vue";
import MappedDocumentDetailPage from "@/pages/entities/MappedDocumentDetailPage.vue";
import EntityListPage from "@/pages/entities/EntityListPage.vue";
import FeatureUnavailablePage from "@/pages/FeatureUnavailablePage.vue";
import PermissionDeniedPage from "@/pages/PermissionDeniedPage.vue";
import NotFoundPage from "@/pages/NotFoundPage.vue";

export const moduleRoutes = [
  {
    path: "/home",
    name: "home",
    component: HomeDashboardPage,
    meta: { title: "Home", description: "Dashboard, metrics, alerts and quick actions.", accent: "blue", icon: "home" },
  },
  {
    path: "/smart-sales",
    name: "smart-sales",
    component: SmartSalesPage,
    meta: { title: "Smart Sales", description: "Retail catalogue, customer selection and guided sales workflow.", accent: "blue", icon: "cart" },
  },
  {
    path: "/sales",
    name: "sales",
    component: ModuleDashboardPage,
    meta: { title: "Sales", description: "Customers, quotations, orders, delivery notes and invoices.", accent: "green", icon: "sales" },
  },
  {
    path: "/purchases",
    name: "purchases",
    component: ModuleDashboardPage,
    meta: { title: "Purchases", description: "Suppliers, requests, orders, receipts and purchase invoices.", accent: "purple", icon: "bag" },
  },
  {
    path: "/inventory",
    name: "inventory",
    component: ModuleDashboardPage,
    meta: { title: "Inventory", description: "Products, warehouses, transfers, stock levels and traceability.", accent: "orange", icon: "box" },
  },
  {
    path: "/finance",
    name: "finance",
    component: ModuleDashboardPage,
    meta: { title: "Finance", description: "Accounting, payments, receivables, payables and financial reports.", accent: "gold", icon: "finance" },
  },
  {
    path: "/operations",
    name: "operations",
    component: ModuleDashboardPage,
    meta: { title: "Operations", description: "Assets, manufacturing, quality, projects and support.", accent: "turquoise", icon: "settings" },
  },
  {
    path: "/crm",
    name: "crm",
    component: ModuleDashboardPage,
    meta: { title: "CRM", description: "Leads, opportunities, contacts, campaigns and appointments.", accent: "pink", icon: "users" },
  },
  {
    path: "/reports",
    name: "reports",
    component: PriorityReportHubPage,
    meta: { title: "Reports", description: "Permission-aware operational and financial reporting.", accent: "dark-blue", icon: "chart" },
  },
  {
    path: "/admin",
    name: "admin",
    component: () => import("@/pages/priority/AdminLandingPage.vue"),
    meta: { title: "Administration", description: "Users, roles, companies, printing, email, data, finance and system tools.", accent: "purple", icon: "shield" },
  },
  // Two plain paths rather than one optional/regex param: an optional custom-regex
  // segment scores lower in vue-router's ranking than the
  // /:module(...|admin)/:pathMatch(.+) clean-route catch-all below, so the
  // catch-all swallowed these and rendered "Page not found". Verified in a real
  // browser. User/Role/Role Profile CRUD keeps its own canonical /admin routes
  // and is not duplicated here.
  {
    path: "/admin/access-control",
    name: "access-control",
    component: () => import("@/pages/priority/AccessControlPage.vue"),
    meta: { title: "Access Control", description: "Effective access, user permissions, roles and email delivery status.", accent: "purple", icon: "shield" },
  },
  {
    path: "/admin/access-control/:tab",
    name: "access-control-tab",
    component: () => import("@/pages/priority/AccessControlPage.vue"),
    meta: { title: "Access Control", description: "Effective access, user permissions, roles and email delivery status.", accent: "purple", icon: "shield" },
  },
  {
    path: "/admin/system",
    name: "system-operations",
    component: () => import("@/pages/priority/SystemOperationsPage.vue"),
    meta: { title: "System Operations", description: "Read-only health, readiness and backup status.", accent: "dark-blue", icon: "shield" },
  },
  {
    path: "/admin/system/:tab",
    name: "system-operations-tab",
    component: () => import("@/pages/priority/SystemOperationsPage.vue"),
    meta: { title: "System Operations", description: "Read-only health, readiness and backup status.", accent: "dark-blue", icon: "shield" },
  },
  {
    path: "/admin/data",
    name: "data-management",
    component: () => import("@/pages/priority/DataManagementPage.vue"),
    meta: { title: "Data Management", description: "Guided import and export of business records.", accent: "turquoise", icon: "box" },
  },
  {
    path: "/admin/data/:tab",
    name: "data-management-tab",
    component: () => import("@/pages/priority/DataManagementPage.vue"),
    meta: { title: "Data Management", description: "Guided import and export of business records.", accent: "turquoise", icon: "box" },
  },
  {
    path: "/setup",
    name: "setup-wizard",
    component: () => import("@/pages/priority/SetupWizardPage.vue"),
    meta: { title: "Setup", description: "First-time company setup.", accent: "blue", icon: "settings" },
  },
  {
    path: "/setup/:step",
    name: "setup-wizard-step",
    component: () => import("@/pages/priority/SetupWizardPage.vue"),
    meta: { title: "Setup", description: "First-time company setup.", accent: "blue", icon: "settings" },
  },
  {
    path: "/admin/email",
    name: "email-admin",
    component: () => import("@/pages/priority/EmailAdminPage.vue"),
    meta: { title: "Email & Notifications", description: "Email delivery status, templates and notifications.", accent: "gold", icon: "settings" },
  },
  {
    path: "/admin/email/:tab",
    name: "email-admin-tab",
    component: () => import("@/pages/priority/EmailAdminPage.vue"),
    meta: { title: "Email & Notifications", description: "Email delivery status, templates and notifications.", accent: "gold", icon: "settings" },
  },
  {
    path: "/admin/printing",
    name: "printing-admin",
    component: () => import("@/pages/priority/PrintingAdminPage.vue"),
    meta: { title: "Printing & Branding", description: "Letter heads, print formats and document preview.", accent: "purple", icon: "settings" },
  },
  {
    path: "/admin/printing/:tab",
    name: "printing-admin-tab",
    component: () => import("@/pages/priority/PrintingAdminPage.vue"),
    meta: { title: "Printing & Branding", description: "Letter heads, print formats and document preview.", accent: "purple", icon: "settings" },
  },
  {
    path: "/reports/scheduled",
    name: "scheduled-reports",
    component: () => import("@/pages/priority/ScheduledReportsPage.vue"),
    meta: { title: "Scheduled Reports", description: "Auto-email reports on a schedule.", accent: "dark-blue", icon: "chart" },
  },
  {
    path: "/admin/readiness",
    name: "launch-readiness",
    component: () => import("@/pages/priority/LaunchReadinessPage.vue"),
    meta: { title: "Launch Readiness", description: "Truthful go-live checklist.", accent: "gold", icon: "shield" },
  },
  {
    path: "/admin/finance/decisions",
    name: "accountant-decisions",
    component: () => import("@/pages/priority/AccountantDecisionsPage.vue"),
    meta: { title: "Accountant Decisions", description: "Finance decisions awaiting an accountant.", accent: "gold", icon: "shield" },
  },
  { path: "/feature-unavailable", name: "feature-unavailable", component: FeatureUnavailablePage, meta: { title: "Feature Unavailable", accent: "orange" } },
  { path: "/permission-denied", name: "permission-denied", component: PermissionDeniedPage, meta: { title: "Permission Denied", accent: "pink" } },
  { path: "/not-found", name: "not-found", component: NotFoundPage, meta: { title: "Page Not Found", accent: "orange" } },
];

export const entityRoutes = [
  {
    path: "/sales/customers",
    name: "customer-list",
    component: EntityListPage,
    meta: { title: "Customers", entityKey: "customers", accent: "green" },
  },
  {
    path: "/sales/customers/new",
    name: "customer-new",
    component: () => import("@/pages/entities/CustomerQuickForm.vue"),
    meta: { title: "New Customer", entityKey: "customers", accent: "green" },
  },
  {
    path: "/sales/customers/:name/edit",
    name: "customer-edit",
    component: () => import("@/pages/entities/CustomerQuickForm.vue"),
    meta: { title: "Edit Customer", entityKey: "customers", accent: "green" },
  },
  {
    path: "/sales/customers/:name",
    name: "customer-detail",
    component: EntityDetailPage,
    meta: { title: "Customer", entityKey: "customers", backRoute: "/sales/customers", accent: "green" },
  },
  {
    path: "/inventory/products",
    name: "item-list",
    component: EntityListPage,
    meta: { title: "Products", entityKey: "items", accent: "orange" },
  },
  {
    path: "/inventory/products/new",
    name: "item-new",
    component: () => import("@/pages/entities/ProductQuickForm.vue"),
    meta: { title: "New Product", entityKey: "items", accent: "orange" },
  },
  {
    path: "/inventory/products/:name/edit",
    name: "item-edit",
    component: () => import("@/pages/entities/ProductQuickForm.vue"),
    meta: { title: "Edit Product", entityKey: "items", accent: "orange" },
  },
  {
    path: "/inventory/products/:name",
    name: "item-detail",
    component: EntityDetailPage,
    meta: { title: "Product", entityKey: "items", backRoute: "/inventory/products", accent: "orange" },
  },
  {
    path: "/sales/delivery-notes",
    name: "delivery-note-list",
    component: EntityListPage,
    meta: { title: "Delivery Notes", entityKey: "delivery_notes", accent: "green" },
  },
  {
    path: "/sales/delivery-notes/new",
    name: "delivery-note-new",
    component: EntityFormPage,
    meta: { title: "New Delivery Note", entityKey: "delivery_notes", accent: "green" },
  },
  {
    path: "/sales/delivery-notes/:name/edit",
    name: "delivery-note-edit",
    component: EntityFormPage,
    meta: { title: "Edit Delivery Note", entityKey: "delivery_notes", accent: "green" },
  },
  {
    path: "/sales/delivery-notes/:name",
    name: "delivery-note-detail",
    component: MappedDocumentDetailPage,
    meta: { title: "Delivery Note", entityKey: "delivery_notes", accent: "green" },
  },
  {
    path: "/sales/invoices",
    name: "sales-invoice-list",
    component: EntityListPage,
    meta: { title: "Sales Invoices", entityKey: "sales_invoices", accent: "green" },
  },
  {
    path: "/sales/invoices/new",
    name: "sales-invoice-new",
    component: EntityFormPage,
    meta: { title: "New Sales Invoice", entityKey: "sales_invoices", accent: "green" },
  },
  {
    path: "/sales/invoices/:name/edit",
    name: "sales-invoice-edit",
    component: EntityFormPage,
    meta: { title: "Edit Sales Invoice", entityKey: "sales_invoices", accent: "green" },
  },
  {
    path: "/sales/invoices/:name",
    name: "sales-invoice-detail",
    component: MappedDocumentDetailPage,
    meta: { title: "Sales Invoice", entityKey: "sales_invoices", accent: "green" },
  },
  {
    path: "/finance/payments",
    name: "payment-entry-list",
    component: EntityListPage,
    meta: { title: "Payment Entries", entityKey: "payment_entries", accent: "gold" },
  },
  {
    path: "/finance/payments/new",
    name: "payment-entry-new",
    component: EntityFormPage,
    meta: { title: "New Payment Entry", entityKey: "payment_entries", accent: "gold" },
  },
  {
    path: "/finance/payments/:name/edit",
    name: "payment-entry-edit",
    component: EntityFormPage,
    meta: { title: "Edit Payment Entry", entityKey: "payment_entries", accent: "gold" },
  },
  {
    path: "/finance/payments/:name",
    name: "payment-entry-detail",
    component: MappedDocumentDetailPage,
    meta: { title: "Payment Entry", entityKey: "payment_entries", accent: "gold" },
  },
  {
    path: "/sales/orders",
    name: "sales-order-list",
    component: EntityListPage,
    meta: { title: "Sales Orders", entityKey: "sales_orders", accent: "green" },
  },
  {
    path: "/sales/orders/new",
    name: "sales-order-new",
    component: EntityFormPage,
    meta: { title: "New Sales Order", entityKey: "sales_orders", accent: "green" },
  },
  {
    path: "/sales/orders/:name/edit",
    name: "sales-order-edit",
    component: EntityFormPage,
    meta: { title: "Edit Sales Order", entityKey: "sales_orders", accent: "green" },
  },
  {
    path: "/sales/orders/:name",
    name: "sales-order-detail",
    component: EntityDetailPage,
    meta: { title: "Sales Order", entityKey: "sales_orders", backRoute: "/sales/orders", accent: "green" },
  },
];

// Generated routes are deliberately registered after handcrafted routes.
// The server-owned feature registry decides whether the feature is allowlisted.
export const generatedRoutes = [
  { path: "/generated/:feature", name: "generated-list", component: () => import("@/pages/generated/UniversalListPage.vue"), meta: { title: "Generated List", accent: "turquoise" } },
  { path: "/generated/:feature/new", name: "generated-new", component: () => import("@/pages/generated/UniversalFormPage.vue"), meta: { title: "Generated Form", accent: "turquoise" } },
  { path: "/generated/:feature/:name/edit", name: "generated-edit", component: () => import("@/pages/generated/UniversalFormPage.vue"), meta: { title: "Generated Form", accent: "turquoise" } },
  { path: "/generated/:feature/:name", name: "generated-detail", component: () => import("@/pages/generated/UniversalDetailPage.vue"), meta: { title: "Generated Detail", accent: "turquoise" } },
  // Henderson Analysis is a dedicated management page, not an ERPNext report, so it
  // must be matched before the /reports/:report catch-all treats it as a report name.
  { path: "/reports/henderson-analysis", name: "henderson-analysis", component: () => import("@/pages/priority/PriorityRoutePage.vue"), meta: { title: "Henderson Analysis", accent: "dark-blue" } },
  { path: "/reports/:report", name: "generated-report", component: () => import("@/pages/generated/UniversalReportPage.vue"), meta: { title: "Report", accent: "dark-blue" } },
  { path: "/views/:feature/:view", name: "generated-view", component: () => import("@/pages/generated/UniversalSpecialPage.vue"), meta: { title: "Special View", accent: "purple" } },
];

// Clean priority routes resolve through the server-owned registry. They are
// registered after handcrafted pages and before /generated compatibility URLs.
export const priorityRoutes = [
  { path: "/reports/view/:report", name: "priority-report-view", component: () => import("@/pages/priority/PriorityRoutePage.vue"), meta: { title: "Report", accent: "dark-blue" } },
  { path: "/reports/:group(sales|purchases|inventory|finance|crm|operations)", name: "priority-report-group", component: () => import("@/pages/priority/PriorityRoutePage.vue"), meta: { title: "Reports", accent: "dark-blue" } },
  { path: "/pos", name: "priority-pos", component: () => import("@/pages/priority/PriorityRoutePage.vue"), meta: { title: "Point of Sale", accent: "green" } },
  { path: "/:module(sales|purchases|inventory|finance|crm|operations|admin)/:pathMatch(.+)", name: "priority-clean-route", component: () => import("@/pages/priority/PriorityRoutePage.vue"), meta: { title: "Retail ERP", accent: "turquoise" } },
];

export const navigationModules = moduleRoutes
  .filter((route) => !["smart-sales", "feature-unavailable", "permission-denied", "not-found"].includes(route.name))
  .map((route) => ({
    name: route.name,
    label: route.meta.title,
    path: route.path,
    accent: route.meta.accent,
    icon: route.meta.icon,
  }));
