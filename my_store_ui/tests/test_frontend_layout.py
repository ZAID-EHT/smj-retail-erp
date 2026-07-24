from pathlib import Path
import unittest


class TestRetailERPScrolling(unittest.TestCase):
	def test_shared_shell_keeps_browser_page_scrolling_enabled(self):
		css = (Path(__file__).resolve().parents[2] / "frontend" / "src" / "design" / "base.css").read_text()
		self.assertNotIn("body.retail-erp-active { overflow: hidden", css)
		self.assertIn("overflow-y: auto", css)
		self.assertIn(".retail-erp-page .retail-erp-mount { min-height: 100vh; overflow: visible; }", css)
		self.assertIn(".ref-app-shell { min-height: 100vh; overflow: visible;", css)
		self.assertIn("overflow-y: visible", css)

	def test_dialogs_scroll_internally_without_body_scroll_lock(self):
		css = (Path(__file__).resolve().parents[2] / "frontend" / "src" / "design" / "base.css").read_text()
		self.assertIn("max-height: min(760px,calc(100vh - 40px)); overflow: auto", css)
		self.assertNotIn("body.modal-open", css)
		self.assertNotIn("body.scroll-lock", css)

	def test_smj_page_system_is_shared_and_loaded_last(self):
		frontend = Path(__file__).resolve().parents[2] / "frontend" / "src"
		main = (frontend / "main.js").read_text()
		styles = (frontend / "design" / "smj-page-system.css").read_text()
		container = (frontend / "components" / "layout" / "PageContainer.vue").read_text()
		self.assertIn('import "./design/smj-page-system.css";', main)
		self.assertGreater(main.index("smj-page-system.css"), main.index("priority-pages.css"))
		for selector in (
			".ref-entity-page__header",
			".ref-detail-header",
			".rug-banner",
			".ref-form-section",
			".rug-table-region",
			".smj-sales-kpis",
		):
			self.assertIn(selector, styles)
		self.assertIn(':data-accent="accent"', container)
		self.assertIn(':data-module="moduleName"', container)

	def test_shared_table_headers_start_at_the_top_of_the_table_region(self):
		styles = (Path(__file__).resolve().parents[2] / "frontend" / "src" / "design" / "smj-page-system.css").read_text()
		start = styles.index(".ref-data-table thead,")
		end = styles.index("\n}", start)
		table_header_rule = styles[start:end]
		self.assertIn("position: sticky", table_header_rule)
		self.assertIn("top: 0", table_header_rule)
		self.assertNotIn("var(--ref-header-height)", table_header_rule)

	def test_smart_sales_keeps_live_workflow_and_reference_stock_triplet(self):
		frontend = Path(__file__).resolve().parents[2] / "frontend" / "src"
		source = (frontend / "pages" / "priority" / "SmartSalesPage.vue").read_text()
		for marker in (
			"getSmartSales",
			"getCustomerCreditStatus",
			"createSmartOrder",
			"Actual stock shown",
			"Reserved stock",
			"Available to sell",
			"Create Draft Sales Order",
		):
			self.assertIn(marker, source)
		self.assertNotIn("ignore_permissions", source)

	def test_smart_sales_enforces_customer_first_and_stock_gating(self):
		frontend = Path(__file__).resolve().parents[2] / "frontend" / "src"
		source = (frontend / "pages" / "priority" / "SmartSalesPage.vue").read_text()
		# Customer-first: cart/add/submit gate on a selected customer.
		self.assertIn("customerSelected", source)
		self.assertIn("Select a customer to begin the order", source)
		# Add-to-cart and the submit button are disabled until a customer is chosen.
		self.assertIn(":disabled=\"!customerSelected || outOfStock(item)\"", source)
		# Zero-available stock is surfaced and blocked, not silently added.
		self.assertIn("Out of Stock", source)
		self.assertIn("outOfStock", source)
		# Cart reprices through the backend engine on customer change / add.
		self.assertIn("getCartPricing", source)
		self.assertIn("repriceCart", source)
		# The catalogue is priced against the customer's own price list.
		self.assertIn("customer_price_list", source)
		service = (frontend / "services" / "smartSales.js").read_text()
		self.assertIn("get_cart_pricing", service)

	def test_header_mounts_permission_aware_quick_create_menu(self):
		frontend = Path(__file__).resolve().parents[2] / "frontend" / "src"
		header = (frontend / "components" / "shell" / "AppHeader.vue").read_text()
		self.assertIn("QuickCreateMenu", header)
		menu = (frontend / "components" / "shell" / "QuickCreateMenu.vue").read_text()
		# Keyboard + dismissal behaviours are wired.
		for marker in ("getQuickCreateActions", "Escape", "ArrowDown", "ArrowUp", "role=\"menu\"", "Teleport"):
			self.assertIn(marker, menu)
		service = (frontend / "services" / "quickCreate.js").read_text()
		self.assertIn("get_quick_create_actions", service)

	def test_header_uses_compact_permission_filtered_module_menus(self):
		frontend = Path(__file__).resolve().parents[2] / "frontend" / "src"
		navigation = (frontend / "components" / "shell" / "ModuleNavigation.vue").read_text()
		header = (frontend / "components" / "shell" / "AppHeader.vue").read_text()
		styles = (frontend / "design" / "smj-page-system.css").read_text()
		for marker in (
			"primaryModuleNames",
			"linksFor(module)",
			"visibleLinks(module)",
			"linkSummary(link, module)",
			"showAllLinks",
			"Show fewer links",
			"Show all ${linksFor(module).length} links",
			"ref-module-dropdown__copy",
			"Only pages permitted for your account are shown",
		):
			self.assertIn(marker, navigation)
		self.assertNotIn("Ready to open", navigation)
		self.assertIn("SmjNotification", header)
		self.assertIn("SmjMessage", header)
		self.assertIn(".ref-module-dropdown__more", styles)
		self.assertIn(".ref-module-dropdown__copy", styles)
		self.assertIn(".ref-mobile-navigation__links", styles)
		self.assertIn(".ref-user-menu__copy", styles)

	def test_standalone_asset_error_remains_hidden_until_a_real_load_failure(self):
		frontend = Path(__file__).resolve().parents[2] / "frontend" / "src"
		styles = (frontend / "design" / "standalone.css").read_text()
		self.assertIn("#retail-erp-asset-error[hidden]", styles)
		self.assertIn("display: none !important", styles)
