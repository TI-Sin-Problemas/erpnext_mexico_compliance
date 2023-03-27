"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""
from erpnext.accounts.doctype.sales_invoice import sales_invoice
from frappe import _


class SalesInvoice(sales_invoice.SalesInvoice):
    """ERPNext Sales Invoice override"""

    def get_sat_payment_method(self):
        """Returns SAT Payment method code"""
        return self.sat_payment_method.split("-")[0].strip()

    def get_invoice_service_dates(self) -> str:
        """Returns invoice dates as a formatted string"""
        start_date = _("From {}").format(self.from_date) if self.from_date else None
        end_date = _("To {}").format(self.to_date) if self.to_date else None
        return f"{start_date} {end_date}".strip()
