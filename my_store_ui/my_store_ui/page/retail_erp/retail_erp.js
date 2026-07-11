frappe.pages["retail-erp"].on_page_load = function (wrapper) {
	document.body.classList.add("retail-erp-active");
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Retail ERP"),
		single_column: true,
	});

	$(wrapper).addClass("retail-erp-page");
	const mountTarget = document.createElement("div");
	mountTarget.className = "retail-erp-mount";
	$(wrapper).find(".layout-main-section").empty().append(mountTarget);

	frappe.require(
		[
			"/assets/my_store_ui/frontend/retail-erp.css",
			"/assets/my_store_ui/frontend/retail-erp.js",
		],
		() => {
			if (!window.RetailERPFrontend?.mount) {
				frappe.throw(__("Retail ERP frontend bundle could not be loaded."));
			}
			wrapper.retail_erp_app = window.RetailERPFrontend.mount(mountTarget, {
				frappe: window.frappe,
				__: window.__,
			});
		},
	);
};

frappe.pages["retail-erp"].on_page_show = function (wrapper) {
	document.body.classList.add("retail-erp-active");
	wrapper.retail_erp_app?.syncRoute?.();
};

frappe.pages["retail-erp"].on_page_hide = function (wrapper) {
	document.body.classList.remove("retail-erp-active");
	wrapper.retail_erp_app?.closeTransientUi?.();
};
