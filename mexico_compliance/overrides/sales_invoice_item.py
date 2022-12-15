"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""
import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice_item import sales_invoice_item


class SalesInvoiceItem(sales_invoice_item.SalesInvoiceItem):
    """ERPNext Sales Invoice Item override"""

    def before_validate(self):
        """Add missing fields before validation"""
        if self.item_code:
            item = frappe.get_doc("Item", self.item_code)
            self.sat_product_or_service_key = item.sat_product_or_service_key

    def get_item(self):
        """Returns related Item DocType if any"""
        if not self.item_code:
            return None
        return frappe.get_doc("Item", self.item_code)

    def get_service_duration(self):
        """Returns a string with From and To dates of services"""
        start_date = ""
        if self.service_start_date:
            start_date = _("From {}").format(self.service_start_date)

        end_date = ""
        if self.service_end_date:
            start_date = _("To {}").format(self.service_end_date)

        return f"{start_date} {end_date}".strip()

    def get_cfdi_description(self):
        """Returns description ready to stamp a CFDI"""
        description = f"{self.item_name}"
        if all([self.description, self.item_name != self.description]):
            description += f" - {self.description}"

        service_dates = self.get_service_duration()
        if service_dates:
            description += f" ({service_dates})"

        return description.strip()
