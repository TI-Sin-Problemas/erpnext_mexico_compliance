// Copyright (c) 2025, TI Sin Problemas and contributors
// For license information, please see license.txt

frappe.query_reports["Stamped Invoice Differences"] = {
  filters: [
    {
      fieldname: "date_range",
      label: __("Date Range"),
      fieldtype: "Date Range",
      reqd: 1,
      default: [frappe.datetime.month_start(), frappe.datetime.month_end()],
    },
  ],
};
