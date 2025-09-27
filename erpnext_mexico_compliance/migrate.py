"""Migration tasks"""

import frappe

from .sat import update_sat_catalogs
from .utils.cfdi import get_uuid_from_xml


def set_sales_invoices_uuid():
    """Sets the 'mx_uuid' field of all Sales Invoices with the UUID extracted from their
    'mx_stamped_xml' field."""

    query = frappe.qb.get_query(  # type: ignore
        "Sales Invoice",
        fields=["name", "mx_stamped_xml"],
        filters={"mx_stamped_xml": ["is", "set"], "mx_uuid": ["is", "not set"]},
    )

    for name, xml in query.run():
        frappe.db.set_value("Sales Invoice", name, "mx_uuid", get_uuid_from_xml(xml))


def set_payment_entries_uuid():
    """Sets the 'mx_uuid' field of all Payment Entries with the UUID extracted from their
    'mx_stamped_xml' field."""
    query = frappe.qb.get_query(  # type: ignore
        "Payment Entry",
        fields=["name", "mx_stamped_xml"],
        filters={"mx_stamped_xml": ["is", "set"], "mx_uuid": ["is", "not set"]},
    )

    for name, xml in query.run():
        frappe.db.set_value("Payment Entry", name, "mx_uuid", get_uuid_from_xml(xml))


def enqueue_sat_catalogs_update():
    """Queues a task to update the SAT Catalogs for the current site."""
    print(f"Queued update of SAT Catalogs for {frappe.local.site}")
    frappe.enqueue(update_sat_catalogs, queue="long")
