frappe.pages["smart-sales"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({ parent: wrapper, title: "Smart Sales", single_column: true });
	wrapper.smart_sales = new SmartSales(wrapper);
};

frappe.pages["smart-sales"].on_page_show = function (wrapper) {
	wrapper.smart_sales?.refresh();
};

class SmartSales {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.$main = $(wrapper).find(".layout-main-section");
		this.state = { cart: new Map(), page: 1, search: "", group: "", customer: null, warehouse: "", price_list: "" };
		this.debounce = null;
		this.render_shell();
		this.bind_events();
	}

	async refresh() {
		if (this.loading) return;
		this.loading = true;
		this.$main.addClass("ss-loading");
		try {
			const response = await frappe.call({
				method: "my_store_ui.api.get_bootstrap",
				args: {
					page: this.state.page,
					page_length: 24,
					search: this.state.search,
					item_group: this.state.group,
					warehouse: this.state.warehouse,
					price_list: this.state.price_list,
				},
				freeze: false,
			});
			this.data = response.message;
			this.state.price_list = this.data.price_list;
			if (!this.state.warehouse && this.data.warehouses.length) this.state.warehouse = this.data.warehouses[0];
			this.render_navigation();
			this.render_filters();
			this.render_products();
			this.render_cart();
		} catch (error) {
			this.$main.find(".ss-products").html(`<div class="ss-empty">${__("Unable to load products. Check your permissions and try again.")}</div>`);
		} finally {
			this.loading = false;
			this.$main.removeClass("ss-loading");
		}
	}

	render_shell() {
		$(this.wrapper).addClass("smart-sales-page");
		this.$main.html(`
			<div class="smart-sales-shell">
				<nav class="ss-nav"><a class="ss-brand" href="/app"><span>E</span><strong>ERPNext <small>v15</small></strong></a><button class="ss-menu-toggle">☰</button><div class="ss-nav-groups"></div><div class="ss-nav-actions"><button class="ss-search-command">⌕</button><button class="ss-bell">♢</button><button class="ss-avatar">${frappe.user.name.slice(0, 1).toUpperCase()}</button><button class="ss-logout">↪ ${__("Logout")}</button></div></nav>
				<div class="ss-toolbar"><button class="ss-all-products">▦ ${__("All Products")}</button><div class="ss-search"><span>⌕</span><input type="search" placeholder="${__("Search product, SKU, brand or description")}"></div><select class="ss-group"><option value="">${__("All Categories")}</option></select><select class="ss-warehouse"></select><select class="ss-price-list"></select><button class="ss-cart-pill">🛒 <span>${__("Cart")}</span> <b>0</b></button></div>
				<div class="ss-content">
					<main class="ss-catalogue">
						<section class="ss-hero"><div><p>${__("SMART RETAIL")}</p><h1>${__("ERPNext Smart Sales Interface")}</h1><h2>${__("Live products, prices and stock from ERPNext")}</h2><div class="ss-hero-tags"><span>▥ ${__("Real-time Stock")}</span><span>◇ ${__("Smart Pricing")}</span><span>ϟ ${__("Fast Orders")}</span><span>◎ ${__("LKR Ready")}</span></div></div><div class="ss-bags">♧</div></section>
						<section class="ss-customer"><div class="ss-customer-search">♙ <input placeholder="${__("Search or select customer")}"><button>⌄</button></div><div class="ss-customer-results"></div></section>
						<div class="ss-products"></div><button class="ss-load-more">${__("Load more")}</button>
					</main>
					<aside class="ss-cart"><div class="ss-cart-head"><div><small>${__("CURRENT CART")}</small><h3>${__("Draft Sales Order")}</h3></div><button class="ss-cart-close">×</button></div><div class="ss-order-note">ⓘ ${__("The order will be saved as Draft so it can be reviewed before confirmation.")}</div><div class="ss-cart-items"></div><div class="ss-totals"></div><button class="ss-generate">▣ ${__("Generate Draft Sales Order")}</button><button class="ss-invoice" disabled>✓ ${__("Create Final Invoice")}</button></aside>
				</div>
			</div>`);
	}

	bind_events() {
		this.$main.on("input", ".ss-search input", (event) => {
			clearTimeout(this.debounce);
			this.debounce = setTimeout(() => { this.state.search = event.target.value; this.state.page = 1; this.refresh(); }, 350);
		});
		this.$main.on("change", ".ss-group", (e) => { this.state.group = e.target.value; this.state.page = 1; this.refresh(); });
		this.$main.on("change", ".ss-warehouse", (e) => { this.state.warehouse = e.target.value; this.refresh(); });
		this.$main.on("change", ".ss-price-list", (e) => { this.state.price_list = e.target.value; this.refresh(); });
		this.$main.on("click", ".ss-all-products", () => { this.state.search = ""; this.state.group = ""; this.state.page = 1; this.$main.find(".ss-search input").val(""); this.refresh(); });
		this.$main.on("click", ".ss-product .ss-add", (e) => this.add_to_cart($(e.currentTarget).closest(".ss-product").data("code")));
		this.$main.on("click", ".ss-product [data-qty]", (e) => this.product_qty(e));
		this.$main.on("click", ".ss-cart-item [data-cart-qty]", (e) => this.cart_qty(e));
		this.$main.on("click", ".ss-remove", (e) => { this.state.cart.delete($(e.currentTarget).closest(".ss-cart-item").data("code")); this.render_cart(); });
		this.$main.on("input", ".ss-customer-search input", (e) => this.search_customers(e.target.value));
		this.$main.on("click", ".ss-customer-option", (e) => this.select_customer($(e.currentTarget).data("name"), $(e.currentTarget).data("label")));
		this.$main.on("click", ".ss-generate", () => this.generate_order());
		this.$main.on("click", ".ss-cart-pill, .ss-cart-close", () => this.$main.find(".ss-cart").toggleClass("open"));
		this.$main.on("click", ".ss-menu-toggle", () => this.$main.find(".ss-nav-groups").toggleClass("open"));
		this.$main.on("click", ".ss-nav-button", (e) => { const menu = $(e.currentTarget).next(); this.$main.find(".ss-dropdown").not(menu).removeClass("open"); menu.toggleClass("open"); });
		this.$main.on("click", ".ss-search-command", () => frappe.ui.toolbar.search.show());
		this.$main.on("click", ".ss-logout", () => frappe.app.logout());
	}

	render_navigation() {
		const groups = [{ label: __("Home"), color: "#087BC1", links: [{ label: __("Desk"), route: "/app" }] }, ...(this.data.navigation || [])];
		this.$main.find(".ss-nav-groups").html(groups.map(group => `<div class="ss-nav-group" style="--nav:${group.color}"><button class="ss-nav-button">${group.label} <span>⌄</span></button><div class="ss-dropdown">${group.links.map(link => `<a href="${link.route}">${link.label}</a>`).join("")}</div></div>`).join(""));
	}

	render_filters() {
		const option = (value, selected) => `<option value="${frappe.utils.escape_html(value)}" ${value === selected ? "selected" : ""}>${frappe.utils.escape_html(value)}</option>`;
		this.$main.find(".ss-group").html(`<option value="">${__("All Categories")}</option>${this.data.item_groups.map(x => option(x, this.state.group)).join("")}`);
		this.$main.find(".ss-warehouse").html(this.data.warehouses.map(x => option(x, this.state.warehouse)).join(""));
		this.$main.find(".ss-price-list").html(this.data.price_lists.map(x => option(x, this.state.price_list)).join(""));
	}

	render_products() {
		const currency = this.data.currency || "LKR";
		if (!this.data.items.length) { this.$main.find(".ss-products").html(`<div class="ss-empty">${__("No products matched your search.")}</div>`); return; }
		this.$main.find(".ss-products").html(this.data.items.map(item => {
			const image = item.image || "/assets/my_store_ui/images/product-placeholder.svg";
			const stock = flt(item.actual_qty);
			return `<article class="ss-product" data-code="${frappe.utils.escape_html(item.item_code)}" data-qty="1"><div class="ss-product-image"><img loading="lazy" src="${encodeURI(image)}" onerror="this.src='/assets/my_store_ui/images/product-placeholder.svg'"><span class="${stock > 0 ? "in" : "out"}">${stock > 0 ? __("In Stock") : __("Out of Stock")}</span></div><h3>${frappe.utils.escape_html(item.item_name || item.item_code)}</h3><p>${__("SKU")}: ${frappe.utils.escape_html(item.item_code)}</p><p>${frappe.utils.escape_html([item.brand, item.item_group].filter(Boolean).join(" · "))}</p><strong>${format_currency(item.rate, currency)}</strong><div class="ss-qty"><button data-qty="-1">−</button><span>1</span><button data-qty="1">+</button></div><button class="ss-add" ${stock <= 0 ? "disabled" : ""}>🛒 ${stock > 0 ? __("Add to Cart") : __("Out of Stock")}</button></article>`;
		}).join(""));
		this.$main.find(".ss-load-more").toggle(this.data.has_more);
	}

	product_qty(event) {
		const card = $(event.currentTarget).closest(".ss-product");
		const next = Math.max(1, cint(card.attr("data-qty")) + cint($(event.currentTarget).data("qty")));
		card.attr("data-qty", next).find(".ss-qty span").text(next);
	}

	add_to_cart(code) {
		const item = this.data.items.find(row => row.item_code === code);
		const card = this.$main.find(`.ss-product[data-code="${CSS.escape(code)}"]`);
		const qty = cint(card.attr("data-qty")) || 1;
		const current = this.state.cart.get(code);
		this.state.cart.set(code, { ...item, qty: (current?.qty || 0) + qty });
		this.render_cart();
		frappe.show_alert({ message: __("Added to cart"), indicator: "green" });
	}

	cart_qty(event) {
		const code = $(event.currentTarget).closest(".ss-cart-item").data("code");
		const item = this.state.cart.get(code);
		item.qty = Math.max(1, item.qty + cint($(event.currentTarget).data("cart-qty")));
		this.render_cart();
	}

	render_cart() {
		const currency = this.data?.currency || "LKR";
		const items = [...this.state.cart.values()];
		const totalQty = items.reduce((sum, item) => sum + item.qty, 0);
		const subtotal = items.reduce((sum, item) => sum + flt(item.rate) * item.qty, 0);
		this.$main.find(".ss-cart-pill b").text(totalQty);
		this.$main.find(".ss-cart-items").html(items.length ? items.map(item => `<div class="ss-cart-item" data-code="${frappe.utils.escape_html(item.item_code)}"><img src="${encodeURI(item.image || "/assets/my_store_ui/images/product-placeholder.svg")}"><div><h4>${frappe.utils.escape_html(item.item_name || item.item_code)}</h4><small>${__("SKU")}: ${frappe.utils.escape_html(item.item_code)}</small><div class="ss-mini-qty"><button data-cart-qty="-1">−</button><span>${item.qty}</span><button data-cart-qty="1">+</button></div></div><div class="ss-line"><button class="ss-remove">×</button><strong>${format_currency(item.rate * item.qty, currency)}</strong></div></div>`).join("") : `<div class="ss-empty ss-cart-empty">${__("Your cart is empty.")}<small>${__("Choose a product to get started.")}</small></div>`);
		this.$main.find(".ss-totals").html(`<div><span>${__("Products")} (${items.length})</span><b>${totalQty}</b></div><div><span>${__("Subtotal")}</span><b>${format_currency(subtotal, currency)}</b></div><div><span>${__("Tax")}</span><b>${__("Calculated by ERPNext")}</b></div><div class="ss-grand"><span>${__("Estimated Total")}</span><b>${format_currency(subtotal, currency)}</b></div>`);
		this.$main.find(".ss-generate").prop("disabled", !items.length || !this.state.customer || !this.data?.can_create_sales_order);
	}

	async search_customers(txt) {
		clearTimeout(this.customerDebounce);
		this.customerDebounce = setTimeout(async () => {
			const response = await frappe.call({ method: "my_store_ui.api.search_customers", args: { txt }, freeze: false });
			this.$main.find(".ss-customer-results").html(response.message.map(row => `<button class="ss-customer-option" data-name="${frappe.utils.escape_html(row.name)}" data-label="${frappe.utils.escape_html(row.customer_name)}"><b>${frappe.utils.escape_html(row.customer_name)}</b><small>${frappe.utils.escape_html(row.mobile_no || row.name)}</small></button>`).join("")).addClass("open");
		}, 250);
	}

	select_customer(name, label) {
		this.state.customer = name;
		this.$main.find(".ss-customer-search input").val(label).attr("readonly", true);
		this.$main.find(".ss-customer-results").removeClass("open").empty();
		this.render_cart();
	}

	async generate_order() {
		if (!this.state.customer || !this.state.cart.size) return;
		const button = this.$main.find(".ss-generate").prop("disabled", true);
		try {
			const response = await frappe.call({
				method: "my_store_ui.api.create_draft_sales_order",
				args: { payload: { request_id: frappe.utils.get_random(24), customer: this.state.customer, company: this.data.company, warehouse: this.state.warehouse, price_list: this.state.price_list, items: [...this.state.cart.values()].map(item => ({ item_code: item.item_code, qty: item.qty })) } },
				freeze: true,
				freeze_message: __("Creating draft Sales Order..."),
			});
			const result = response.message;
			frappe.msgprint({ title: __("Draft Sales Order created"), indicator: "green", message: `<a href="${result.route}"><strong>${frappe.utils.escape_html(result.name)}</strong></a><br>${__("Open it to review and edit before submission.")}` });
		} finally { button.prop("disabled", false); }
	}
}
