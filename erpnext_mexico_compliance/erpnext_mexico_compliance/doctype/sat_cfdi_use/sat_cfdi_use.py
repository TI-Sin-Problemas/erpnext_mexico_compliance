"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import frappe
from frappe import _
from frappe.model.document import Document


class SATCFDIUse(Document):
    """SAT's CFDI Use"""

    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.sat_cfdi_use_tax_regime.sat_cfdi_use_tax_regime import (
            SATCFDIUseTaxRegime,
        )

        description: DF.Data
        enabled: DF.Check
        key: DF.Data
        key_name: DF.Data | None
        tax_regimes: DF.Table[SATCFDIUseTaxRegime]
    # end: auto-generated types

    def before_save(self):
        """Set DocType key name"""
        self.key_name = f"{self.key} - {self.description}"[:140]

    def validate(self):
        """Validate if all tax_regimes are unique."""
        existing_tax_regimes = set()
        msgs = []
        for tr in self.tax_regimes:
            if tr.tax_regime in existing_tax_regimes:
                msg = _("Row {0}: Tax Regime {1} is duplicated").format(
                    tr.idx, tr.tax_regime
                )
                msgs.append(msg)
            existing_tax_regimes.add(tr.tax_regime)

        if len(msgs) > 0:
            frappe.throw(msgs, title=_("Validation Error"), as_list=True)
