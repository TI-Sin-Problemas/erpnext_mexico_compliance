"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import bz2
import os
import sqlite3
import tempfile

import frappe
import requests
from frappe.utils import date_diff
from pypika import Query, Table

from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.sat_cfdi_use.sat_cfdi_use import (
    SATCFDIUse,
)
from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.sat_product_or_service_key.sat_product_or_service_key import (
    SATProductorServiceKey,
)
from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.sat_relationship_type.sat_relationship_type import (
    SATRelationshipType,
)


class CatalogManager:
    def __init__(self):
        self.db_path = self.download_db()
        self.connection = sqlite3.connect(self.db_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()
        os.remove(self.db_path)

    def download_db(self):
        url = "https://github.com/phpcfdi/resources-sat-catalogs/releases/latest/download/catalogs.db.bz2"
        response = requests.get(url=url)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            decompressed = bz2.decompress(response.content)
            f.write(decompressed)
        return f.name

    def _get_query_result_as_dict(self, fields: list, items: list[tuple]):
        """Transforms a query result into a list of dictionaries.

        Args:
            fields (list): A list of pypika fields.
            items (list[tuple]): A list of query result items.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a row of data and its values are mapped to the corresponding field name.
        """
        result = []
        for row in items:
            item = {}
            for idx, field in enumerate(fields):
                item[field.name] = row[idx]
            result.append(item)
        return result

    def _get_query_result(self, table: Table, fields: list):
        """Executes a query and returns the result.

        Args:
            table (Table): The table to query.
            fields (list): A list of pypika fields to select.

        Returns:
            list[tuple]: The result of the query.
        """
        cur = self.connection.cursor()
        query = Query.from_(table).select(*fields)
        cur.execute(str(query))
        return cur.fetchall()

    def _get_items(
        self, table: Table, fields: list[str], as_dict: bool = False
    ) -> list[tuple] | list[dict]:
        """Retrieves items from a given table.

        Args:
            table (Table): The table to query.
            fields (list[str]): A list of field names to select.
            as_dict (bool, optional): If True, returns the result as a list of dictionaries. Defaults to False.

        Returns:
            list[tuple] | list[dict]: A list of items, either as a list of tuples or a list of dictionaries.
        """
        query_result = self._get_query_result(table, fields)

        if as_dict:
            return self._get_query_result_as_dict(fields, query_result)

        return query_result

    def _update_relationship_types(self):
        """Updates the SAT Relationship Type documents based on the data retrieved from the database."""
        table = Table("cfdi_40_tipos_relaciones")
        fields = [table.id, table.texto, table.vigencia_desde]
        data: list[dict] = self._get_items(table=table, fields=fields, as_dict=True)  # type: ignore
        doctype = "SAT Relationship Type"

        for d in data:
            has_changed = False

            try:
                doc: SATRelationshipType = frappe.get_doc(doctype, d["id"])  # type: ignore
            except frappe.DoesNotExistError:
                doc: SATRelationshipType = frappe.new_doc(doctype, code=d["id"])  # type: ignore

            if doc.description != d["texto"]:
                doc.description = d["texto"]
                has_changed = True

            if date_diff(doc.valid_from, d["vigencia_desde"]):  # type: ignore
                doc.valid_from = d["vigencia_desde"]
                has_changed = True

            if has_changed or doc.is_new():
                doc.save()

        frappe.db.commit()

    def _update_product_services(self):
        """Updates the SAT Product or Service Key documents based on the data retrieved from the database.

        The SAT Product or Service Key documents are updated based on the data retrieved from the database.
        If a document does not exist, it is created. If a document exists and the description has changed, the description is updated.
        """
        table = Table("cfdi_40_productos_servicios")
        fields = [table.id, table.texto]
        data: list[dict] = self._get_items(table=table, fields=fields, as_dict=True)  # type: ignore
        doctype = "SAT Product or Service Key"

        for d in data:
            has_changed = False
            key = d["id"]
            description = d["texto"]

            try:
                doc: SATProductorServiceKey = frappe.get_doc(doctype, {"key": key})  # type: ignore
            except frappe.DoesNotExistError:
                doc: SATProductorServiceKey = frappe.new_doc(doctype, key=key)  # type: ignore

            if doc.description != description:
                doc.description = description
                has_changed = True

            if has_changed or doc.is_new():
                doc.save()

        frappe.db.commit()

    def _update_cfdi_uses(self):
        """Updates the SAT CFDI Use documents based on the data retrieved from the database."""
        table = Table("cfdi_40_usos_cfdi")
        fields = [table.id, table.texto, table.regimenes_fiscales_receptores]
        data: list[dict] = self._get_items(table=table, fields=fields, as_dict=True)  # type: ignore
        doctype = "SAT CFDI Use"

        for d in data:
            has_changed = False
            key = d["id"]
            description = d["texto"]
            tax_regimes = [
                r.strip() for r in d["regimenes_fiscales_receptores"].split(",")
            ]

            try:
                doc: SATCFDIUse = frappe.get_doc(doctype, {"key": key})  # type: ignore
            except frappe.DoesNotExistError:
                doc: SATCFDIUse = frappe.new_doc(doctype, key=key)  # type: ignore

            if doc.description != description:
                doc.description = description
                has_changed = True

            doc_tax_regimes = [tr.tax_regime for tr in doc.tax_regimes]
            for regime in tax_regimes:
                if regime not in doc_tax_regimes:
                    doc.append("tax_regimes", {"tax_regime": regime})
                    has_changed = True

            if has_changed or doc.is_new():
                doc.save()

        frappe.db.commit()

    def update_doctype(self, doctype: str):
        match doctype:
            case "SAT CFDI Use":
                self._update_cfdi_uses()
            case "SAT Product or Service Key":
                self._update_product_services()
            case "SAT Relationship Type":
                self._update_relationship_types()
            case _:
                raise ValueError(f"Unsupported doctype: {doctype}")
