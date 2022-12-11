"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""
import re
import frappe
from frappe import _
from erpnext.selling.doctype.customer.customer import Customer as ERPNextCustomer


class Customer(ERPNextCustomer):
    """ERPNext Customer override"""

    def validate_mexican_tax_id(self):
        """Validate customer name for SAT compliance"""
        exp = "^[A-ZÑ&]{3,4}[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])(?:[A-Z\d]{3})$"
        pattern = re.compile(exp)
        if not re.match(pattern, self.tax_id):
            frappe.throw(
                _("Tax Id does not comply with SAT specifications"),
                title=_("Invalid Tax Id"),
            )

    def get_customer_primary_address(self):
        """Get customer primary address document"""
        return frappe.get_doc("Address", self.customer_primary_address)

    @frappe.whitelist()
    def is_mexican(self):
        """Return True if primary address is in Mexico"""
        if not self.customer_primary_address:
            return False

        address = self.get_customer_primary_address()
        return address.country.upper().startswith("MEX")

    def validate(self):
        if self.tax_id and self.is_mexican():
            self.tax_id = self.tax_id.upper()
            self.validate_mexican_tax_id()

        return super().validate()
