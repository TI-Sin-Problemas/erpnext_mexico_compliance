"""Installation tasks"""
import os

import frappe
from frappe.core.doctype.data_import.data_import import import_file

from .hooks import app_name

logger = frappe.logger("erpnext_mexico_compliance.install")

def after_sync():
    """Run tasks after migration sync"""
    logger.info("Importing SAT Product or Service Key data...")
    fixtures_directory = "fixtures_csv"
    files = sorted(os.listdir(frappe.get_app_path(app_name, fixtures_directory)))
    for file in files:
        logger.info(f"Loading {file}...")
        file_path = frappe.get_app_path(app_name, fixtures_directory, file)
        import_file("SAT Product or Service Key", file_path, "Insert", console=True)
