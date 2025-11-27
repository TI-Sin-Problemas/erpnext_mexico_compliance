"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt
"""

from .catalogs import CatalogManager


def update_sat_catalogs():
    manager = CatalogManager()
    manager.update_doctype("SAT CFDI Use")
    manager.update_doctype("SAT Product or Service Key")
    manager.update_doctype("SAT Relationship Type")
