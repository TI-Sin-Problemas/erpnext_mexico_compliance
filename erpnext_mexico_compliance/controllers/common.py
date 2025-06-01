"""
Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import abc

import frappe
from frappe import _
from frappe.client import attach_file
from frappe.model.document import Document
from frappe.model.naming import NamingSeries
from satcfdi.cfdi import CFDI
from satcfdi.create.cfd import cfdi40

from ..erpnext_mexico_compliance.doctype.digital_signing_certificate.digital_signing_certificate import (
    DigitalSigningCertificate,
)


class CommonController(Document):
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        name: DF.Data
        naming_series: DF.Data
        mx_stamped_xml: DF.HTMLEditor

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
    def send_stamp_request(self, certificate: str):
        """Sends a request to stamp the CFDI document with the provided digital signing certificate.
        Args:
            certificate (str): The name of the Digital Signing Certificate to use for stamping.
        """
        raise NotImplementedError("send_stamp_request method is not implemented")

    @frappe.whitelist()
    def attach_pdf(self) -> Document:
        """Attaches the CFDI PDF to the current document.

        This method generates a PDF file from the CFDI XML and attaches it to the current document.

        Returns:
            Document: The result of attaching the PDF file to the current document.
        """
        from satcfdi import render  # pylint: disable=import-outside-toplevel

        cfdi = cfdi40.CFDI.from_string(self.mx_stamped_xml.encode("utf-8"))
        file_name = f"{self.name}_CFDI.pdf"
        file_data = render.pdf_bytes(cfdi)
        return attach_file(file_name, file_data, self.doctype, self.name, is_private=1)

    @frappe.whitelist()
    def attach_xml(self) -> Document:
        """Attaches the CFDI XML to the current document.

        This method generates an XML file from the CFDI XML and attaches it to the current document.

        Returns:
            Document: The result of attaching the XML file to the current document.
        """
        file_name = f"{self.name}_CFDI.xml"
        xml = self.mx_stamped_xml
        return attach_file(file_name, xml, self.doctype, self.name, is_private=1)

    @frappe.whitelist()
    def stamp_cfdi(self, certificate: str):
        """Stamps a CFDI document with the provided digital signing certificate.

        Args:
            certificate (str): The name of the Digital Signing Certificate to use for signing.

        Returns:
            CFDI: A message indicating the result of the stamping operation.
        """
        self.run_method("before_stamp_cfdi")
        self.send_stamp_request(certificate)
        self.run_method("after_stamp_cfdi")
        self.run_method("before_attach_files")
        self.run_method("before_attach_pdf")
        self.attach_pdf()
        self.run_method("after_attach_pdf")
        self.run_method("before_attach_xml")
        self.attach_xml()
        self.run_method("after_attach_xml")
        self.run_method("after_attach_files")
        frappe.msgprint(_("CFDI Stamped Successfully"), indicator="green", alert=True)
