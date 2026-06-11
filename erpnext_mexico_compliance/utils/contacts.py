"""Copyright (c) 2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe


def get_all_billing_contacts_emails(customer: str) -> list[str]:
	"""Get all billing contacts emails for a given customer

	Args:
		customer (str): The name of the customer

	Returns:
		list[str]: A list of emails
	"""
	return frappe.get_all(
		"Contact",
		fields=["email_ids.email_id"],
		filters={
			"is_billing_contact": 1,
			"links.link_doctype": "Customer",
			"links.link_name": customer,
		},
		pluck="email_ids.email_id",
	)


def get_contact_emails(name: str) -> list[str]:
	"""Get all emails for a given contact

	Args:
		name (str): The name of the contact

	Returns:
		list[str]: A list of emails
	"""
	return frappe.get_all(
		"Contact",
		fields=["email_ids.email_id"],
		filters={"name": name},
		pluck="email_ids.email_id",
	)
