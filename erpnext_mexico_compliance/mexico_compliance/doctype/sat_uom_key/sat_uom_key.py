# Copyright (c) 2022, Alfredo Altamirano and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SATUOMKey(Document):
    def before_save(self):
        """Set DocType Name"""
        self.key_name = f"{self.key} - {self.uom_name}"[:140]
