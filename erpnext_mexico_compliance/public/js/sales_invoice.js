// Copyright (c) 2024, TI Sin Problemas and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
  setup(frm) {
    frm.set_query("mx_cfdi_use", (doc, docType, docName) => {
      return {
        query: "erpnext_mexico_compliance.controllers.queries.cfdi_use_query",
        filters: { customer: doc.customer },
      };
    });
  },
});
