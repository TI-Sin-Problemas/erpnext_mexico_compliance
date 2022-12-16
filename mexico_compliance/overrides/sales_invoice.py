"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""
from erpnext.accounts.doctype.sales_invoice import sales_invoice


class SalesInvoice(sales_invoice.SalesInvoice):
    """ERPNext Sales Invoice override"""

    def get_sat_payment_method(self):
        """Returns SAT Payment method code"""
        return self.sat_payment_method.split("-")[0].strip()
