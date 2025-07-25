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
        is_group: DF.Check
        key: DF.Data
        key_name: DF.Data | None
        lft: DF.Int
        old_parent: DF.Link | None
        parent_sat_product_or_service_key: DF.Link | None
        rgt: DF.Int
    # end: auto-generated types
    """SAT's Product or Service Key"""

    def before_save(self):
        """Set DocType key name"""
        self.key_name = f"{self.key} - {self.description}"[:140]
