// Copyright (c) 2024, TI Sin Problemas and contributors
// For license information, please see license.txt

function promptBeforeStamp(frm) {
	frappe.prompt(
		[
			{
				label: __("Digital Signing Certificate"),
				fieldname: "certificate",
				fieldtype: "Link",
				options: "Digital Signing Certificate",
				filters: { company: frm.doc.company },
			},
		],
		async ({ certificate }) => {
			await frm.call({
				method: "stamp_cfdi",
				doc: frm.doc,
				args: { certificate },
				freeze: true,
				freeze_message: __("Stamping CFDI..."),
			});
			frm.reload_doc();
		},
		__("Select a Certificate to sign the CFDI")
	);
}

function stampCfdi(frm) {
	const zeroAmountItems = frm.doc.items.filter((item) => item.amount === 0);

	if (zeroAmountItems.length > 0) {
		frappe.confirm(
			__("Items with amount of 0 won't be included in the CFDI. Do you want to continue?"),
			() => {
				promptBeforeStamp(frm);
			}
		);
	} else {
		promptBeforeStamp(frm);
	}
}

async function checkCancellationStatus(frm) {
	await frm.call("check_cancellation_status");
}

function cancel(frm) {
	const { mx_stamped_xml, cancellation_reason, requires_relationship, substitute_invoice } =
		frm.doc;

	if (mx_stamped_xml) {
		if (!cancellation_reason) {
			const msg = __("A Cancellation Reason is required to cancel this sales invoice.");
			frappe.throw(msg);
		}

		if (requires_relationship && !substitute_invoice) {
			const msg = __("The Cancellation Reason requires a substitute invoice.");
			frappe.throw(msg);
		}

		frappe.prompt(
			[
				{
					label: __("Digital Signing Certificate"),
					fieldname: "certificate",
					fieldtype: "Link",
					options: "Digital Signing Certificate",
					filters: { company: frm.doc.company },
				},
			],
			async ({ certificate }) => {
				await frappe.call({
					method: "cancel",
					doc: frm.doc,
					args: { certificate },
					btn: $(`button[data-label="${__("Cancel")}"]`),
					freeze: true,
				});
				frm.reload_doc();
			},
			__("Select a Certificate to sign the CFDI")
		);
	}
}

/**
 * Add buttons to download CFDI files
 *
 * @param {frappe.ui.form.Form} frm
 * @param {string} dt
 * @param {string} dn
 */
function addDownloadCFDIBtns(frm, dt, dn) {
	const cfdiActionsGroup = __("CFDI Actions");

	frm.add_custom_button(
		__("View PDF file"),
		() => window.open(`/api/v2/document/${dt}/${dn}/method/view_pdf`),
		cfdiActionsGroup
	);

	frm.add_custom_button(
		__("Download CFDI files"),
		() => {
			window.location.href = `/api/v2/document/${dt}/${dn}/method/download_cfdi_files`;
		},
		cfdiActionsGroup
	);
}

/**
 * Hook executed on form refresh
 *
 * @param {frappe.ui.form.Form} frm - The form object
 * @param {string} dt - The doctype
 * @param {string} dn - The doctype name
 */
function refresh(frm, dt, dn) {
	const { docstatus, mx_stamped_xml, cancellation_acknowledgement } = frm.doc;

	if (mx_stamped_xml) {
		erpnext_mexico_compliance.utils.overrideEmailDocFunction(frm);
		addDownloadCFDIBtns(frm, dt, dn);
	}

	switch (docstatus) {
		case 1:
			if (mx_stamped_xml) {
				frm.page.set_secondary_action(__("Cancel"), () => cancel(frm));
			} else {
				frm.add_custom_button(__("Stamp CFDI"), () => stampCfdi(frm));
			}

			if (cancellation_acknowledgement) {
				frm.add_custom_button(__("Check Cancellation Status"), () =>
					checkCancellationStatus(frm)
				);
			}

			break;
	}
}

/**
 * Hook executed on form setup
 *
 * @param {frappe.ui.form.Form} frm - The form object
 */
function setup(frm) {
	frm.set_query("mx_cfdi_use", (doc) => {
		if (!doc.customer) return {};
		return {
			query: "erpnext_mexico_compliance.controllers.queries.cfdi_use_query",
			filters: { customer: doc.customer },
		};
	});

	frm.set_query("substitute_invoice", (doc) => {
		return {
			filters: [
				["name", "!=", doc.name],
				["mx_stamped_xml", "is", "set"],
			],
		};
	});
}

function downloadCancellationAcknowledgement(frm) {
	window.open(
		"/api/method/erpnext_mexico_compliance.api.v1.download_cancellation_acknowledgement?doctype=Sales%20Invoice&docname=" +
			frm.doc.name
	);
}

frappe.ui.form.on("Sales Invoice", {
	refresh,
	setup,
	mx_download_acknowledgement: downloadCancellationAcknowledgement,
});
