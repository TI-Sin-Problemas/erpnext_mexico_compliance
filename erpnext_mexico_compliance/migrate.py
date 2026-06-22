"""Migration tasks"""

import frappe


def set_cfdi_settings():
	"""Sets the CFDI Stamping Settings to the current site configuration."""
	settings = frappe.get_single("CFDI Stamping Settings")
	settings.save(ignore_version=True)
