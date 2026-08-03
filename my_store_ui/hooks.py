app_name = "my_store_ui"
app_title = "My Store UI"
app_publisher = "SMJ"
app_description = "Upgrade-safe retail sales interface for ERPNext"
app_email = "zaidhnajeeb98@gmail.com"
app_license = "mit"

required_apps = ["erpnext"]

# Keep Retail ERP metadata customisations upgrade-safe and version controlled.
# This app owns only the explicitly named Item fields below.
fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["dt", "=", "Item"], ["fieldname", "in", [
			"custom_product_material", "custom_product_size", "custom_product_colour",
			"custom_published", "custom_supplier",
			"custom_purchase_price", "custom_additional_cost", "custom_total_cost",
			"custom_retail_profit_percentage", "custom_wholesale_profit_percentage",
			"custom_retail_price", "custom_wholesale_price", "custom_sku_prefix",
			"custom_sku", "custom_image_2", "custom_carton_qty", "custom_margin",
			"custom_stock_location_1", "custom_stock_location_2",
			"custom_stock_location_3",
		]]],
	},
	{
		"dt": "Custom Field",
		"filters": [["dt", "=", "Customer"], ["fieldname", "in", [
			"custom_credit_type", "custom_whatsapp_no", "custom_accounts_department_no",
			"custom_transport_method", "custom_transport_detail", "custom_br_no",
			"custom_business_nature", "custom_credit_days",
		]]],
	},
	{
		"dt": "Custom Field",
		"filters": [
			["dt", "in", ["Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry"]],
			["fieldname", "=", "custom_wholesale_transaction_id"],
		],
	},
]

# The stylesheet is deliberately scoped to .smart-sales-shell so standard
# ERPNext pages keep their native appearance.
app_include_css = ["/assets/my_store_ui/css/smart_sales.css"]

# Standalone Retail ERP website shell. Rules are prefix-scoped and cannot
# intercept APIs, assets, files, print/PDF, webhooks or other website routes.
home_page = "retail_erp"
website_route_rules = [
	{"from_route": "/retail-erp", "to_route": "retail_erp"},
	{"from_route": "/retail-erp/<path:app_path>", "to_route": "retail_erp"},
]
before_request = ["my_store_ui.route_guard.before_request"]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "my_store_ui",
# 		"logo": "/assets/my_store_ui/logo.png",
# 		"title": "My Store UI",
# 		"route": "/my_store_ui",
# 		"has_permission": "my_store_ui.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/my_store_ui/css/my_store_ui.css"
# app_include_js = "/assets/my_store_ui/js/my_store_ui.js"

# include js, css files in header of web template
# web_include_css = "/assets/my_store_ui/css/my_store_ui.css"
# web_include_js = "/assets/my_store_ui/js/my_store_ui.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "my_store_ui/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "my_store_ui/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "my_store_ui.utils.jinja_methods",
# 	"filters": "my_store_ui.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "my_store_ui.install.before_install"
# after_install = "my_store_ui.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "my_store_ui.uninstall.before_uninstall"
# after_uninstall = "my_store_ui.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "my_store_ui.utils.before_app_install"
# after_app_install = "my_store_ui.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "my_store_ui.utils.before_app_uninstall"
# after_app_uninstall = "my_store_ui.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "my_store_ui.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Shared Wholesale Transaction ID stamping/propagation. Each handler is a no-op
# when the custom_wholesale_transaction_id field is absent, so this is safe on
# any site (including before the fixture is applied).
doc_events = {
	"Sales Order": {
		"validate": [
			"my_store_ui.wholesale.transaction_id.assign_to_sales_order",
			# Freezes the customer's sales team onto the order at creation. It is
			# never re-read afterwards, so reassigning the customer later cannot
			# rewrite an order that already exists.
			"my_store_ui.sales_team.stamp_sales_document",
		],
	},
	"Delivery Note": {
		"validate": [
			"my_store_ui.wholesale.transaction_id.propagate_from_source",
			"my_store_ui.sales_team.stamp_sales_document",
		],
	},
	"Sales Invoice": {
		"validate": [
			"my_store_ui.wholesale.transaction_id.propagate_from_source",
			"my_store_ui.sales_team.stamp_sales_document",
		],
	},
	"Payment Entry": {
		"validate": "my_store_ui.wholesale.transaction_id.propagate_payment_entry",
	},
}

# Scheduled Tasks
# ---------------

# Release stock reservations past the configurable expiry window (default 3 days).
# No-op when reservation is disabled.
scheduler_events = {
	"daily": [
		"my_store_ui.wholesale.reservation.release_expired_reservations",
	],
}

# scheduler_events = {
# 	"all": [
# 		"my_store_ui.tasks.all"
# 	],
# 	"daily": [
# 		"my_store_ui.tasks.daily"
# 	],
# 	"hourly": [
# 		"my_store_ui.tasks.hourly"
# 	],
# 	"weekly": [
# 		"my_store_ui.tasks.weekly"
# 	],
# 	"monthly": [
# 		"my_store_ui.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "my_store_ui.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "my_store_ui.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "my_store_ui.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["my_store_ui.utils.before_request"]
# after_request = ["my_store_ui.utils.after_request"]

# Job Events
# ----------
# before_job = ["my_store_ui.utils.before_job"]
# after_job = ["my_store_ui.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"my_store_ui.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
