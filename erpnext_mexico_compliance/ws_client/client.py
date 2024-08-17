from enum import Enum
from typing import Any

import frappe
from satcfdi.cfdi import CFDI
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport

from .exceptions import WSClientException, WSExistingCfdiException


class WSClient:
    """Represents a CFDI Web Service client."""

    response: Any

    class OperationMode(Enum):
        """Represents the operation mode of the CFDI Web Service."""

        PROD = "https://app.facturaloplus.com/ws/servicio.do?wsdl"
        TEST = "https://dev.facturaloplus.com/ws/servicio.do?wsdl"

    def __init__(self, api_key: str, mode: OperationMode = OperationMode.TEST) -> None:
        self.api_key = api_key
        self.client = Client(mode.value, transport=Transport(cache=SqliteCache()))
        self.logger = frappe.logger("erpnext_mexico_compliance.ws_client", True)

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
        res = self.response
        match res.code:
            case "200":
                return
            case "307":
                self.logger.error({"code": res.code, "message": res.message})
                raise WSExistingCfdiException(res.message, res.code, res.data)
            case _:
                self.logger.error({"code": res.code, "message": res.message})
                raise WSClientException(res.message, res.code)

    def stamp(self, cfdi: CFDI) -> tuple[str, str]:
        """Stamps a CFDI using the provided client and API key.

        Args:
            cfdi (CFDI): The CFDI to be stamped.

        Returns:
            tuple[str, str]: A tuple containing the stamped CFDI data and the corresponding message.

        Raises:
            WSExistingCfdiException: If the CFDI already exists.
            WSClientException: If the stamping operation fails.
        """
        xml_cfdi = cfdi.xml_bytes().decode("utf-8")
        self.response = self.client.service.timbrar(
            apikey=self.api_key, xmlCFDI=xml_cfdi
        )
        self.logger.debug({"action": "stamp", "data": xml_cfdi})
        self.raise_from_code()
        return self.response.data, self.response.message

        self.raise_from_code(res.code, res.message)
        return res.data, res.message

    def get_available_credits(self) -> int:
        """Retrieves the available credits from the CFDI Web Service.

        Returns:
            int: The number of available credits.
        """
        res = self.client.service.consultarCreditosDisponibles(apikey=self.api_key)
        self.response = res
        self.raise_from_code()
        return res.data
