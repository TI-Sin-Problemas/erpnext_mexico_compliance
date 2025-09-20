"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import sys
from datetime import datetime
from decimal import Decimal

import frappe
from erpnext.accounts.doctype.sales_invoice import sales_invoice
from erpnext.setup.doctype.company.company import Company, get_default_company_address
from frappe import _
from frappe.contacts.doctype.address.address import Address
from frappe.utils import get_datetime
from satcfdi.create.cfd import catalogos, cfdi40
from satcfdi.exceptions import SchemaValidationError

from erpnext_mexico_compliance.utils import money_in_words
from erpnext_mexico_compliance.utils.cfdi import get_uuid_from_xml

from ..controllers.common import CommonController
from ..erpnext_mexico_compliance.doctype.cfdi_stamping_settings.cfdi_stamping_settings import (
    CFDIStampingSettings,
)
from ..ws_client import get_ws_client
from .customer import Customer

# temporary hack until https://github.com/frappe/frappe/issues/27373 is fixed
if sys.path[0].rsplit("/", maxsplit=1)[-1] == "utils":
    sys.path[0] = sys.path[0].replace("apps/frappe/frappe/utils", "sites")


class SalesInvoice(CommonController, sales_invoice.SalesInvoice):
    """ERPNext Sales Invoice override"""

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        mx_payment_option: DF.Link
        mode_of_payment: DF.Link
        mx_cfdi_use: DF.Link
        mx_payment_mode: DF.Data
        mx_stamped_xml: DF.HTMLEditor
        cancellation_reason: DF.Link
        substitute_invoice: DF.Link
        cancellation_acknowledgement: DF.HTMLEditor
        mx_addenda: DF.HTMLEditor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.company_address:
            self.company_address = get_default_company_address(self.company)

    def on_submit(self):
        """
        Stamps the sales invoice atomatically if the
        CFDI Stamping Settings are configured to do so.

        If the CFDI Stamping Settings are configured to stamp the sales invoice
        automatically, this method will stamp the sales invoice with the first
        digital signing certificate that matches the company of the sales
        invoice. If no matching certificate is found, the sales invoice will not
        be stamped.
        """
        super().on_submit()
        settings: CFDIStampingSettings = frappe.get_single("CFDI Stamping Settings")
        if settings.stamp_on_submit:
            csd = frappe.get_value("Default CSD", {"company": self.company}, "csd")
            # If stamping fails, do not block the submission of the sales invoice
            try:
                self.stamp_cfdi(csd)
            except Exception as e:
                frappe.msgprint(str(e), title=_("CFDI Stamping Error"))

    @property
    def subscription_duration_display(self) -> str:
        """Returns a string displaying the service duration in a formatted manner.

        The service duration is displayed as a range between the start date and the end date, if
        both are provided. If only one of them is provided, the string will display the start or
        end date accordingly. If neither is provided, an empty string is returned.

        Examples:
        - From `start_date`
        - To `end_date`
        - From `start_date` To `end_date`

        Returns:
            str: The formatted service duration string.
        """
        start_date = _("From {}").format(self.from_date) if self.from_date else ""
        end_date = _("To {}").format(self.to_date) if self.to_date else ""
        return f"{start_date} {end_date}".strip()

    @property
    def company_doc(self) -> Company:
        """Company DocType that created the invoice"""
        return frappe.get_doc("Company", self.company)

    @property
    def customer_doc(self) -> Customer:
        """Customer DocType of the invoice"""
        return frappe.get_doc("Customer", self.customer)

    @property
    def customer_address_doc(self) -> Address:
        """Address DocType of the customer"""
        return frappe.get_doc("Address", self.customer_address)

    @property
    def tax_accounts(self) -> list[dict]:
        """Returns a list of dictionaries containing tax account information.

        The list includes the name, tax type, and tax rate of each account.
        The accounts are filtered by the names of the account heads in the invoice's taxes.

        Returns:
            list[dict]: A list of dictionaries containing tax account information.
        """
        heads = [t.account_head for t in self.taxes]
        return frappe.get_list(
            "Account",
            filters={"name": ["in", heads]},
            fields=["name", "tax_type", "tax_rate"],
        )

    def validate_company_address(self):
        """Validates the company address on the invoice.

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
            company = self.company_doc
            link = f'<a href="{company.get_url()}">{company.name}</a>'
            frappe.throw(_("Company {0} has no address").format(link))

    def validate_customer(self):
        """Validates the customer information on the invoice.

        This function checks if the customer has a tax ID, tax regime, and a valid billing address.
        It also checks if the customer's address has a valid zip code.
        If any issues are found, an error message is thrown with the list of issues.

        Raises:
            frappe.ValidationError: If any issues were found.
        """
        customer_link = (
            f'<a href="{self.customer_doc.get_url()}">{self.customer_doc.name}</a>'
        )
        msgs = []
        if not self.customer_doc.tax_id:
            msgs.append(_("Customer {0} has no tax ID").format(customer_link))

        if not self.customer_doc.mx_tax_regime:
            msgs.append(_("Customer {0} has no tax regime").format(customer_link))

        if self.customer_address:
            address = self.customer_address_doc
            if not address.pincode:
                link = f'<a href="{address.get_url()}">{address.name}</a>'
                msgs.append(_("Customer address {0} has no zip code").format(link))
        else:
            msgs.append(_("Invoice has no billing address"))

        if len(msgs) > 0:
            frappe.throw(msgs, as_list=True)

        self.customer_doc.validate_mexican_tax_id()

    @property
    def cfdi_receiver(self) -> cfdi40.Receptor:
        """`cfdi40.Receptor` object representing the receiver of the CFDI document for this sales
        invoice."""
        return cfdi40.Receptor(
            rfc=self.customer_doc.tax_id,
            nombre=self.customer_name.upper(),
            domicilio_fiscal_receptor=self.customer_address_doc.pincode,
            regimen_fiscal_receptor=self.customer_doc.mx_tax_regime,
            uso_cfdi=self.mx_cfdi_use,
        )

    @property
    def cfdi_items(self) -> list[cfdi40.Concepto]:
        """Returns a list of `cfdi40.Concepto` objects representing the items of the CFDI document
        for this sales invoice."""
        cfdi_items = []
        for item in self.items:
            discount = (
                Decimal(str(item.discount_amount)) if item.discount_amount else None
            )
            cfdi_items.append(
                cfdi40.Concepto(
                    clave_prod_serv=item.mx_product_service_key,
                    cantidad=Decimal(item.qty),
                    clave_unidad=item.uom_doc.mx_uom_key,
                    descripcion=item.cfdi_description,
                    valor_unitario=Decimal(str(item.rate + item.discount_amount)),
                    no_identificacion=item.item_code,
                    descuento=discount,
                    impuestos=item.cfdi_taxes,
                )
            )
        return cfdi_items

    @property
    def posting_datetime(self) -> datetime:
        """`datetime` object representing the posting date and time of the sales invoice."""
        return get_datetime(f"{self.posting_date}T{self.posting_time}")

    def get_cfdi_voucher(self, csd) -> cfdi40.Comprobante:
        address = frappe.get_doc("Address", self.company_address)
        return cfdi40.Comprobante(
            emisor=csd.get_issuer(),
            lugar_expedicion=address.pincode,
            receptor=self.cfdi_receiver,
            conceptos=self.cfdi_items,
            moneda=self.currency,
            tipo_de_comprobante=catalogos.TipoDeComprobante.INGRESO,
            serie=self.cfdi_series,
            folio=self.cfdi_folio,
            forma_pago=self.mx_payment_mode,
            tipo_cambio=(
                Decimal(self.conversion_rate) if self.currency != "MXN" else None
            ),
            metodo_pago=self.mx_payment_option,
            fecha=self.posting_datetime,
        )

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

    def send_stamp_request(self, certificate: str):
        """Stamps a CFDI document for the current sales invoice.

        Args:
            certificate (str): The name of the Digital Signing Certificate to use for signing.
        """
        self.validate_company_address()
        self.validate_customer()

        try:
            cfdi = self.sign_cfdi(certificate)
        except SchemaValidationError as e:
            frappe.throw(str(e), title=_("Invalid CFDI"))

        ws = get_ws_client()
        xml = ws.stamp(cfdi)

        self.db_set("mx_stamped_xml", xml)
        self.db_set("mx_uuid", get_uuid_from_xml(xml))

    @property
    def requires_relationship(self) -> int:
        """This property determines whether a relationship with another sales invoice is required
        for the current sales invoice.

        It checks if a cancellation reason is set, and if so, retrieves the corresponding
        Cancellation Reason document.

        The function returns an integer indicating whether a relationship is required, based on the
        requires_relationship field of the Cancellation Reason document.

        Returns:
            int: 1 if a relationship is required, 0 otherwise.
        """
        if not self.cancellation_reason:
            return 0
        reason = frappe.get_doc("Cancellation Reason", self.cancellation_reason)
        return reason.requires_relationship

    @frappe.whitelist()
    def cancel_cfdi(self, certificate: str):
        """Cancels the CFDI document of this sales invoice.

        Args:
            certificate (str): The name of the Digital Signing Certificate to use for cancellation.

        Returns:
            Document: The result of the cancellation operation.
        """
        return super()._cancel_cfdi(certificate, "substitute_invoice")

    @property
    def payment_entries(self) -> list[frappe._dict]:
        """List of Payment Entries associated with the current Sales Invoice."""
        references = frappe.get_all(
            "Payment Entry Reference",
            filters={
                "reference_doctype": self.doctype,
                "reference_name": self.name,
            },
            fields=["parent"],
        )
        return frappe.get_all(
            "Payment Entry",
            filters={"name": ["in", [r.parent for r in references]]},
            fields=["name", "posting_date"],
            order_by="posting_date asc",
        )

    def set_total_in_words(self):
        if self.meta.get_field("base_in_words"):
            base_amount = abs(
                self.base_grand_total
                if self.is_rounded_total_disabled()
                else self.base_rounded_total
            )
            self.base_in_words = money_in_words(base_amount, self.company_currency)

        if self.meta.get_field("in_words"):
            amount = abs(
                self.grand_total
                if self.is_rounded_total_disabled()
                else self.rounded_total
            )
            self.in_words = money_in_words(amount, self.currency)
