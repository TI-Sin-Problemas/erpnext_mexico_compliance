import frappe


def activate_auto_commit(func):
	"""Temporarily set auto_commit_on_many_writes to True."""

	def wrapper(*args, **kwargs):
		old = frappe.db.auto_commit_on_many_writes
		frappe.db.auto_commit_on_many_writes = True
		try:
			func(*args, **kwargs)
		finally:
			frappe.db.auto_commit_on_many_writes = old

	return wrapper
