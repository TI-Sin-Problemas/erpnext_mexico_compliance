// Copyright (c) 2024, TI Sin Problemas and contributors
// For license information, please see license.txt

function stampCfdi(frm) {
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

async function checkCancellationStatus(frm) {
	await frm.call("check_cancellation_status");
}

function cancel(frm) {
	const {
		mx_stamped_xml,
		cancellation_reason,
		requires_relationship,
		substitute_payment_entry,
	} = frm.doc;

	if (mx_stamped_xml) {
		if (!cancellation_reason) {
			const msg = __("A Cancellation Reason is required to cancel this payment entry.");
			frappe.throw(msg);
		}
	}

	if (requires_relationship && !substitute_payment_entry) {
		const msg = __("The Cancellation Reason requires a substitute payment entry.");
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
			const { message: cfdi_msg } = await frappe.call({
				method: "cancel",
				doc: frm.doc,
				args: { certificate },
				btn: $(`button[data-label="${__("Cancel")}"]`),
				freeze: true,
			});
			frappe.show_alert({ message: cfdi_msg, indicator: "green" });
			frm.reload_doc();
		},
		__("Select a Certificate to sign the CFDI")
	);
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

function setup(frm) {
	frm.set_query("substitute_payment_entry", (doc) => {
		return {
			filters: [
				["name", "!=", doc.name],
				["mx_stamped_xml", "is", "set"],
			],
		};
	});

	frm.set_query("mode_of_payment", () => {
		return {
			filters: {
				sat_payment_method: ["!=", "99"],
			},
		};
	});
}

frappe.ui.form.on("Payment Entry", {
	refresh,
	setup,
});
