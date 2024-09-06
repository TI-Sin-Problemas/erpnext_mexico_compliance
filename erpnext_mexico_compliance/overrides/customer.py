"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import frappe
from erpnext.selling.doctype.customer.customer import Customer as ERPNextCustomer
from frappe import _

from ..controllers.validators import is_valid_rfc


class Customer(ERPNextCustomer):
    """ERPNext Customer override"""

    @property
    def tax_id_is_rfc(self) -> bool:
        """True if tax id complies with RFC format"""
        return is_valid_rfc(self.tax_id)

    def validate_mexican_tax_id(self):
        """Validate customer name for SAT compliance"""
        if not self.tax_id_is_rfc:
            msg = _("Tax Id does not comply with SAT specifications")
            title = _("Invalid Tax Id")
            frappe.throw(msg, title=title)

    def get_primary_address(self):
        """Get customer primary address document"""
        return frappe.get_doc("Address", self.customer_primary_address)

    @property
    def is_mexican(self):
        """Return True if primary address is in Mexico"""
        if not self.customer_primary_address:
            return False

        address = self.get_primary_address()
        return address.country.upper().startswith("MEX")

    def validate(self):
        if self.is_mexican and self.tax_id:
            self.tax_id = self.tax_id.upper()
            self.validate_mexican_tax_id()

        return super().validate()
