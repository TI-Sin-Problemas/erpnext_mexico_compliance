# Copyright (c) 2025, TI Sin Problemas and contributors
# For license information, please see license.txt

from decimal import Decimal

import frappe
from frappe import _
from satcfdi.cfdi import CFDI


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("Sales Invoice"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
        },
        {
            "fieldname": "grand_total",
            "label": _("Grand Total"),
            "fieldtype": "Currency",
        },
        {
            "fieldname": "cfdi_total",
            "label": _("CFDI Grand Total"),
            "fieldtype": "Currency",
        },
        {
            "fieldname": "difference",
            "label": _("Difference"),
            "fieldtype": "Currency",
        },
    ]


def get_data(filters=None):
    filters = filters or {}
    filters.update(
        {
            "mx_stamped_xml": ["is", "set"],
            "posting_date": ["between", filters.pop("date_range")],
        }
    )

    data = frappe.get_all(
        "Sales Invoice",
        fields=["name", "grand_total", "mx_stamped_xml"],
        filters=filters,
        order_by="posting_date asc",
    )

    ret = []
    for d in data:
        d["grand_total"] = Decimal(str(d["grand_total"]))
        cfdi = CFDI.from_string(d["mx_stamped_xml"].encode("utf-8"))
        d["cfdi_total"] = cfdi["Total"]
        d["difference"] = abs(d["grand_total"] - d["cfdi_total"])

        if d["difference"] > 0:
            ret.append(d)

    return ret


def execute(filters=None):
    return get_columns(), get_data(filters)
