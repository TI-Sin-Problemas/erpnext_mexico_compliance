// Copyright (c) 2024, TI Sin Problemas and contributors
// For license information, please see license.txt

function stampCfdi() {
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
    },
    __("Select a Certificate to sign the CFDI")
  );
}

async function attachFile(frm, ext) {
  const functionMap = { pdf: "attach_pdf", xml: "attach_xml" };

  try {
    const { message } = await frm.call(functionMap[ext]);
    const { file_name } = message;
    frappe.show_alert({
      message: __("File {0} attached", [file_name]),
      indicator: "green",
    });
    frm.reload_doc();
  } catch (error) {
    const { responseJSON } = error;
    frappe.throw(responseJSON ? responseJSON.exception : error);
  }
}

const cfdiActionsGroup = __("CFDI Actions");

async function addAttachPdfButton(frm) {
  const { message: hasFile } = await frm.call("has_file", {
    file_name: `${frm.doc.name}_CFDI.pdf`,
  });

  if (!hasFile) {
    frm.add_custom_button(
      __("Attach PDF"),
      async () => await attachFile(frm, "pdf"),
      cfdiActionsGroup
    );
  }
}

async function addAttachXmlButton(frm) {
  const { message: hasFile } = await frm.call("has_file", {
    file_name: `${frm.doc.name}_CFDI.xml`,
  });

  if (!hasFile) {
    frm.add_custom_button(
      __("Attach XML"),
      async () => await attachFile(frm, "xml"),
      cfdiActionsGroup
    );
  }
}

async function refresh(frm) {
  const { docstatus, mx_stamped_xml, name } = frm.doc;

  if (docstatus == 1 && !mx_stamped_xml) {
    frm.add_custom_button(__("Stamp CFDI"), stampCfdi);
  }

  if (mx_stamped_xml) {
    await addAttachPdfButton(frm);
    await addAttachXmlButton(frm);
  }
}

function setup(frm) {
  frm.set_query("mx_cfdi_use", (doc, docType, docName) => {
    return {
      query: "erpnext_mexico_compliance.controllers.queries.cfdi_use_query",
      filters: { customer: doc.customer },
    };
  });
}

frappe.ui.form.on("Sales Invoice", {
  refresh,
  setup,
});
