"""Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt"""

from erpnext_mexico_compliance import ws_client
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

    @property
    def available_credits(self) -> int:
        """Retrieves the available credits from the CFDI Web Service.

        Returns:
            int: The number of available credits.
        """
        if self.api_key and self.api_secret:
            ws = ws_client.get_ws_client(self)
            available_credits = ws.get_available_credits()
        else:
            available_credits = 0

        return available_credits
