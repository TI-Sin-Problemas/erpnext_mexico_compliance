"""Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe
from erpnext.controllers.queries import get_fields
from frappe.desk.reportview import get_filters_cond


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def cfdi_use_query(doctype, txt, searchfield, start, page_len, filters: dict):
	doctype = "SAT CFDI Use"
	customer = filters.pop("customer", None)
	meta = frappe.get_meta(doctype)

	if customer:
		customer = frappe.get_doc("Customer", customer)
		filters.update({"tax_regimes.tax_regime": customer.mx_tax_regime})

	if txt:
		filters[searchfield] = ["like", f"%{txt}%"]

	query = frappe.qb.get_query(
		doctype,
		fields=get_fields(doctype, ["name"]),
		filters=filters,
		limit=page_len,
		offset=start,
		order_by=f"{meta.sort_field} {meta.sort_order}",
	)
	return query.run()
