"""Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe
from erpnext_mexico_compliance import ws_client
from frappe import _
from frappe.model.document import Document


class CFDIStampingSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.cfdi_pdf_template.cfdi_pdf_template import (
            CFDIPDFTemplate,
        )
        from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.default_csd.default_csd import (
            DefaultCSD,
        )
        from frappe.types import DF

        api_key: DF.Data | None
        api_secret: DF.Password | None
        default_csds: DF.Table[DefaultCSD]
        pdf_templates: DF.Table[CFDIPDFTemplate]
        stamp_on_submit: DF.Check
        test_mode: DF.Check
    # end: auto-generated types

    def get_secret(self) -> str:
        """Retrieves the API secret.

        Returns:
            str: The API secret.
        """
        return self.get_password("api_secret")

    def get_token(self) -> str:
        """Retrieves the API token.

        Returns:
            str: The API token.
        """
        return f"{self.api_key}:{self.get_secret()}"

    @frappe.whitelist()
    def get_available_credits(self) -> int:
        """Retrieves the available credits from the CFDI Web Service.

        Returns:
            int: The number of available credits.
        """
        ws = ws_client.get_ws_client(self)
        return ws.get_available_credits()

    def _validate_children(self):
        """
        Validates that there are no duplicated PDF templates per company and document type.

        It checks all the PDF templates in the `pdf_templates` child table and
        throws an exception if there are any duplicates for the same company and
        document type.
        """
        existing_templates = set()
        for t in self.pdf_templates:
            value = (t.company, t.document_type)
            if value in existing_templates:
                frappe.throw(_("Duplicated PDF template for {} and {}").format(*value))
            existing_templates.add(value)

    def validate(self):
        """Validates the CFDI Stamping Settings."""
        self._validate_children()
