"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""
import frappe
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
