"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt"""

import typing as t

import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from satcfdi.cfdi import CFDI

from erpnext_mexico_compliance.hooks import app_name
from erpnext_mexico_compliance.utils import qr_as_base64


def get_sample_file_content(
    document_type: str, sample_type: t.Literal["xml", "html.jinja", "css"]
) -> str:
    """
    Reads a sample file for the given document type.

    Args:
        document_type (str): The document type of the file to read.
        sample_type (Literal["xml", "html", "css"]): The type of the file to read, which can be
            "xml", "html", or "css".

    Returns:
        str: The contents of the sample file.

    Raises:
        ValueError: If the document type is not supported.
    """
    match document_type:
        case "Payment Entry":
            file_name = f"pago.{sample_type}"
        case "Sales Invoice":
            file_name = f"ingreso.{sample_type}"
        case _:
            raise ValueError(f"Unsupported document type: {document_type}")

    path = f"{frappe.get_app_path(app_name)}/examples/cfdi/{file_name}"
    with open(path, "r") as f:
        content = f.read()
    return content


class CFDIPDFTemplate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        company: DF.Link
        content_html: DF.HTMLEditor
        css_styles: DF.Code | None
        document_type: DF.Literal["", "Payment Entry", "Sales Invoice"]
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
            body = f"<body>{header}{self.content_html}{footer}</body>"
        else:
            body = f"<body>{self.content_html}</body>"
        return f"<html>{head}{body}</html>"

    def get_rendered_pdf(self, xml: str) -> bytes:
        """Renders the PDF template with the given XML and returns it as a PDF.

        Args:
            xml (str): The XML of the CFDI to render.

        Returns:
            bytes: The rendered PDF.
        """
        cfdi = CFDI.from_string(xml.encode("utf-8"))
        qr = qr_as_base64(cfdi.verifica_url)
        rendered = frappe.render_template(self.template, {"cfdi": cfdi, "qr": qr})
        return get_pdf(rendered)

    def get_example_pdf(self):
        """Generates an example PDF using a sample CFDI XML file.

        This method reads a sample CFDI XML file from the application's examples directory,
        renders it using the PDF template, and returns the resulting PDF as bytes.

        Returns:
            bytes: The rendered example PDF.
        """

        xml = get_sample_file_content(self.document_type, "xml")
        return self.get_rendered_pdf(xml)

    @frappe.whitelist()
    def get_sample_content(self) -> str:
        """Returns a sample HTML content for the given document type.

        This method reads a sample HTML file from the application's examples directory,
        which can be used to populate the `content_html` field of the CFDI PDF template.

        Returns:
            str: The sample HTML content.
        """
        return get_sample_file_content(self.document_type, "html.jinja")

    @frappe.whitelist()
    def get_sample_css(self) -> str:
        """Returns a sample CSS content for the given document type.

        This method reads a sample CSS file from the application's examples directory,
        which can be used to populate the `css_styles` field of the CFDI PDF template.

        Returns:
            str: The sample CSS content.
        """

        return get_sample_file_content(self.document_type, "css")


@frappe.whitelist()
def print_example(docname):
    """Prints a rendered PDF of the given CFDI PDF template.

    Args:
        docname (str): The name of the CFDI PDF template document to render.
    """
    doc = frappe.get_doc("CFDI PDF Template", docname)
    frappe.local.response.filename = f"{doc.title}.pdf"
    frappe.local.response.filecontent = doc.get_example_pdf()
    frappe.local.response.type = "pdf"
