"""
Scheduled tasks for ERPNext Mexico Compliance App

Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import frappe

from erpnext_mexico_compliance.overrides.payment_entry import PaymentEntry
from erpnext_mexico_compliance.overrides.sales_invoice import SalesInvoice


def check_cancellation_status():
	"""Checks the cancellation status of Sales Invoices and Payment Entries."""
	invoices = frappe.get_all(
		"Sales Invoice",
		fields=["name"],
		filters={
			"cancellation_acknowledgement": ["is", "not set"],
			"docstatus": 1,
		},
	)
	payments = frappe.get_all(
		"Payment Entry",
		fields=["name"],
		filters={
			"cancellation_acknowledgement": ["is", "not set"],
			"docstatus": 1,
		},
	)

	for i in invoices:
		frappe.debug_log.append(f"Checking cancellation status for Sales Invoice: {i.name}")
		si: SalesInvoice = frappe.get_doc("Sales Invoice", i.name)
		si.update_cancellation_status()

	for p in payments:
		frappe.debug_log.append(f"Checking cancellation status for Payment Entry: {p.name}")
		pe: PaymentEntry = frappe.get_doc("Payment Entry", p.name)
		pe.update_cancellation_status()
