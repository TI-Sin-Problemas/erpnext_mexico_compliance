"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""
# import frappe
from frappe.model.document import Document


class SATTaxRegime(Document):
    """SAT's Tax System"""

    def before_save(self):
        """Set DocType key name"""
        self.key_name = f"{self.key} - {self.description}"[:140]
