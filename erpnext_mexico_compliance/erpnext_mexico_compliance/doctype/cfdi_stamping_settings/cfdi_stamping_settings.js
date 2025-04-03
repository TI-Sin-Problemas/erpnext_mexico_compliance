// Copyright (c) 2024, TI Sin Problemas and contributors
// For license information, please see license.txt

frappe.ui.form.on("CFDI Stamping Settings", {
  refresh(frm) {
    if (frm.doc.api_key && frm.doc.api_secret) {
      frm.add_custom_button(__("Available credits"), async () => {
        const { message } = await frm.call("get_available_credits");
        frappe.msgprint(
          __("Available credits") +
            `: ${message}<br>` +
            __("1 credit is consumed every time a CFDI gets stamped"),
          "Available credits"
        );
      });
    }
  },
});
