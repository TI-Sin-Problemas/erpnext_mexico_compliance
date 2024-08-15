"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""
# import frappe
from frappe.model.document import Document


class SATTaxRegime(Document):
    """SAT's Tax Regime"""
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

    def before_save(self):
        """Set DocType key name"""
        self.key_name = f"{self.key} - {self.description}"[:140]
