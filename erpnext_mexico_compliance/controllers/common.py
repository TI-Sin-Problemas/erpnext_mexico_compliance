"""
Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import abc

import frappe
from frappe.model.naming import NamingSeries
from satcfdi.cfdi import CFDI
from satcfdi.create.cfd import cfdi40

from ..erpnext_mexico_compliance.doctype.digital_signing_certificate.digital_signing_certificate import (
    DigitalSigningCertificate,
)


class CommonController(abc.ABC):
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        name: DF.Data
        naming_series: DF.Data

    @property
    def cfdi_series(self) -> str:
        """CFDI Series code"""
        prefix = str(NamingSeries(self.naming_series).get_prefix())
        return prefix if prefix[-1].isalnum() else prefix[:-1]

    @property
    def cfdi_folio(self) -> str:
        """CFDI Folio number"""
        prefix = str(NamingSeries(self.naming_series).get_prefix())
        return str(int(self.name.replace(prefix, "")))

    @abc.abstractmethod
    def get_cfdi_voucher(self, csd: DigitalSigningCertificate) -> cfdi40.Comprobante:
        """Generates a CFDI voucher using the provided digital signing certificate.

        Args:
            csd (DigitalSigningCertificate): The digital signing certificate.

        Returns:
            cfdi40.Comprobante: The generated CFDI voucher.
        """
        raise NotImplementedError("cfdi_voucher method is not implemented")

    def sign_cfdi(self, certificate: str) -> CFDI:
        """Signs a CFDI document with the provided digital signing certificate.

        Args:
            certificate (str): The name of the Digital Signing Certificate to use for signing.

        Returns:
            CFDI: The signed and processed CFDI document.
        """
        csd = frappe.get_doc("Digital Signing Certificate", certificate)
        voucher = self.get_cfdi_voucher(csd)
        voucher.sign(csd.signer)
        return voucher.process(True)

    @abc.abstractmethod
    def stamp_cfdi(self, certificate: str):
        """Stamps a CFDI document with the provided digital signing certificate.

        Args:
            certificate (str): The name of the Digital Signing Certificate to use for signing.

        Returns:
            CFDI: A message indicating the result of the stamping operation.
        """
        raise NotImplementedError("stamp_cfdi method is not implemented")
