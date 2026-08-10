app_name = "bin_tracking"
app_title = "Bin Tracking"
app_publisher = "ERPNext"
app_description = "Warehouse bin tracking system with QR code and barcode support"
app_icon = "icon-qrcode"
app_color = "#3498db"
app_email = "admin@erpnext.com"
app_license = "MIT"
app_version = "0.0.1"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/bin_tracking/css/bin_tracking.css"
]
app_include_js = [
	"/assets/bin_tracking/js/bin_tracking.js"
]

# include custom scss in every page (without file extension ".scss")
# app_include_scss = "bin_tracking/public/scss/index"

# application home page (will override Website Settings)
# home_page = "index"

# website user home page (by default, will be "app/home")
# website_home_page = "app/home"

# Generators
# ----------

# automatically create page route for each document type
# website_generators = ["Web Template"]

# Provide support for Guest User
# ------ --------

# Ignore authentication on certain routes
# no_cache_on_routes = ["/api/method/run_doc_method"]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "index"

# website user home page (by default, will be "app/home")
# website_home_page = "app/home"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Warehouse": {
		"validate": "bin_tracking.warehouse_events.validate_warehouse",
		"on_update": "bin_tracking.warehouse_events.on_warehouse_update",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bin_tracking.tasks.all"
# 	],
# 	"daily": [
# 		"bin_tracking.tasks.daily"
# 	],
# 	"hourly": [
# 		"bin_tracking.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bin_tracking.tasks.weekly"
# 	],
# 	"monthly": [
# 		"bin_tracking.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "bin_tracking.install.before_tests"

# DocType Class
# ---------------
# Override standard DocType classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"before_insert": "method",
# 	}
# }

# Automated Tasks (called via scheduler)
# ---------------------------------------

# An example scheduled task
# scheduler_events = {
#	"cron": {
#		"0 0 * * *": "bin_tracking.tasks.task1"
#	},
#	"all": [
#		"bin_tracking.tasks.task2"
#	],
#	"daily": [
#		"bin_tracking.tasks.daily"
#	],
# }

# If you want to set up Log Based Audit
# audit_log_enabled_doctypes = [
# 	"Login",
# 	"User",
# ]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_field}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_field}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# ]

# Server-side Form Scripts
# -------------------------

# server_script_map = {
# 	"ToDo": "bin_tracking/public/py/todo.py",
# }

doctype_js = {
	"Item": "public/js/item.js",
	"Warehouse": "public/js/warehouse.js",
}

# Jinja filter
# -------

# jinja_filter_map = {
# 	"_abs": "_abs_custom"
# }

# Ctx Filter
# ----------

# Add custom context for jinja
# jinja_filter_map = {
# 	"abs": abs,
# }

# Context Processor
# -----------------

# Context processors to be run on every page load
website_context = {
	"favicon": "/assets/bin_tracking/images/icon.ico"
}

# Sitemap
# -------

# website_sitemap_fields = {
# 	"doctype_name": {
# 		"condition_field": "published",
# 		"date_field": "date",
# 		"route": "\/blog\/%(name)s"
# 	}
# }

# Website Generators
# ------------------

# website_generators = ["Web Template"]

# Other Installed Apps
# --------------------

# Dependencies on other apps
other_apps_installed = [
	"erpnext",
	"frappe",
]

# Override Home Page
# ------------------

# Home page override
# home_page = "Awesome Page"

# API Methods
# -----------

# api_methods = {
# 	"frappe.client.get": "bin_tracking.api.custom_get"
# }

# Fixtures
# --------

# Sync on every activate
# always_ensure_fixtures = ["Custom Field"]

# Sync fixtures on bench migrate
# fixtures = [
# 	"custom_field",
# 	"custom_script",
# ]

# Pages
# -----

# web_pages = ["page_1", "page_2"]

# Plugins
# -------

# Plugins to be loaded
# plugins = [
# 	"bin_tracking/public/js/bin_tracking.js"
# ]
