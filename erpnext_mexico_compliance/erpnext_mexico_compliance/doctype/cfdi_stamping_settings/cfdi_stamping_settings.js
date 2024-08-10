// Copyright (c) 2024, TI Sin Problemas and contributors
// For license information, please see license.txt

frappe.ui.form.on("CFDI Stamping Settings", {
  refresh(frm) {
    if (
      frm.doc.signing_certificate &&
      frm.doc.signing_key &&
      frm.doc.signing_password
    ) {
      frm.add_custom_button(__("Validate Signing Certificate"), () => {
        frm.call("validate_signing_certificate");
      });
    }
  },
});
