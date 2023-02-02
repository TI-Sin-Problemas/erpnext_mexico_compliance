"""Setup functions"""
import json
import math
import os
import re
import frappe


logger = frappe.logger("erpnext_mexico_compliance")


def split_big_fixtures():
    """Split big fixtures to avoid to many writes error"""

    src_path = frappe.get_app_path("erpnext_mexico_compliance", "big_fixtures")
    target_path = frappe.get_app_path("erpnext_mexico_compliance", "fixtures")

    for file in os.listdir(src_path):
        file_path = f"{src_path}/{file}"
        max_fixture_qty = 20000
        fixtures = frappe.get_file_json(file_path)
        fixtures_count = len(fixtures)
        iterations = math.ceil(fixtures_count / max_fixture_qty)

        start = 0
        for i in range(iterations):
            iteration = i + 1
            end_limit = iteration * max_fixture_qty
            end = end_limit if end_limit < fixtures_count else fixtures_count

            with open(
                f"{target_path}/{file}.{start}.{end}.json", "w+", encoding="utf-8"
            ) as target_file:
                target_file.write(
                    json.dumps(fixtures[start:end], ensure_ascii=False, indent=1)
                )

            start = end


def remove_splitted_fixtures():
    """Remove splitted fixtures"""

    src_path = frappe.get_app_path("erpnext_mexico_compliance", "fixtures")
    pattern = re.compile(r".*\.(\d+)\.(\d+)\.json")

    for file in os.listdir(src_path):
        if pattern.match(file):
            os.unlink(f"{src_path}/{file}")
