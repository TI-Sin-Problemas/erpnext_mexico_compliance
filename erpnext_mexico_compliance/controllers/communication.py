import ast
from typing import TYPE_CHECKING

import frappe
from frappe.core.doctype.communication.email import make

if TYPE_CHECKING:
	from erpnext_mexico_compliance.overrides.payment_entry import PaymentEntry
	from erpnext_mexico_compliance.overrides.sales_invoice import SalesInvoice


@frappe.whitelist()
def send_email(
	doctype=None,
	name=None,
	content=None,
	subject=None,
	sent_or_received="Sent",
	sender=None,
	sender_full_name=None,
	recipients=None,
	communication_medium="Email",
	send_email=False,
	print_html=None,
	print_format=None,
	attachments=None,
	send_me_a_copy=False,
	cc=None,
	bcc=None,
	read_receipt=None,
	print_letterhead=True,
	email_template=None,
	communication_type=None,
	send_after=None,
	print_language=None,
	now=False,
	raw_html=False,
	add_css=True,
	in_reply_to=None,
	attach_cfdi_files=False,
	**kwargs,
) -> dict[str, str]:
	doc: PaymentEntry | SalesInvoice = frappe.get_doc(doctype, name)  # type: ignore
	if attach_cfdi_files and doc.mx_stamped_xml:
		if attachments is None:
			attachments = []
		elif isinstance(attachments, str):
			attachments = ast.literal_eval(attachments)

		attachments.append({"fname": f"{doc.name}_CFDI.zip", "fcontent": doc.get_cfdi_zip_file().getvalue()})

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
