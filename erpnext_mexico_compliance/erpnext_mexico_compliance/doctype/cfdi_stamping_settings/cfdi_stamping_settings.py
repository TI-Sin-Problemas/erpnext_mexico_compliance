# Copyright (c) 2024, TI Sin Problemas and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.file_manager import get_file
from frappe.utils.password import get_decrypted_password
from satcfdi.exceptions import CFDIError
from satcfdi.models import Signer


class CFDIStampingSettings(Document):

    def _get_file(self, field: str) -> tuple[str, bytes]:
        return get_file(getattr(self, field))

    def get_certificate(self) -> bytes:
        """Returns the Digital Signing Certificate

        Returns:
            bytes: Digital Signing Certificate
        """
        if not self.signing_certificate:
            frappe.throw(_("Signing Certificate not configured"))
        return self._get_file("signing_certificate")[1]

    def get_key(self) -> bytes:
        """Returns the Digital Signing Certificate Key

        Returns:
            bytes: Digital Signing Certificate Key
        """
        if not self.signing_key:
            frappe.throw(_("Signing Key not configured"))
        return self._get_file("signing_key")[1]

    def get_certificate_password(self) -> str:
        """Returns the Digital Signing Certificate Key Password

        Returns:
            str: Password for the Digital Signing Certificate key
        """
        if not self.signing_password:
            frappe.throw(_("Signing Password not configured"))
        return get_decrypted_password(self.doctype, self.name, "signing_password")

    def get_csd_signer(self) -> Signer:
        """Returns Signer from the Digital Signing Certificate

        Returns:
            Signer: CSD Signer
        """
        certificate = self.get_certificate()
        key = self.get_key()
        password = self.get_certificate_password()
        try:
            signer = Signer.load(certificate=certificate, key=key, password=password)
        except (CFDIError, ValueError) as e:
            frappe.throw(title="Invalid Signing Certificate", msg=str(e))

        return signer

    @frappe.whitelist()
    def validate_signing_certificate(self):
        """Validate the CSD Signing Certificate"""
        self.get_csd_signer()
