"""Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.caching import redis_cache

from erpnext_mexico_compliance import ws_client


class CFDIStampingSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.cfdi_pdf_template.cfdi_pdf_template import (
            CFDIPDFTemplate,
        )
        from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.default_csd.default_csd import (
            DefaultCSD,
        )

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

    @property
    def is_premium(self) -> bool:
        """Determines if the account is a premium subscriber.

        Checks if both the API key and API secret are set. If either is missing,
        the account is not considered premium. Otherwise, it verifies the premium
        status through an external check.

        Returns:
            bool: True if the account is premium, False otherwise.
        """
        if not self.api_key or not self.api_secret:
            return False
        return get_is_premium()


@redis_cache(ttl=43200)  # Cache for 12 hours
def get_is_premium() -> bool:
    """
    Checks if the current account has a valid premium subscription.

    It uses the Web Service client to retrieve the subscription details and
    checks if the subscription is valid. The result is cached for 12 hours.

    Returns:
        bool: True if the account has a valid premium subscription, False otherwise.
    """
    ws = ws_client.get_ws_client()
    subscription = ws.get_subscription_details()
    return subscription.has_subscription
