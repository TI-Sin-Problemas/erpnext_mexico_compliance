"""
Copyright (c) 2026, TI Sin Problemas and contributors
For license information, please see license.txt
"""

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from erpnext_mexico_compliance.overrides import sales_invoice

PORTAL_USER = "portal-sales-invoice@example.com"
# The permission is decided before the Company is looked up (Administrator is
# granted outright, a Website User is denied at doctype level), so the tests do
# not need a Company record.
COMPANY = "_Test Company MX"


def _portal_user() -> str:
	"""A Website User with the Customer role, like the ones that open /invoices."""
	if not frappe.db.exists("User", PORTAL_USER):
		frappe.get_doc(
			{
				"doctype": "User",
				"email": PORTAL_USER,
				"first_name": "Portal",
				"user_type": "Website User",
				"send_welcome_email": 0,
			}
		).insert(ignore_permissions=True)
	user = frappe.get_doc("User", PORTAL_USER)
	if "Customer" not in frappe.get_roles(PORTAL_USER):
		user.add_roles("Customer")
	return PORTAL_USER


class TestSalesInvoiceInPortalSession(IntegrationTestCase):
	"""Building a Sales Invoice must not need permission on Company."""

	def setUp(self):
		frappe.set_user("Administrator")
		self.user = _portal_user()

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_portal_user_can_build_a_sales_invoice_without_company(self):
		"""What `get_portal_row` does for every row of /invoices."""
		frappe.set_user(self.user)
		invoice = frappe.get_doc({"doctype": "Sales Invoice", "name": "SINV-PORTAL-ROW"})
		self.assertFalse(invoice.company_address)

	def test_portal_user_does_not_look_up_the_company_address(self):
		frappe.set_user(self.user)
		with patch.object(sales_invoice, "get_default_company_address") as lookup:
			invoice = frappe.get_doc({"doctype": "Sales Invoice", "company": COMPANY})
		lookup.assert_not_called()
		self.assertFalse(invoice.company_address)

	def test_a_user_who_can_read_the_company_still_gets_the_default_address(self):
		with patch.object(
			sales_invoice, "get_default_company_address", return_value="Main Address"
		) as lookup:
			invoice = frappe.get_doc({"doctype": "Sales Invoice", "company": COMPANY})
		lookup.assert_called_once_with(COMPANY)
		self.assertEqual(invoice.company_address, "Main Address")

	def test_an_existing_company_address_is_kept(self):
		with patch.object(sales_invoice, "get_default_company_address") as lookup:
			invoice = frappe.get_doc(
				{"doctype": "Sales Invoice", "company": COMPANY, "company_address": "Kept"}
			)
		lookup.assert_not_called()
		self.assertEqual(invoice.company_address, "Kept")
