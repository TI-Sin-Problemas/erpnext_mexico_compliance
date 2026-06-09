// Copyright (c) 2026, TI Sin Problemas and contributors
// For license information, please see license.txt

frappe.views.CommunicationComposer = class extends frappe.views.CommunicationComposer {
	get_fields() {
		const fields = super.get_fields();
		fields.push({
			label: __("Attach CFDI files"),
			fieldname: "attach_cfdi_files",
			fieldtype: "Check",
			default: 1,
		});
		return fields;
	}

	send_email(btn, form_values, selected_attachments, print_html, print_format) {
		const me = this;
		this.dialog.hide();

		if (!form_values.recipients && !form_values.cc && !form_values.bcc) {
			frappe.msgprint(__("Enter Email Recipient(s) in the To, CC, or BCC fields"));
			return;
		}

		if (!form_values.attach_document_print) {
			print_html = null;
			print_format = null;
		}

		if (this.frm && !frappe.model.can_email(this.doc.doctype, this.frm)) {
			frappe.msgprint(__("You are not allowed to send emails related to this document"));
			return;
		}

		return frappe.call({
			method: "erpnext_mexico_compliance.controllers.communication.send_email",
			args: {
				recipients: form_values.recipients,
				cc: form_values.cc,
				bcc: form_values.bcc,
				subject: form_values.subject,
				content: me.get_email_content(),
				doctype: me.doc.doctype,
				name: me.doc.name,
				send_email: 1,
				print_html: print_html,
				send_me_a_copy: form_values.send_me_a_copy,
				print_format: print_format,
				sender: form_values.sender,
				sender_full_name: form_values.sender ? frappe.user.full_name() : undefined,
				email_template: form_values.email_template,
				attachments: selected_attachments,
				read_receipt: form_values.send_read_receipt,
				print_letterhead: me.is_print_letterhead_checked(),
				send_after: form_values.send_after ? form_values.send_after : null,
				print_language: form_values.print_language,
				raw_html: form_values.use_html,
				add_css: form_values.add_css,
				in_reply_to: (this.is_a_reply && this.last_email?.name) || null,
				attach_cfdi_files: form_values.attach_cfdi_files,
			},
			btn,
			callback(r) {
				if (!r.exc) {
					frappe.utils.play_sound("email");

					const communication_name = r.message["name"];

					if (r.message["emails_not_sent_to"]) {
						frappe.msgprint(
							__("Email not sent to {0} (unsubscribed / disabled)", [
								frappe.utils.escape_html(r.message["emails_not_sent_to"]),
							])
						);
					}

					me.clear_cache();

					if (me.frm) {
						me.frm.reload_doc();
					}

					let undo_alert = frappe.show_alert(
						{
							message: `<span>${__(
								"Email Sent"
							)}</span><span class="cursor-pointer ml-4" data-action="undo" style="font-weight: 500; text-decoration: underline;">${__(
								"Undo"
							)}</span>`,
							indicator: "green",
						},
						10,
						{
							undo: () => {
								if (undo_alert) {
									undo_alert.find(".close").click();
								}
								frappe
									.xcall(
										"frappe.core.doctype.communication.email.undo_email_send",
										{ communication_name: communication_name }
									)
									.then((d) => {
										if (me.frm) {
											me.frm.reload_doc();
										}

										// Reopen the composer with the recovered data
										new frappe.views.CommunicationComposer({
											doc: d.doc,
											subject: d.subject,
											recipients: d.recipients,
											cc: d.cc,
											bcc: d.bcc,
											message: d.content,
											sender: d.sender,
											read_receipt: d.send_read_receipt,
											attachments: d.attachments,
											frm: me.frm,
										});

										frappe.show_alert({
											message: __("Email sending undone"),
											indicator: "blue",
										});
									});
							},
						}
					);

					// try the success callback if it exists
					if (me.success) {
						try {
							me.success(r);
						} catch (e) {
							console.log(e);
						}
					}
				} else {
					frappe.msgprint(
						__("There were errors while sending email. Please try again.")
					);

					// try the error callback if it exists
					if (me.error) {
						try {
							me.error(r);
						} catch (e) {
							console.log(e);
						}
					}
				}
			},
		});
	}
};
