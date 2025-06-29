"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe
from erpnext_mexico_compliance.hooks import app_name
from erpnext_mexico_compliance.utils import qr_as_base64
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from satcfdi.cfdi import CFDI


class CFDIPDFTemplate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        body: DF.HTMLEditor
        company: DF.Link
        css_styles: DF.Code | None
        document_type: DF.Literal["Sales Invoice"]
        letter_head: DF.Link | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        title: DF.Data | None
    # end: auto-generated types

    @property
    def template(self):
        """Returns the HTML template for the PDF."""
        title = f"<title>{self.title}</title>"
        style = f"<style>{self.css_styles}</style>"
        head = (
            '<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
            f"{title}{style}</head>"
        )
        if self.letter_head:
            letterhead = frappe.get_doc("Letter Head", self.letter_head)
            header = letterhead.content or ""
            footer = letterhead.footer or ""
            body = f"<body>{header}{self.body}{footer}</body>"
        else:
            body = f"<body>{self.body}</body>"
        return f"<html>{head}{body}</html>"

    def get_rendered_example(self):
        """Renders the PDF template with a sample CFDI and returns it as rendered HTML.

        The sample CFDI is taken from the `examples/cfdi/ingreso.xml` file in the app directory.
        The QR code is generated from the verification URL of the sample CFDI.

        Returns:
            str: The rendered HTML template.
        """
        example_file_path = f"{frappe.get_app_path(app_name)}/examples/cfdi/ingreso.xml"
        cfdi = CFDI.from_file(example_file_path)
        qr = qr_as_base64(cfdi.verifica_url)
        return frappe.render_template(self.template, {"cfdi": cfdi, "qr": qr})


@frappe.whitelist()
def print_example(docname):
    """Prints a rendered PDF of the given CFDI PDF template.

    Args:
        docname (str): The name of the CFDI PDF template document to render.
    """
    doc = frappe.get_doc("CFDI PDF Template", docname)
    frappe.local.response.filename = f"{doc.title}.pdf"
    frappe.local.response.filecontent = get_pdf(doc.get_rendered_example())
    frappe.local.response.type = "pdf"
