import typing as t

import click
import frappe

from erpnext_mexico_compliance.utils.cfdi import get_uuid_from_xml


def set_missing_uuids(doctype: t.Literal["Sales Invoice", "Payment Entry"]):
	"""Sets the 'mx_uuid' field of all Sales Invoices or Payment Entries with the UUID extracted from their
	'mx_stamped_xml' field.

	Args:
		doctype (t.Literal["Sales Invoice", "Payment Entry"]): The doctype of the documents.
	"""
	FILTERS = {"mx_stamped_xml": ["is", "set"], "mx_uuid": ["is", "not set"]}

	qty = frappe.db.count("Sales Invoice", filters=FILTERS)
	if qty:
		query = frappe.qb.get_query(  # type: ignore
			doctype, fields=["name", "mx_stamped_xml"], filters=FILTERS
		)

		with click.progressbar(query.run(), label=f"Setting {doctype} missing UUIDs") as bar:
			for name, xml in bar:
				frappe.db.set_value("Sales Invoice", name, "mx_uuid", get_uuid_from_xml(xml))
