import typing as t

import frappe
from frappe import _
from frappe.utils import file_manager, pdf

from erpnext_mexico_compliance.utils.files import compress_files


@frappe.whitelist()
def download_cfdi_files(
    doctype: t.Literal["Sales Invoice", "Payment Entry"], docname: str
):
    """
    Download CFDI files for a given document.

    Args:
        doctype (t.Literal["Sales Invoice", "Payment Entry"]): The doctype of the document.
        docname (str): The name of the document.

    Returns:
        A response with the file content and filename.
    """

    file_table = frappe.qb.DocType("File")
    doctype_table = frappe.qb.DocType(doctype)
    portal_user_table = frappe.qb.DocType("Portal User")
    query = (
        frappe.qb.get_query(
            doctype_table,
            fields=[file_table.file_name],
            filters={
                doctype_table.name: docname,
                portal_user_table.user: frappe.session.user,
                portal_user_table.parenttype: "Customer",
                file_table.attached_to_doctype: doctype,
                file_table.file_name: ["like", "%CFDI%"],
            },
        )
        .left_join(portal_user_table)
        .on(portal_user_table.parent == doctype_table.customer)
        .left_join(file_table)
        .on(file_table.attached_to_name == doctype_table.name)
    )
    file_names = query.run()

    if len(file_names) == 0:
        raise frappe.PageDoesNotExistError

    frappe.local.response.filename = f"{docname}.zip"
    frappe.local.response.filecontent = compress_files(
        [file_manager.get_file_path(f[0]) for f in file_names]
    )
    frappe.local.response.type = "download"


@frappe.whitelist()
def download_cancellation_acknowledgement(
    doctype: t.Literal["Sales Invoice", "Payment Entry"], docname: str
):
    """Downloads a PDF containing the cancellation acknowledgement for the given document.

    Args:
        doctype (str): The type of document to cancel.
        docname (str): The name of the document to cancel.

    Raises:
        frappe.PageDoesNotExistError: If the document does not exist.
        frappe.ValidationError: If the document does not have a cancellation acknowledgement.
    """
    doc = frappe.get_doc(doctype, docname)

    if not doc.cancellation_acknowledgement:
        msg = _("No cancellation acknowledgement available for {0} {1}.")
        frappe.throw(
            msg.format(doctype, docname),
            title=_("Cancellation Acknowledgement Not Found"),
        )

    template = frappe.get_template(
        "erpnext_mexico_compliance/templates/cfdi/cancellation_acknowledgement.html"
    )
    reason = frappe.get_doc("Cancellation Reason", doc.cancellation_reason)

    substitute_attribute = (
        "substitute_invoice"
        if doctype == "Sales Invoice"
        else "substitute_payment_entry"
    )
    substitute_doc = getattr(doc, substitute_attribute)
    if substitute_doc:
        substitute_doc = frappe.get_doc(doctype, substitute_doc)

    frappe.local.response.filename = f"Acuse_{docname}.pdf"
    frappe.local.response.filecontent = pdf.get_pdf(
        template.render(
            ack=doc.ack_cancellation_element, reason=reason, substitute=substitute_doc
        )
    )
    frappe.local.response.type = "pdf"
