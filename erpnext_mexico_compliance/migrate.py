"""Migration tasks"""

import frappe

from . import sat


def enqueue_sat_catalogs_update():
	"""Queues a task to update the SAT Catalogs for the current site."""
	frappe.enqueue(sat.update_tax_regimes)
	frappe.enqueue(sat.update_cfdi_uses)
	frappe.enqueue(sat.update_payment_options)
	frappe.enqueue(sat.update_payment_methods)
	frappe.enqueue(sat.update_product_or_service_keys, queue="long")
	frappe.enqueue(sat.update_relationship_types)
	frappe.enqueue(sat.update_units_of_measure, queue="long")
	print(f"Queued update of SAT Catalogs for {frappe.local.site}")


def set_cfdi_settings():
	"""Sets the CFDI Stamping Settings to the current site configuration."""
	settings = frappe.get_single("CFDI Stamping Settings")
	settings.save(ignore_version=True)
