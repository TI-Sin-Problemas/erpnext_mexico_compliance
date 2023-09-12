"""Installation tasks"""
import os

import frappe
from frappe.core.doctype.data_import.importer import Importer, ImportFile

from .hooks import app_name


# TODO: Replace with frappe.core.doctype.data_import.data_import.import_file
#       when commit c6b1b02 is merged into version-14
def import_local_file(
    doctype, file_path, import_type, submit_after_import=False, console=False
):
    """
    Import documents in from CSV or XLSX using data import.

    :param doctype: DocType to import
    :param file_path: Path to .csv, .xls, or .xlsx file to import
    :param import_type: One of "Insert" or "Update"
    :param submit_after_import: Whether to submit documents after import
    :param console: Set to true if this is to be used from command line. Will print errors or progress to stdout.
    """

    class LocalImportFile(ImportFile):
        def read_file(self, file_path: str):
            _, extn = super().read_file(file_path)
            file_content = frappe.read_file(file_path, True)
            return file_content, extn

    class LocalImporter(Importer):
        def __init__(
            self,
            doctype,
            data_import=None,
            file_path=None,
            import_type=None,
            console=False,
        ):
            self.doctype = doctype
            self.console = console

            self.data_import = data_import
            if not self.data_import:
                self.data_import = frappe.get_doc(doctype="Data Import")
                if import_type:
                    self.data_import.import_type = import_type

            self.template_options = frappe.parse_json(
                self.data_import.template_options or "{}"
            )
            self.import_type = self.data_import.import_type

            self.import_file = LocalImportFile(
                doctype,
                file_path or data_import.google_sheets_url or data_import.import_file,
                self.template_options,
                self.import_type,
            )

    data_import = frappe.new_doc("Data Import")
    data_import.submit_after_import = submit_after_import
    data_import.import_type = (
        "Insert New Records"
        if import_type.lower() == "insert"
        else "Update Existing Records"
    )

    i = LocalImporter(
        doctype=doctype, file_path=file_path, data_import=data_import, console=console
    )
    i.import_data()


def after_sync():
    """Run tasks after migration sync"""
    print("Importing SAT Product or Service Key data...")
    fixtures_directory = "fixtures_csv"
    files = sorted(os.listdir(frappe.get_app_path(app_name, fixtures_directory)))
    for file in files:
        print("\nLoading", f"{file}...")
        file_path = frappe.get_app_path(app_name, fixtures_directory, file)
        import_local_file(
            "SAT Product or Service Key", file_path, "Insert", console=True
        )
