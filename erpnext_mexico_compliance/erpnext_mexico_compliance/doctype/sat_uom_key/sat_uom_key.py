# Copyright (c) 2022, Alfredo Altamirano and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SATUOMKey(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        description: DF.SmallText | None
        enabled: DF.Check
        key: DF.Data
        key_name: DF.Data | None
        uom_name: DF.Data
    # end: auto-generated types
    def before_save(self):
        """Set DocType Name"""
        self.key_name = f"{self.key} - {self.uom_name}"[:140]
