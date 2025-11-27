"""
Copyright (c) 2022, Alfredo Altamirano and contributors
For license information, please see license.txt
"""

# import frappe
from frappe.model.document import Document


class SATProductorServiceKey(Document):
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
    """SAT's Product or Service Key"""

    def before_save(self):
        """Set DocType key name"""
        self.key_name = f"{self.key} - {self.description}"[:140]
