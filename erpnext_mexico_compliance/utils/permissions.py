import frappe


def check_app_permission():
	roles = frappe.get_roles()
	allowed_roles = ["System Manager", "Accounts Manager"]

	if any(role in allowed_roles for role in roles):
		return True

	return False
