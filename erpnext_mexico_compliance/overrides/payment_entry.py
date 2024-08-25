"""
Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import frappe
from erpnext.accounts.doctype.payment_entry import payment_entry
from erpnext.setup.doctype.company.company import get_default_company_address
from frappe import _
from satcfdi.create.cfd import cfdi40, pago20
from satcfdi.exceptions import SchemaValidationError

from ..controllers.common import CommonController
from ..erpnext_mexico_compliance.doctype.digital_signing_certificate.digital_signing_certificate import (
    DigitalSigningCertificate,
)
from ..ws_client import WSClientException, WSExistingCfdiException, get_ws_client


class PaymentEntry(CommonController, payment_entry.PaymentEntry):
    """ERPNext Payment Entry override"""

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        mx_payment_mode: DF.Data
        mx_stamped_xml: DF.HTMLEditor

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
                    id_documento=ref.cfdi_uuid,
                    moneda_dr=ref.currency,
                    num_parcialidad=get_installment_number(
                        ref.doctype, ref.name, self.name
                    ),
                    imp_saldo_ant=last_balance,
                    imp_pagado=pe_ref.allocated_amount,
                    objeto_imp_dr="01",
                )
            )

        return result

    def get_cfdi_voucher(self, csd: DigitalSigningCertificate) -> cfdi40.Comprobante:
        address = frappe.get_doc("Address", self.company_address)

        if not address.pincode:
            frappe.throw(_("Address {0} has no zip code").format(address.name))

        return cfdi40.Comprobante.pago(
            emisor=csd.get_issuer(),
            lugar_expedicion=address.pincode,
            receptor=self.cfdi_receiver,
            complemento_pago=pago20.Pagos(
                pago=pago20.Pago(
                    fecha_pago=self.reference_date,
                    forma_de_pago_p=self.mx_payment_mode,
                    moneda_p=self.currency,
                    docto_relacionado=self.cfdi_related_documents,
                    tipo_cambio_p=self.conversion_rate,
                )
            ),
            serie=self.cfdi_series,
            folio=self.cfdi_folio,
            fecha=self.posting_date,
        )

    def validate_company(self):
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

    def validate_references(self):
        """Validates the references in the payment entry.

        Iterates through each reference in the payment entry and checks if the referenced document
        has been stamped.

        Throws:
            frappe.ValidationError: If any of the references have not been stamped.
        """
        msgs = []
        for pe_ref in self.references:
            ref = frappe.get_doc(pe_ref.reference_doctype, pe_ref.reference_name)
            if not ref.mx_stamped_xml:
                anchor = f'<a href="{ref.get_url()}">{ref.name}</a>'
                msgs.append(_("Reference {0} has not being stamped").format(anchor))

        if len(msgs) > 0:
            frappe.throw(msgs, as_list=True)

    @frappe.whitelist()
    def stamp_cfdi(self, certificate: str):
        self.validate_company()
        self.validate_references()

        cfdi = self.sign_cfdi(certificate)
        ws = get_ws_client()
        try:
            data, message = ws.stamp(cfdi)
        except SchemaValidationError as e:
            frappe.throw(str(e), title=_("Invalid CFDI"))
        except WSExistingCfdiException as e:
            data = e.data
            message = e.message
        except WSClientException as e:
            frappe.throw(str(e), title=_("CFDI Web Service Error"))

        self.mx_stamped_xml = data
        self.save()
        return message


def get_installment_number(doctype: str, docname: str, payment_entry_name: str) -> int:
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