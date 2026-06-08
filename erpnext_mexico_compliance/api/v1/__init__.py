import typing as t

import frappe
from frappe import _
from frappe.utils import pdf

if t.TYPE_CHECKING:
	from erpnext_mexico_compliance.overrides.payment_entry import PaymentEntry
	from erpnext_mexico_compliance.overrides.sales_invoice import SalesInvoice


@frappe.whitelist()
def download_cfdi_files(doctype: t.Literal["Sales Invoice", "Payment Entry"], docname: str):
	"""Download CFDI files for a given document.

	Args:
		doctype (t.Literal["Sales Invoice", "Payment Entry"]): The doctype of the document.
		docname (str): The name of the document.

	Returns:
		A response with the file content and filename.
	"""
	customers = frappe.get_all("Customer", {"portal_users.user": frappe.session.user}, pluck="name")
	doc: SalesInvoice | PaymentEntry = frappe.get_doc(
		doctype,
		{"name": docname, "customer": ["in", customers]},  # type: ignore
	)
	doc.download_cfdi_files()


@frappe.whitelist()
def download_cancellation_acknowledgement(doctype: t.Literal["Sales Invoice", "Payment Entry"], docname: str):
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

	substitute_attribute = "substitute_invoice" if doctype == "Sales Invoice" else "substitute_payment_entry"
	substitute_doc = getattr(doc, substitute_attribute)
	if substitute_doc:
		substitute_doc = frappe.get_doc(doctype, substitute_doc)

	frappe.local.response.filename = f"Acuse_{docname}.pdf"
	frappe.local.response.filecontent = pdf.get_pdf(
		template.render(ack=doc.ack_cancellation_element, reason=reason, substitute=substitute_doc)
	)
	frappe.local.response.type = "pdf"
