# Copyright (c) 2022, Alfredo Altamirano and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SATUOMKey(Document):
    def autoname(self):
        """Set DocType Name"""
        self.name = f"{self.key} - {self.uom_name}"[:140]
