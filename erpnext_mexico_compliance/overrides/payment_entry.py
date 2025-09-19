"""
Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import sys

import frappe
from erpnext.accounts.doctype.payment_entry import payment_entry
from erpnext.setup.doctype.company.company import get_default_company_address
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import get_datetime
from satcfdi.create.cfd import cfdi40, pago20
from satcfdi.exceptions import SchemaValidationError

from erpnext_mexico_compliance.utils import money_in_words
from erpnext_mexico_compliance.utils.cfdi import get_uuid_from_xml

from ..controllers.common import CommonController
from ..erpnext_mexico_compliance.doctype.cfdi_stamping_settings.cfdi_stamping_settings import (
    CFDIStampingSettings,
)
from ..erpnext_mexico_compliance.doctype.digital_signing_certificate.digital_signing_certificate import (
    DigitalSigningCertificate,
)
from ..ws_client import get_ws_client

# temporary hack until https://github.com/frappe/frappe/issues/27373 is fixed
if sys.path[0].rsplit("/", maxsplit=1)[-1] == "utils":
    sys.path[0] = sys.path[0].replace("apps/frappe/frappe/utils", "sites")


class PaymentEntry(CommonController, payment_entry.PaymentEntry):
    """ERPNext Payment Entry override"""

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        mx_payment_mode: DF.Data
        mx_stamped_xml: DF.HTMLEditor
        cancellation_reason: DF.Link
        substitute_payment_entry: DF.Link
        cancellation_acknowledgement: DF.HTMLEditor

    def on_submit(self):
        """
        Stamps the payment entry automatically if the
        CFDI Stamping Settings are configured to do so.

        If the CFDI Stamping Settings are configured to stamp the payment entry
        automatically, this method will stamp the payment entry with the first
        digital signing certificate that matches the company of the payment
        entry. If no matching certificate is found, the payment entry will not
        be stamped.
        """
        super().on_submit()
        settings: CFDIStampingSettings = frappe.get_single("CFDI Stamping Settings")
        payment_options = [
            doc.mx_payment_option if hasattr(doc, "mx_payment_option") else None
            for doc in self.get_reference_docs()
        ]
        conditions = [
            settings.stamp_on_submit,
            self.payment_type == "Receive",
            self.party_type == "Customer",
            all(i == "PPD" for i in payment_options),
        ]
        if all(conditions):
            csd = frappe.get_value("Default CSD", {"company": self.company}, "csd")
            # If stamping fails, do not block the submission of the payment entry
            try:
                self.stamp_cfdi(csd)
            except Exception as e:
                frappe.msgprint(str(e), title=_("CFDI Stamping Error"))

    @property
    def company_address(self) -> str:
        """Name of the default address of the Company associated with the current payment entry."""
        return get_default_company_address(self.company)

    @property
    def cfdi_receiver(self) -> cfdi40.Receptor:
        """`cfdi40.Receptor` object representing the receiver of the CFDI document for this payment
        entry."""
        customer = frappe.get_doc(self.party_type, self.party)
        address = frappe.get_doc("Address", customer.customer_primary_address)

        if not customer.mx_tax_regime:
            link = f'<a href="{customer.get_url()}">{customer.name}</a>'
            msg = _("Customer {0} has no tax regime").format(link)
            frappe.throw(msg)

        return cfdi40.Receptor(
            rfc=customer.tax_id,
            nombre=customer.customer_name.upper(),
            domicilio_fiscal_receptor=address.pincode,
            regimen_fiscal_receptor=customer.mx_tax_regime,
            uso_cfdi="CP01",
        )

    @property
    def cfdi_related_documents(self) -> list[pago20.DoctoRelacionado]:
        """List of `pago20.DoctoRelacionado` objects, each representing a related document for the
        current payment entry."""
        result = []
        for pe_ref in self.references:
            ref = frappe.get_doc(pe_ref.reference_doctype, pe_ref.reference_name)
            last_balance = pe_ref.allocated_amount + pe_ref.outstanding_amount
            result.append(
                pago20.DoctoRelacionado(
                    id_documento=ref.mx_uuid,
                    moneda_dr=ref.currency,
                    num_parcialidad=get_installment_number(
                        ref.doctype, ref.name, self.name
                    ),
                    imp_saldo_ant=last_balance,
                    imp_pagado=pe_ref.allocated_amount,
                    objeto_imp_dr="01",
                    serie=ref.cfdi_series,
                    folio=ref.cfdi_folio,
                )
            )

        return result

    def get_cfdi_voucher(self, csd: DigitalSigningCertificate) -> cfdi40.Comprobante:
        address = frappe.get_doc("Address", self.company_address)

        if not address.pincode:
            frappe.throw(_("Address {0} has no zip code").format(address.name))

        reference_date = self.reference_date
        if isinstance(reference_date, str):
            reference_date = get_datetime(reference_date)

        posting_date = self.posting_date
        if isinstance(posting_date, str):
            posting_date = get_datetime(posting_date)

        issuer = csd.get_issuer()

        if all(r.total_amount == r.allocated_amount for r in self.references):
            invoices = []
            for r in self.references:
                invoice = frappe.get_doc(r.reference_doctype, r.reference_name)
                if not invoice.mx_stamped_xml:
                    msg = _("Reference {0} has not being stamped").format(invoice.name)
                    frappe.throw(msg)
                cfdi = cfdi40.CFDI.from_string(invoice.mx_stamped_xml.encode("utf-8"))
                invoices.append(cfdi)
            return cfdi40.Comprobante.pago_comprobantes(
                comprobantes=invoices,
                fecha_pago=get_datetime(reference_date),
                forma_pago=self.mx_payment_mode,
                emisor=issuer,
                lugar_expedicion=address.pincode,
                serie=self.cfdi_series,
                folio=self.cfdi_folio,
                fecha=get_datetime(posting_date),
            )

        frappe.throw(
            _(
                "All references must have the same total amount, "
                "partial payments are not supported"
            )
        )

        payment = pago20.Pago(
            fecha_pago=reference_date,
            forma_de_pago_p=self.mx_payment_mode,
            moneda_p=self.paid_from_account_currency,
            docto_relacionado=self.cfdi_related_documents,
            tipo_cambio_p=self.source_exchange_rate,
        )

        posting_date = self.posting_date
        if isinstance(posting_date, str):
            posting_date = get_datetime(posting_date)

        return cfdi40.Comprobante.pago(
            emisor=issuer,
            lugar_expedicion=address.pincode,
            receptor=self.cfdi_receiver,
            complemento_pago=pago20.Pagos(pago=payment),
            serie=self.cfdi_series,
            folio=self.cfdi_folio,
            fecha=posting_date,
        )

    def validate_company_address(self):
        """
        Validates the company information associated with the current payment entry.

        This function checks if the company has an address and if it has a valid zip code.
        If any issues are found, an error message is thrown with the list of issues.

        Raises:
            frappe.ValidationError: If any issues were found.
        """
        if self.company_address:
            address = frappe.get_doc("Address", self.company_address)
            if not address.pincode:
                link = f'<a href="{address.get_url()}">{address.name}</a>'
                frappe.throw(_("Address {0} has no zip code").format(link))
        else:
            company = frappe.get_doc("Company", self.company)
            link = f'<a href="{company.get_url()}">{company.name}</a>'
            frappe.throw(_("Company {0} has no address").format(link))

    def get_reference_docs(self) -> list[Document]:
        """List of documents associated with the current payment entry.

        Returns:
            list[Document]: List of documents associated with the current payment entry.
        """

        return [
            frappe.get_doc(r.reference_doctype, r.reference_name)
            for r in self.references
        ]

    def validate_references(self):
        """Validates the references in the payment entry.

        Iterates through each reference in the payment entry and checks if the referenced document
        has been stamped.

        Throws:
            frappe.ValidationError: If any of the references have not been stamped.
        """
        msgs = []
        for ref in self.get_reference_docs():
            if ref.doctype != "Sales Invoice":
                msg = _("Cannot stamp a payment entry with a {0} reference").format(
                    ref.doctype
                )
                msgs.append(msg)

            if not ref.mx_stamped_xml:
                anchor = f'<a href="{ref.get_url()}">{ref.name}</a>'
                msgs.append(_("Reference {0} has not being stamped").format(anchor))

            if ref.mx_payment_option != "PPD":
                msg = _("SAT Payment Option for reference {0} is not PPD").format(
                    ref.mx_payment_option
                )
                msgs.append(msg)

        if len(msgs) > 0:
            frappe.throw(msgs, as_list=True)

    def send_stamp_request(self, certificate: str):
        self.validate_company_address()
        self.validate_references()

        try:
            cfdi = self.sign_cfdi(certificate)
        except SchemaValidationError as e:
            frappe.throw(str(e), title=_("Invalid CFDI"))

        ws = get_ws_client()
        xml = ws.stamp(cfdi)

        self.db_set("mx_stamped_xml", xml)
        self.db_set("mx_uuid", get_uuid_from_xml(xml))

    @frappe.whitelist()
    def has_file(self, file_name: str) -> bool:
        """Returns DocType name if the CFDI document for this sales invoice has a file named as
        `file_name` attached."""
        return frappe.db.exists(
            "File",
            {
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "file_name": file_name,
            },
        )

    @property
    def requires_relationship(self) -> int:
        """Indicates whether a relationship with another payment entry is required for the
        cancellation reason.

        Returns:
            int: 1 if a relationship is required, 0 otherwise.
        """
        if not self.cancellation_reason:
            return 0
        reason = frappe.get_doc("Cancellation Reason", self.cancellation_reason)
        return reason.requires_relationship

    @frappe.whitelist()
    def cancel_cfdi(self, certificate: str):
        """Cancels the CFDI document of this payment entry.

        Args:
            certificate (str): The name of the Digital Signing Certificate to use for cancellation.

        Returns:
            Document: The result of the cancellation operation.
        """
        return super()._cancel_cfdi(certificate, "substitute_payment_entry")

    def set_total_in_words(self):
        if self.payment_type in ("Pay", "Internal Transfer"):
            base_amount = abs(self.base_paid_amount)
            amount = abs(self.paid_amount)
            currency = self.paid_from_account_currency
        elif self.payment_type == "Receive":
            base_amount = abs(self.base_received_amount)
            amount = abs(self.received_amount)
            currency = self.paid_to_account_currency

        self.base_in_words = money_in_words(base_amount, self.company_currency)
        self.in_words = money_in_words(amount, currency)


def get_installment_number(
    doctype: str, docname: str, payment_entry_name: str
) -> int | None:
    """Returns the installment number of a payment entry in a sales invoice.

    Args:
        doctype (str): The type of document.
        docname (str): The name of the document.
        payment_entry_name (str): The name of the payment entry.

    Returns:
        int: The installment number of the payment entry.

    Raises:
        frappe.ValidationError: If the document type is not "Sales Invoice".
    """
    if doctype != "Sales Invoice":
        raise frappe.ValidationError(_("Invalid Document Type"))
    doc = frappe.get_doc(doctype, docname)
    for idx, entry in enumerate(doc.payment_entries, 1):
        if entry.name == payment_entry_name:
            return idx

    return None
