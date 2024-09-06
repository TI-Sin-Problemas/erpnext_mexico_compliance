"""
Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import frappe
from erpnext.setup.doctype.employee.employee import Employee as ERPNextEmployee
from frappe import _

from ..controllers import validators


class Employee(ERPNextEmployee):

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        mx_second_last_name: DF.Data
        mx_rfc: DF.Data

    def set_employee_name(self):
        super().set_employee_name()
        self.employee_name += " " + self.mx_second_last_name

    def validate_rfc(self):
        """Validate the RFC of the Employee.

        This function checks if the RFC of the Employee complies with the SAT specifications.
        If the RFC does not comply, it throws an error with a corresponding message.

        Raises:
            frappe.ValidationError: If the RFC does not comply with the SAT specifications.
        """
        if not validators.is_valid_rfc(self.mx_rfc):
            msg = _("RFC format does not comply with SAT specifications")
            frappe.throw(msg, title=_("Invalid RFC"))

    def validate(self):
        super().validate()

        if self.mx_rfc:
            self.validate_rfc()
