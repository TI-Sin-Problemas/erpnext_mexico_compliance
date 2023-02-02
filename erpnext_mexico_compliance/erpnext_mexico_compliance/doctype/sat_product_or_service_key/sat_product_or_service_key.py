"""
Copyright (c) 2022, Alfredo Altamirano and contributors
For license information, please see license.txt
"""

# import frappe
from frappe.model.document import Document


class SATProductorServiceKey(Document):
    """SAT's Product or Service Key"""

    def before_save(self):
        """Set DocType key name"""
        self.key_name = f"{self.key} - {self.description}"[:140]
