"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""

from decimal import Decimal

import frappe
from erpnext.accounts.doctype.sales_invoice import sales_invoice
from erpnext.setup.doctype.company.company import Company, get_default_company_address
from frappe import _
from frappe.contacts.doctype.address.address import Address
from frappe.model.naming import NamingSeries
from satcfdi.create.cfd import catalogos, cfdi40

from .customer import Customer


class SalesInvoice(sales_invoice.SalesInvoice):
    """ERPNext Sales Invoice override"""

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        mx_payment_option: DF.Link
        mode_of_payment: DF.Link
        mx_cfdi_use: DF.Link
        mx_payment_mode: DF.Data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.company_address:
            self.company_address = get_default_company_address(self.company)

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
    def company_address_doc(self) -> Address:
        """Address DocType of the issuer company"""
        return frappe.get_doc("Address", self.company_address)

    @property
    def customer_address_doc(self) -> Address:
        """Address DocType of the customer"""
        return frappe.get_doc("Address", self.customer_address)

    @property
    def tax_accounts(self) -> list[dict]:
        heads = [t.account_head for t in self.taxes]
        return frappe.get_list(
            "Account",
            filters={"name": ["in", heads]},
            fields=["name", "tax_type", "tax_rate"],
        )

    def validate_company(self):
        """Validates the company information on the invoice.

        This function checks if the company has an address and if it has a valid zip code.
        If any issues are found, an error message is thrown with the list of issues.

        Raises:
            frappe.ValidationError: If any issues were found.
        """
        msgs = []
        if self.company_address:
            address = self.company_address_doc
            if not address.pincode:
                link = f'<a href="{address.get_url()}">{address.name}</a>'
                msgs.append(_("Address {0} has no zip code").format(link))
        else:
            company = self.company_doc
            link = f'<a href="{company.get_url()}">{company.name}</a>'
            msgs.append(_("Company {0} has no address").format(link))

        if len(msgs) > 0:
            frappe.throw(msgs, as_list=True)

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
            discount = Decimal(item.discount_amount) if item.discount_amount else None
            cfdi_items.append(
                cfdi40.Concepto(
                    clave_prod_serv=item.mx_product_service_key,
                    cantidad=Decimal(item.qty),
                    clave_unidad=item.uom_doc.mx_uom_key,
                    descripcion=item.cfdi_description,
                    valor_unitario=Decimal(item.rate),
                    no_identificacion=item.item_code,
                    descuento=discount,
                    impuestos=item.cfdi_taxes,
                )
            )
        return cfdi_items

    @property
    def cfdi_series(self) -> str:
        """Series code for the CFDI document for this sales invoice."""
        prefix = str(NamingSeries(self.naming_series).get_prefix())
        return prefix if prefix[-1].isalnum() else prefix[:-1]

    @property
    def cfdi_folio(self) -> str:
        """Folio number for the CFDI document for this sales invoice."""
        prefix = str(NamingSeries(self.naming_series).get_prefix())
        return str(int(self.name.replace(prefix, "")))

