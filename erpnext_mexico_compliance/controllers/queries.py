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
    cfdi_use_table = "`tabSAT CFDI Use`"
    tax_regime_table = "`tabSAT CFDI Use Tax Regime`"

    if customer:
        customer = frappe.get_doc("Customer", customer)
        filters.update({"tax_regime": customer.mx_tax_regime})

    fields = [f"{cfdi_use_table}.{f}" for f in get_fields(doctype, [])]
    filters_cond = get_filters_cond(doctype, filters, [])

    item_list = frappe.db.sql(
        f"""select {", ".join(fields)} from {cfdi_use_table}
            left join {tax_regime_table} on {tax_regime_table}.parent = {cfdi_use_table}.name
            where
                {cfdi_use_table}.enabled = 1
                and (
                    {cfdi_use_table}.key_name like "%{txt}%"
                    or {cfdi_use_table}.{searchfield} like "%{txt}%"
                )
                {filters_cond}
            order by {cfdi_use_table}.{searchfield} asc
            limit {page_len} offset {start}
            """
    )
    return item_list
