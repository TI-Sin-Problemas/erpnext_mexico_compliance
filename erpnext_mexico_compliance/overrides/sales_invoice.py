"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import frappe
from erpnext.accounts.doctype.sales_invoice import sales_invoice
from erpnext.setup.doctype.company.company import Company, get_default_company_address
from frappe import _
from frappe.contacts.doctype.address.address import Address
from satcfdi.create.cfd import cfdi40

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

    def get_invoice_service_dates(self) -> str:
        """Returns invoice dates as a formatted string"""
        start_date = _("From {}").format(self.from_date) if self.from_date else None
        end_date = _("To {}").format(self.to_date) if self.to_date else None
        return f"{start_date} {end_date}".strip()

    @property
    def company_doc(self) -> Company:
        """Company that created the invoice

        Returns:
            Company: Company doctype
        """
        return frappe.get_doc("Company", self.company)

    @property
    def customer_doc(self) -> Customer:
        """Customer of the invoice

        Returns:
            Customer: Customer doctype
        """
        return frappe.get_doc("Customer", self.customer)

    @property
    def company_address_doc(self) -> Address:
        """Address of the issuer company

        Returns:
            Company: Company address doctype
        """
        return frappe.get_doc("Address", self.company_address)

    @property
    def customer_address_doc(self) -> Address:
        """Address of the customer

        Returns:
            Address: Customer address doctype
        """
        return frappe.get_doc("Address", self.customer_address)

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

    def get_cfdi_receiver(self) -> cfdi40.Receptor:
        """Returns a `cfdi40.Receptor` object representing the receiver of the CFDI document for
        this sales invoice.

        Returns:
            cfdi40.Receptor: Required node to specify the information of the taxpayer receiving the
            receipt.
        """
        return cfdi40.Receptor(
            rfc=self.customer_doc.tax_id,
            nombre=self.customer_name.upper(),
            domicilio_fiscal_receptor=self.customer_address_doc.pincode,
            regimen_fiscal_receptor=self.customer_doc.mx_tax_regime,
            uso_cfdi=self.mx_cfdi_use,
        )

