import frappe
from erpnext_mexico_compliance.utils.cfdi import get_uuid_from_xml


def set_sales_invoices_uuid():
    """Sets the 'mx_uuid' field of all Sales Invoices with the UUID extracted from their
    'mx_stamped_xml' field."""
    query = frappe.qb.get_query(  # type: ignore
        "Sales Invoice",
        fields=["name", "mx_stamped_xml"],
        filters={"mx_stamped_xml": ["is", "set"]},
    )

    for name, xml in query.run():
        frappe.db.set_value("Sales Invoice", name, "mx_uuid", get_uuid_from_xml(xml))


def set_payment_entries_uuid():
    """Sets the 'mx_uuid' field of all Payment Entries with the UUID extracted from their
    'mx_stamped_xml' field."""
    query = frappe.qb.get_query(  # type: ignore
        "Payment Entry",
        fields=["name", "mx_stamped_xml"],
        filters={"mx_stamped_xml": ["is", "set"]},
    )

    for name, xml in query.run():
        frappe.db.set_value("Payment Entry", name, "mx_uuid", get_uuid_from_xml(xml))


def execute():
    """Sets the 'mx_uuid' field of all Sales Invoices and Payment Entries with the UUID extracted
    from their 'mx_stamped_xml' field."""
    set_sales_invoices_uuid()
    set_payment_entries_uuid()
