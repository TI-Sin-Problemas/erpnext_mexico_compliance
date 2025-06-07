"""
Scheduled tasks for ERPNext Mexico Compliance App

Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import frappe


def check_cancellation_status():
    """Checks the cancellation status of Sales Invoices and Payment Entries."""
    invoices = frappe.get_all(
        "Sales Invoice",
        fields=["name"],
        filters=[
            ["cancellation_acknowledgement", "!=", ""],
            ["docstatus", "=", 1],
        ],
    )
    payments = frappe.get_all(
        "Payment Entry",
        fields=["name"],
        filters=[
            ["cancellation_acknowledgement", "!=", ""],
            ["docstatus", "=", 1],
        ],
    )

    for i in invoices:
        doc = frappe.get_doc("Sales Invoice", i.name)
        doc.update_cancellation_status()

    for p in payments:
        doc = frappe.get_doc("Payment Entry", p.name)
        doc.update_cancellation_status()
