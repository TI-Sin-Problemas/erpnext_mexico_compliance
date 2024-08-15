"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""

# import frappe
from frappe.model.document import Document


class SATCFDIUse(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.sat_cfdi_use_tax_regime.sat_cfdi_use_tax_regime import SATCFDIUseTaxRegime
        from frappe.types import DF

        description: DF.Data
        enabled: DF.Check
        key: DF.Data
        key_name: DF.Data | None
        tax_regimes: DF.Table[SATCFDIUseTaxRegime]
    # end: auto-generated types
    """SAT's CFDI Use"""

    def before_save(self):
        """Set DocType key name"""
        self.key_name = f"{self.key} - {self.description}"[:140]
