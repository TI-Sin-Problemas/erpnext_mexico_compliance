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

frappe.ui.form.on("CFDI PDF Template", {
  print_example(frm, cdt, cdn) {
    if (cdn.startsWith("new")) {
      frappe.throw(__("Please save the CFDI PDF Template first"));
    }
    const url = `/api/method/erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.cfdi_pdf_template.cfdi_pdf_template.print_example?docname=${cdn}`;
    window.open(url);
  },
  async load_css_sample(frm, cdt, cdn) {
    const { message } = await frappe.call({
      method: "get_sample_css",
      doc: frappe.get_doc(cdt, cdn),
    });
    frappe.model.set_value(cdt, cdn, "css_styles", message);
  },
  async load_content_sample(frm, cdt, cdn) {
    const { message } = await frappe.call({
      method: "get_sample_content",
      doc: frappe.get_doc(cdt, cdn),
    });
    frappe.model.set_value(cdt, cdn, "content_html", message);
  },
});
