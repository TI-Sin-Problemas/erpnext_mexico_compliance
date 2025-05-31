"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""

from enum import Enum

import frappe
import requests
from frappe import _
from satcfdi.cfdi import CFDI

from . import auth


class OperationMode(Enum):
    """Represents the operation mode of the CFDI Web Service."""

    PROD = "https://tisinproblemas.com"
    TEST = "https://cfdi.tisp-staging.com"


class WSClient:
    """Represents a CFDI Web Service client."""

    response: requests.Response
    endpoints = {
        "cancel": "/api/method/stamp_provider.api.v1.cancel",
        "status": "/api/method/stamp_provider.api.v1.status",
        "quota": "/api/method/stamp_provider.api.v1.quota",
        "stamp": "/api/method/stamp_provider.api.v1.stamp",
    }

    def __init__(self, token: str, mode: OperationMode = OperationMode.TEST) -> None:
        self.session = requests.Session()
        self.session.auth = auth.TokenAuth(token)
        self.url = mode.value
        self.logger = frappe.logger("erpnext_mexico_compliance.ws_client", True)

    def _get_uri(self, method: str) -> str:
        """Returns the URI for the given method.

        Args:
            method (str): The method for which to get the URI.

        Returns:
            str: The URI for the given method.
        """
        return f"{self.url}{self.endpoints[method]}"

    def _get_message(self):
        """Extracts and returns the 'message' field from the JSON response.

        Returns:
            str: The message extracted from the JSON response.
        """
        return self.response.json()["message"]

    def log_error(self, include_data: bool = False) -> None:
        """Logs an error message with optional data.

        Args:
            include_data (bool, optional): Whether to include the response data in the error
            message. Defaults to False.

        This function logs an error message using the logger object. The error message includes the
        response code and message. If the `include_data` parameter is set to True, the response data
        is also included in the error message.
        """
        msg = {"code": self.response.code, "message": self.response.message}
        if include_data:
            msg["data"] = self.response.data
        self.logger.error(msg)

    def raise_from_code(self):
        """Raises a WSClientException if the given code is not 200.

        Raises:
            WSClientException: If the given code is not 200.
            WSExistingCfdiException: If the given code is 307.
        """
        if self.response.ok:
            return

        self.logger.error(
            {"status": self.response.status_code, "message": self.response.text}
        )
        try:
            res = self.response.json()
        except requests.JSONDecodeError:
            res = {"exception": self.response.text}
        msg = res.get("exception", "")
        exc_type = res.get("exc_type", "")
        if exc_type:
            msg = msg.split(exc_type + ":")[1].strip()
        frappe.throw(msg, title=_("CFDI Web Service Error"))

    def stamp(self, cfdi: CFDI) -> str:
        """Stamps the provided CFDI.

        Args:
            cfdi (CFDI): The CFDI to be stamped.

        Returns:
            str: The stamped CFDI XML.
        """
        xml_cfdi = cfdi.xml_bytes().decode("utf-8")
        self.response = self.session.post(
            self._get_uri("stamp"), data={"xml": xml_cfdi}
        )
        self.logger.debug({"action": "stamp", "data": xml_cfdi})
        self.raise_from_code()
        message = self._get_message()
        return message["xml"]

    def cancel(
        self,
        signing_certificate: str,
        cfdi: CFDI,
        reason: str,
        substitute_uuid: str = None,
    ) -> str:
        """Cancels a CFDI using the provided signing certificate, CFDI, reason, and optional
        substitute UUID.

        Args:
            signing_certificate (str): The name of the Digital Signing Certificate DocType to use
                for cancellation.
            cfdi (CFDI): The CFDI to be cancelled.
            reason (str): The reason for cancellation.
            substitute_uuid (str, optional): The substitute UUID for cancellation. Defaults to None.

        Returns:
            str: The cancellation acknowledgement xml.
        """
        csd = frappe.get_doc("Digital Signing Certificate", signing_certificate)
        data = {
            "key": csd.get_key_b64(),
            "cer": csd.get_certificate_b64(),
            "password": csd.get_password(),
            "uuid": cfdi["Complemento"]["TimbreFiscalDigital"]["UUID"],
            "issuer_rfc": cfdi["Emisor"]["Rfc"],
            "receiver_rfc": cfdi["Receptor"]["Rfc"],
            "total": cfdi["Total"],
            "cancellation_reason": reason,
            "substitute_uuid": substitute_uuid,
        }
        self.response = self.session.post(self._get_uri("cancel"), data=data)
        self.logger.debug(
            {
                "action": "cancel",
                "signing_certificate": signing_certificate,
                "cfdi": cfdi,
                "reason": reason,
                "substitute_uuid": substitute_uuid,
            }
        )
        self.raise_from_code()
        msg = self._get_message()
        return msg["acknowledgement"]

    def get_available_credits(self) -> int:
        """Retrieves the available credits from the CFDI Web Service.

        Returns:
            int: The number of available credits.
        """
        self.response = self.session.get(self._get_uri("quota"), timeout=60)
        self.raise_from_code()
        return self._get_message()["available"]
