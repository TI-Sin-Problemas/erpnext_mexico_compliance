import typing as t

import frappe
from frappe.utils import file_manager

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
