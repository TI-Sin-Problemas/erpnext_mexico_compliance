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

    def _get_relationship_types(self, *, as_dict=False):
        """Retrieves a list of relationship types from the database.

        Args:
            as_dict (bool, optional): If True, returns the result as a list of dictionaries. Defaults to False.

        Returns:
            list[tuple] | list[dict]: A list of relationship types, either as a list of tuples or a list of dictionaries.
        """
        table = Table("cfdi_40_tipos_relaciones")
        fields = [table.id, table.texto, table.vigencia_desde]
        query_result = self._get_query_result(table, fields)

        if as_dict:
            return self._get_query_result_as_dict(fields, query_result)

        return query_result

    def _update_relationship_types(self):
        """Updates the SAT Relationship Type documents based on the data retrieved from the database."""
        data = self._get_relationship_types(as_dict=True)
        doctype = "SAT Relationship Type"

        for d in data:
            has_changed = False

            try:
                doc = frappe.get_doc(doctype, d["id"])
            except frappe.DoesNotExistError:
                doc = frappe.new_doc(doctype, code=d["id"])

            if doc.description != d["texto"]:
                doc.description = d["texto"]
                has_changed = True

            if date_diff(doc.valid_from, d["vigencia_desde"]):
                doc.valid_from = d["vigencia_desde"]
                has_changed = True

            if has_changed or doc.is_new():
                doc.save()

        frappe.db.commit()

    def update_doctype(self, doctype: str):
        match doctype:
            case "SAT Relationship Type":
                self._update_relationship_types()
            case _:
                raise ValueError(f"Unsupported doctype: {doctype}")
