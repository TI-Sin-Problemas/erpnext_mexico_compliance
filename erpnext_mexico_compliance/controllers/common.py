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

from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.cfdi_stamping_settings.cfdi_stamping_settings import (
    CFDIStampingSettings,
)
from erpnext_mexico_compliance.utils import qr_as_base64

from ..erpnext_mexico_compliance.doctype.digital_signing_certificate.digital_signing_certificate import (
    DigitalSigningCertificate,
)
from ..ws_client import get_ws_client


class CommonController(Document):
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        naming_series: DF.Data
        mx_stamped_xml: DF.HTMLEditor
        mx_is_cancellable: DF.Check
        cancellation_reason: DF.Link
        cancellation_acknowledgement: DF.HTMLEditor

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

        self.run_method("before_attach_pdf")
        cfdi = cfdi40.CFDI.from_string(self.mx_stamped_xml.encode("utf-8"))
        file_name = f"{self.name}_CFDI.pdf"

        settings: CFDIStampingSettings = frappe.get_single("CFDI Stamping Settings")
        template = filter(
            lambda x: x.document_type == self.doctype and x.company == self.company,
            settings.pdf_templates,
        )
        template = list(template)

        if not settings.is_premium or len(template) == 0:
            from satcfdi import render

            file_data = render.pdf_bytes(cfdi)
        else:
            file_data = template[0].get_rendered_pdf(
                self.mx_stamped_xml, context={"doc": self}
            )

        ret = attach_file(file_name, file_data, self.doctype, self.name, is_private=1)
        self.run_method("after_attach_pdf")
        return ret

    @frappe.whitelist()
    def attach_xml(self) -> Document:
        """Attaches the CFDI XML to the current document.

        This method generates an XML file from the CFDI XML and attaches it to the current document.

        Returns:
            Document: The result of attaching the XML file to the current document.
        """
        self.run_method("before_attach_xml")
        file_name = f"{self.name}_CFDI.xml"
        xml = self.mx_stamped_xml
        ret = attach_file(file_name, xml, self.doctype, self.name, is_private=1)
        self.run_method("after_attach_xml")
        return ret

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
        self.attach_pdf()
        self.attach_xml()
        self.run_method("after_attach_files")
        frappe.msgprint(_("CFDI Stamped Successfully"), indicator="green", alert=True)

    def update_cancellation_status(self):
        """
        Updates the cancellation status of the CFDI associated with the document.

        This method uses a web service client to retrieve the current status of the CFDI.
        If the CFDI is determined to be not cancellable, it updates the document's
        'mx_is_cancellable' field to reflect this status and saves the document.
        If the CFDI is already cancelled, it cancels the document.

        Returns:
            Document: The result of the cancel operation if the CFDI is cancelled.
        """
        ws = get_ws_client()
        cfdi = CFDI.from_string(self.mx_stamped_xml.encode("utf-8"))
        status = ws.get_status(cfdi)
        if status.is_cancellable == status.CancellableStatus.NOT_CANCELLABLE:
            self.mx_is_cancellable = 0
            return self.save()

        if status.status == status.DocumentStatus.CANCELLED:
            return self.cancel()
        return None

    @frappe.whitelist()
    def check_cancellation_status(self):
        """
        Checks the current cancellation status of the CFDI associated with the document.

        This method uses a web service client to retrieve the current status of the CFDI.
        If the CFDI is cancelled, it calls the `update_cancellation_status` method to update
        the document's cancellation status and save the document.

        Returns:
            Document: The result of the cancel operation if the CFDI is cancelled.
        """
        client = get_ws_client()
        status = client.get_status(
            CFDI.from_string(self.mx_stamped_xml.encode("utf-8"))
        )
        title = status.status if isinstance(status.status, str) else status.status.value
        is_cancellable = status.is_cancellable.value if status.is_cancellable else None
        cancellation_status = (
            status.cancellation_status.value if status.cancellation_status else None
        )
        frappe.msgprint(
            msg=[
                _("CFDI Code: {0}").format(status.code),
                _("CFDI Status: {0}").format(title),
                _("Is Cancellable: {0}").format(is_cancellable),
                _("Cancellation Status: {0}").format(cancellation_status),
            ],
            title=title,
            as_list=True,
        )
        if status.status == status.DocumentStatus.CANCELLED:
            return self.update_cancellation_status()
        return None

    def validate_cancel_reason(self):
        """Validates whether a cancellation reason is provided before cancelling a Document.

        This function checks if a cancellation reason is set for the current Document.
        If no cancellation reason is found, it throws an error with a corresponding message.
        """
        if not self.cancellation_reason:
            msg = _("A Cancellation Reason is required.")
            title = _("Invalid Cancellation Reason")
            frappe.throw(msg, title=title)

    def validate_substitute_document(self, substitute_field: str):
        """Validates whether a substitute document is required for the cancellation reason.

        This function checks if the cancellation reason requires a substitute document
        and verifies if the substitute document is provided. If the cancellation reason
        requires a relationship and no substitute document is found, it throws an error
        with a corresponding message.

        Args:
            substitute_field (str): The field name of the substitute document.
        """

        reason = frappe.get_doc("Cancellation Reason", self.cancellation_reason)
        substitute_doc = getattr(self, substitute_field, None)
        substitute_field_label = _(self.meta.get_field(substitute_field).label)
        reason_field_label = _(self.meta.get_field("cancellation_reason").label)
        if reason.requires_relationship and not substitute_doc:
            msg = _("{} is required when {} is {}").format(
                substitute_field_label, reason_field_label, reason.description
            )
            frappe.throw(msg, title=_("{} is required").format(substitute_field_label))

    def _cancel_cfdi(self, certificate: str, substitute_field: str):
        """Cancels the CFDI document associated with the current document.

        This method uses a web service client to cancel the CFDI document associated
        with the current document. The cancellation request is sent with the
        cancellation reason and optional substitute document.

        Args:
            certificate (str): The name of the Digital Signing Certificate to use for cancellation.
            substitute_field (str): The field name of the substitute document.

        Returns:
            Document: The result of the save operation.
        """
        self.validate_cancel_reason()
        self.validate_substitute_document(substitute_field)

        cfdi = CFDI.from_string(self.mx_stamped_xml.encode("utf-8"))
        ws = get_ws_client()

        substitute_name = getattr(self, substitute_field)
        substitute_uuid = None
        if substitute_name:
            substitute = frappe.get_doc(self.doctype, self.substitute_payment_entry)
            substitute_uuid = substitute.cfdi_uuid

        self.cancellation_acknowledgement = ws.cancel(
            certificate, cfdi, self.cancellation_reason, substitute_uuid
        )

        ret = self.save()
        frappe.msgprint(
            _(
                "This Document will be cancelled once the CFDI cancellation request is approved"
            ),
            _("CFDI cancellation requested successfully"),
            indicator="green",
        )
        return ret

    @property
    def mx_cfdi_obj(self) -> CFDI:
        """Converts the stamped XML string to a CFDI object."""
        return CFDI.from_string(self.mx_stamped_xml.encode("utf-8"))

    @property
    def mx_cfdi_qr(self) -> str:
        """Generates a QR code from the CFDI verification URL and returns it in base64-encoded PNG
        format."""
        return qr_as_base64(self.mx_cfdi_obj.verifica_url)
