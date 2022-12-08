"""Setup functions"""
import os
import time
import frappe


logger = frappe.logger("mexico_compliance")


def install_big_fixtures():
    """Install long running fixtures"""

    path = frappe.get_app_path("mexico_compliance", "fixtures_after_install")
    print("Importing long running fixtures. This may take a while.")
    for file in os.listdir(path):
        fixture = f"{path}/{file}"

        print("🚛 Importing", file)
        logger.info("Importing %s", file)

        timer_start = time.perf_counter()
        frappe.import_doc(fixture)
        timer_end = time.perf_counter()
        proc_time = f"{timer_end - timer_start:0.4f}"

        print(f"⏱️ {file} took {proc_time} seconds")
        logger.info("%s took %s seconds", file, proc_time)
