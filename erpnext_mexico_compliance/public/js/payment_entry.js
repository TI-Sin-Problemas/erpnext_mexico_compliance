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
      const { message } = await frm.call("stamp_cfdi", { certificate });
      frappe.show_alert({ message, indicator: "green" });
      frm.reload_doc();
    },
    __("Select a Certificate to sign the CFDI")
  );
}

function refresh(frm) {
  const { docstatus } = frm.doc;
  switch (docstatus) {
    case 1:
      frm.add_custom_button(__("Stamp CFDI"), () => stampCfdi(frm));
      break;
  }
}

frappe.ui.form.on("Payment Entry", {
  refresh,
});
