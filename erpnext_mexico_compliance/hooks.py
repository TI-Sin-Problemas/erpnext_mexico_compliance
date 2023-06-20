from . import __version__ as app_version

app_name = "erpnext_mexico_compliance"
app_title = "ERPNext Mexico Compliance"
app_publisher = "TI Sin Problemas"
app_description = (
    "ERPNext app to serve as base to comply with Mexican Rules and Regulations"
)
app_email = "info@tisinproblemas.com"
app_license = "MIT"
required_apps = ["erpnext"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_mexico_compliance/css/erpnext_mexico_compliance.css"
# app_include_js = "/assets/erpnext_mexico_compliance/js/erpnext_mexico_compliance.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_mexico_compliance/css/erpnext_mexico_compliance.css"
# web_include_js = "/assets/erpnext_mexico_compliance/js/erpnext_mexico_compliance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_mexico_compliance/public/scss/website"

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
# 	"methods": "erpnext_mexico_compliance.utils.jinja_methods",
# 	"filters": "erpnext_mexico_compliance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erpnext_mexico_compliance.install.before_install"
# after_install = "erpnext_mexico_compliance.install.after_install"
after_sync = "erpnext_mexico_compliance.install.after_sync"

# Uninstallation
# ------------

# before_uninstall = "erpnext_mexico_compliance.uninstall.before_uninstall"
# after_uninstall = "erpnext_mexico_compliance.uninstall.after_uninstall"

# Migration
# ------------

# after_migrate = "erpnext_mexico_compliance.migrate.after_migrate"
# before_migrate = "erpnext_mexico_compliance.migrate.before_migrate"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_mexico_compliance.notifications.get_notification_config"

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

override_doctype_class = {
    "Customer": "erpnext_mexico_compliance.overrides.customer.Customer",
    "Sales Invoice": "erpnext_mexico_compliance.overrides.sales_invoice.SalesInvoice",
    "Sales Invoice Item": "erpnext_mexico_compliance.overrides.sales_invoice_item.SalesInvoiceItem",
}

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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_mexico_compliance.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_mexico_compliance.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_mexico_compliance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_mexico_compliance.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpnext_mexico_compliance.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "erpnext_mexico_compliance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_mexico_compliance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_mexico_compliance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


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
# 	"erpnext_mexico_compliance.auth.validate"
# ]

fixtures = [
    {"doctype": "Custom Field", "filters": [{"module": "ERPNext Mexico Compliance"}]},
    {
        "doctype": "Property Setter",
        "filters": [{"module": "ERPNext Mexico Compliance"}],
    },
]
