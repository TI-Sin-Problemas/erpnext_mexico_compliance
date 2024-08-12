"""
Copyright (c) 2022, TI Sin Problemas and contributors
For license information, please see license.txt
"""

from decimal import Decimal

import frappe
from erpnext.accounts.doctype.sales_invoice_item import sales_invoice_item
from erpnext.setup.doctype.uom.uom import UOM
from erpnext.stock.doctype.item.item import Item
from frappe import _
from frappe.utils import strip_html
from satcfdi.create.cfd import catalogos, cfdi40


class SalesInvoiceItem(sales_invoice_item.SalesInvoiceItem):
    """ERPNext Sales Invoice Item override"""

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        mx_product_service_key: DF.Link

    def before_validate(self):
        """Add missing fields before validation"""
        if self.item_code:
            item = frappe.get_doc("Item", self.item_code)
            self.mx_product_service_key = item.mx_product_service_key

    @property
    def item_doc(self) -> Item:
        """Related Item DocType

        Returns:
            Item: Item doctype
        """
        if self.item_code:
            return frappe.get_doc("Item", self.item_code)
        return None

    @property
    def uom_doc(self) -> UOM:
        """The UOM (Unit of Measure) DocType of the item.

        Returns:
            UOM: UOM of the item
        """
        return frappe.get_doc("UOM", self.uom)

    @property
    def service_duration_display(self) -> str:
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
        start_date = ""
        if self.service_start_date:
            start_date = _("From {}").format(self.service_start_date)

        end_date = ""
        if self.service_end_date:
            start_date = _("To {}").format(self.service_end_date)

        return f"{start_date} {end_date}".strip()

    @property
    def cfdi_description(self):
        """Returns description ready to stamp a CFDI"""
        cfdi_description = f"{self.item_name}"
        item_description = strip_html(self.description)
        if all([self.description, self.item_name != item_description]):
            cfdi_description += f" - {item_description}"

        invoice_dates = self.parent_doc.subscription_duration_display
        if invoice_dates:
            cfdi_description += f" ({invoice_dates})"

        return cfdi_description.strip()

    @property
    def cfdi_taxes(self) -> cfdi40.Impuestos:
        """The `cfdi40.Impuestos` object representing the taxes for this sales invoice item."""
        withholding_taxes = []
        transferred_taxes = []
        for account in self.parent_doc.tax_accounts:
            tax_type = catalogos.Impuesto[account["tax_type"]]
            tax_rate = account["tax_rate"] / 100

            if tax_rate < 0:
                withholding = cfdi40.Retencion(
                    impuesto=tax_type,
                    tipo_factor=catalogos.TipoFactor.TASA,
                    tasa_o_cuota=Decimal(tax_rate * -1),
                )
                withholding_taxes.append(withholding)
            else:
                transferred = cfdi40.Traslado(
                    impuesto=tax_type,
                    tipo_factor=catalogos.TipoFactor.TASA,
                    tasa_o_cuota=Decimal(tax_rate),
                )
                transferred_taxes.append(transferred)

        return cfdi40.Impuestos(
            retenciones=withholding_taxes, traslados=transferred_taxes
        )
