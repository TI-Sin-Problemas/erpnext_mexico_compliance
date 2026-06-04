"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt
"""

from .catalogs import CatalogManager


def update_tax_regimes():
	manager = CatalogManager()
	manager.update_doctype("SAT Tax Regime")


def update_cfdi_uses():
	manager = CatalogManager()
	manager.update_doctype("SAT CFDI Use")


def update_payment_options():
	manager = CatalogManager()
	manager.update_doctype("SAT Payment Option")


def update_payment_methods():
	manager = CatalogManager()
	manager.update_doctype("SAT Payment Method")


def update_product_or_service_keys():
	manager = CatalogManager()
	manager.update_doctype("SAT Product or Service Key")


def update_relationship_types():
	manager = CatalogManager()
	manager.update_doctype("SAT Relationship Type")


def update_units_of_measure():
	manager = CatalogManager()
	manager.update_doctype("SAT UOM Key")
