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
    const { message } = error;
    frappe.throw(message ? message : error);
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

function cancel(frm) {
  const {
    mx_stamped_xml,
    cancellation_reason,
    requires_relationship,
    substitute_invoice,
  } = frm.doc;

  if (mx_stamped_xml) {
    if (!cancellation_reason) {
      const msg = __(
        "A Cancellation Reason is required to cancel this sales invoice."
      );
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
        const { message: cfdi_msg } = await frm.call("cancel_cfdi", {
          certificate,
        });
        frappe.show_alert({ message: cfdi_msg, indicator: "green" });
        const { message: cancelled } = await frm.call("cancel");
        frappe.show_alert({ message: cancelled, indicator: "green" });
        frm.reload_doc();
      },
      __("Select a Certificate to sign the CFDI")
    );
  }
}

function refresh(frm) {
  const { docstatus, mx_stamped_xml } = frm.doc;

  if (mx_stamped_xml) {
    addAttachPdfButton(frm);
    addAttachXmlButton(frm);
  }

  switch (docstatus) {
    case 1:
      if (mx_stamped_xml) {
        frm.page.set_secondary_action(__("Cancel"), () => cancel(frm));
      } else {
        frm.add_custom_button(__("Stamp CFDI"), () => stampCfdi(frm));
      }
      break;
  }
}

function setup(frm) {
  frm.set_query("mx_cfdi_use", (doc) => {
    return {
      query: "erpnext_mexico_compliance.controllers.queries.cfdi_use_query",
      filters: { customer: doc.customer },
    };
  });

  frm.set_query("substitute_invoice", (doc) => {
    return {
      filters: [
        ["name", "!=", doc.name],
        ["customer", "=", doc.customer],
        ["mx_stamped_xml", "!=", ""],
      ],
    };
  });
}

frappe.ui.form.on("Sales Invoice", {
  refresh,
  setup,
});
