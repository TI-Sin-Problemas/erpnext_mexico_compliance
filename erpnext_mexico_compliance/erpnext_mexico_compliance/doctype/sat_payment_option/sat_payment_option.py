# Copyright (c) 2024, TI Sin Problemas and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SATPaymentOption(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        description: DF.Data
        enabled: DF.Check
        key: DF.Data
        key_name: DF.Data | None
    # end: auto-generated types
    """SAT's Payment Option (Método de pago)"""

    def before_save(self):
        """Set DocType key name"""
        self.key_name = f"{self.key} - {self.description}"[:140]
