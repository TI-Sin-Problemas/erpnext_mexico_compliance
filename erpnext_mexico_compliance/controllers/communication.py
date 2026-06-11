import json
from typing import TYPE_CHECKING

import frappe
from frappe.core.doctype.communication.email import make

if TYPE_CHECKING:
	from frappe.core.doctype.file.file import File

	from erpnext_mexico_compliance.overrides.payment_entry import PaymentEntry
	from erpnext_mexico_compliance.overrides.sales_invoice import SalesInvoice


@frappe.whitelist()
def send_email(
	doctype: str | None = None,
	name: str | None = None,
	content: str | None = None,
	subject: str | None = None,
	sent_or_received: str = "Sent",
	sender: str | None = None,
	sender_full_name: str | None = None,
	recipients: str | list[str] | None = None,
	communication_medium: str = "Email",
	send_email: bool = False,
	print_html: str | None = None,
	print_format: str | None = None,
	attachments: str | list[dict[str, str]] | None = None,
	send_me_a_copy: bool = False,
	cc: str | list[str] | None = None,
	bcc: str | list[str] | None = None,
	read_receipt: str | None = None,
	print_letterhead: bool = True,
	email_template: str | None = None,
	communication_type: str | None = None,
	send_after: str | None = None,
	print_language: str | None = None,
	now: bool = False,
	raw_html: bool = False,
	add_css: bool = True,
	in_reply_to: str | None = None,
	attach_cfdi_files: bool = False,
	**kwargs,
) -> dict[str, str]:
	doc: PaymentEntry | SalesInvoice = frappe.get_doc(doctype, name)  # type: ignore
	if attach_cfdi_files and doc.mx_stamped_xml:
		if attachments is None:
			attachments = []
		elif isinstance(attachments, str):
			attachments = json.loads(attachments)

		file_name = f"{doc.name}_CFDI.zip"
		file_content = doc.get_cfdi_zip_file().getvalue()
		file_id = frappe.db.exists("File", {"file_name": file_name})

		if file_id:
			file: File = frappe.get_doc("File", {"file_name": file_name})  # type: ignore
			file.content = file_content
			saved_file = file.save()
			attachments.append(saved_file.name)
		else:
			attachments.append({"fname": file_name, "fcontent": file_content})

	return make(
		doctype=doctype,
		name=name,
		content=content,
		subject=subject,
		sent_or_received=sent_or_received,
		sender=sender,
		sender_full_name=sender_full_name,
		recipients=recipients,
		communication_medium=communication_medium,
		send_email=send_email,
		print_html=print_html,
		print_format=print_format,
		attachments=attachments,
		send_me_a_copy=send_me_a_copy,
		cc=cc,
		bcc=bcc,
		read_receipt=read_receipt,
		print_letterhead=print_letterhead,
		email_template=email_template,
		communication_type=communication_type,
		send_after=send_after,
		print_language=print_language,
		now=now,
		raw_html=raw_html,
		add_css=add_css,
		in_reply_to=in_reply_to,
		**kwargs,
	)
