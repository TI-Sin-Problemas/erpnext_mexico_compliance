from enum import Enum

import frappe
from satcfdi.create.cfd.cfdi40 import CFDI
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport

from .exceptions import WSClientException


class WSClient:

    class OperationMode(Enum):
        PROD = "https://app.facturaloplus.com/ws/servicio.do?wsdl"
        TEST = "https://dev.facturaloplus.com/ws/servicio.do?wsdl"

    def __init__(self, api_key: str, mode: OperationMode = OperationMode.TEST) -> None:
        self.api_key = api_key
        self.client = Client(mode.value, transport=Transport(cache=SqliteCache()))
        self.logger = frappe.logger("erpnext_mexico_compliance.ws_client", True)

    def raise_from_code(self, code: str, message: str):
        """Raises a WSClientException if the given code is not 200.

        Args:
            code (str): The status code to check.
            message (str): The error message to raise.

        Raises:
            WSClientException: If the code is not 200.
        """
        if code != "200":
            self.logger.error({"code": code, "message": message})
            raise WSClientException(message, code)

    def stamp(self, cfdi: CFDI) -> tuple[str, str]:
        """Stamps a CFDI using the provided client and API key.

        Args:
            cfdi (CFDI): The CFDI to be stamped.

        Returns:
            tuple[str, str]: A tuple containing the stamped CFDI data and the corresponding message.

        Raises:
            WSClientException: If the stamping operation fails.
        """
        xml_cfdi = cfdi.xml_bytes().decode("utf-8")
        res = self.client.service.timbrar(apikey=self.api_key, xmlCFDI=xml_cfdi)
        self.logger.debug({"action": "stamp", "data": xml_cfdi})
        self.raise_from_code(res.code, res.message)
        return res.data, res.message

    def get_available_credits(self) -> int:
        """Retrieves the available credits from the CFDI Web Service.

        Returns:
            int: The number of available credits.
        """
        res = self.client.service.consultarCreditosDisponibles(apikey=self.api_key)
        self.raise_from_code(res.code, res.message)
        return res.data
