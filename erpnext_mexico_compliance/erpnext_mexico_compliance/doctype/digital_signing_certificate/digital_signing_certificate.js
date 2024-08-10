// Copyright (c) 2024, TI Sin Problemas and contributors
// For license information, please see license.txt

frappe.ui.form.on("Digital Signing Certificate", {
  refresh(frm) {
    if (frm.doc.certificate && frm.doc.key && frm.doc.password) {
      frm.add_custom_button(__("Validate Certificate"), () => {
        frm.call("validate_certificate");
      });
    }
  },
});
