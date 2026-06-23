import typing as t

import click
import frappe

from erpnext_mexico_compliance import sat
from erpnext_mexico_compliance.utils.cfdi import get_uuid_from_xml


def set_missing_uuids(doctype: t.Literal["Sales Invoice", "Payment Entry"]):
	"""Sets the 'mx_uuid' field of all Sales Invoices or Payment Entries with the UUID extracted from their
	'mx_stamped_xml' field.

	Args:
		doctype (t.Literal["Sales Invoice", "Payment Entry"]): The doctype of the documents.
	"""
	FILTERS = {"mx_stamped_xml": ["is", "set"], "mx_uuid": ["is", "not set"]}

	qty = frappe.db.count(doctype, filters=FILTERS)
	if qty:
		query = frappe.qb.get_query(  # type: ignore
			doctype, fields=["name", "mx_stamped_xml"], filters=FILTERS
		)

		with click.progressbar(query.run(), label=f"Setting {doctype} missing UUIDs") as bar:
			for name, xml in bar:
				frappe.db.set_value(doctype, name, "mx_uuid", get_uuid_from_xml(xml))


def enqueue_sat_catalogs_update():
	"""Queues a task to update the SAT Catalogs for the current site."""
	frappe.enqueue(sat.update_tax_regimes)
	frappe.enqueue(sat.update_cfdi_uses)
	frappe.enqueue(sat.update_payment_options)
	frappe.enqueue(sat.update_payment_methods)
	frappe.enqueue(sat.update_product_or_service_keys, queue="long")
	frappe.enqueue(sat.update_relationship_types)
	frappe.enqueue(sat.update_units_of_measure, queue="long")
	click.echo(f"Queued update of SAT Catalogs for {frappe.local.site}")


def set_cfdi_settings():
	"""Sets the CFDI Stamping Settings to the current site configuration."""
	settings = frappe.get_single("CFDI Stamping Settings")
	settings.save(ignore_version=True)
