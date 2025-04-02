# Copyright (c) 2024, TI Sin Problemas and contributors
# For license information, please see license.txt

import frappe
from erpnext_mexico_compliance import ws_client
from frappe import _
from frappe.model.document import Document


class CFDIStampingSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        api_key: DF.Data | None
        api_secret: DF.Password | None
        test_mode: DF.Check
    # end: auto-generated types

    def get_api_key(self) -> str:
        """Retrieves the API key from the CFDI Stamping Settings document.

        Returns:
            str: The API key.
        """
        return self.get_password("api_key")

    @property
    def available_credits(self) -> int:
        """Retrieves the available credits from the CFDI Web Service.

        Returns:
            int: The number of available credits.
        """
        if self.api_key:
            ws = ws_client.get_ws_client(self)
            try:
                available_credits = ws.get_available_credits()
            except ws_client.WSClientException as exception:
                frappe.throw(str(exception), title=_("CFDI Web Service Error"))
        else:
            available_credits = 0

        return available_credits
