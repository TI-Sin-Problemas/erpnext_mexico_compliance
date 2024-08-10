# Copyright (c) 2024, TI Sin Problemas and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.file_manager import get_file
from satcfdi.exceptions import CFDIError
from satcfdi.models import Signer


class DigitalSigningCertificate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        certificate: DF.Attach | None
        company: DF.Link
        key: DF.Attach | None
        legal_name: DF.Data | None
        password: DF.Password | None
        rfc: DF.Data | None
    # end: auto-generated types

    def _get_file(self, field: str) -> bytes:
        return get_file(getattr(self, field))[1]

    def read_certificate(self) -> bytes:
        """Returns the content of the Digital Signing Certificate file

        Returns:
            bytes: Digital Signing Certificate content
        """
        if not self.certificate:
            frappe.throw(_("Certificate file not configured"))
        return self._get_file("certificate")

    def read_key(self) -> bytes:
        """Returns the content of the Digital Signing Certificate Key file

        Returns:
            bytes: Digital Signing Certificate Key content
        """
        if not self.key:
            frappe.throw(_("Key file not configured"))
        return self._get_file("key")

    def get_signer(self) -> Signer:
        """Returns a Signer object loaded with the certificate, key, and password of the current
        DigitalSigningCertificate instance.

        Returns:
            Signer: CSD Signer
        """
        certificate = self.read_certificate()
        key = self.read_key()
        password = self.get_password()
        try:
            signer = Signer.load(certificate=certificate, key=key, password=password)
        except (CFDIError, ValueError) as e:
            frappe.throw(msg=str(e), title="Invalid Signing Certificate")

        return signer

    @frappe.whitelist()
    def validate_certificate(self):
        """Validates the digital signing certificate by checking if the certificate files and
        password are correctly configured."""
        self.get_signer()
        msg = _("Certificate files and password are valid")
        frappe.msgprint(msg=msg, title=_("Success"), indicator="green")

    @property
    def triad_is_complete(self) -> bool:
        """Checks if the digital signing certificate triad is complete.

        The triad consists of the certificate, key, and password. This property returns True if
        all three are present, False otherwise.

        Returns:
            bool: Whether the triad is complete.
        """
        return all([self.certificate, self.key, self.password])

    @property
    def legal_name(self) -> str | None:
        """Returns the legal name associated with the digital signing certificate.

        Returns:
            str | None: The legal name associated with the digital signing certificate, or None if
            the triad is not complete.
        """
        return self.get_signer().legal_name if self.triad_is_complete else None

    @property
    def rfc(self) -> str | None:
        """Returns the RFC associated with the digital signing certificate.

        Returns:
            str | None: The RFC associated with the digital signing certificate, or None if the
            triad is not complete.
        """
        return self.get_signer().rfc if self.triad_is_complete else None
