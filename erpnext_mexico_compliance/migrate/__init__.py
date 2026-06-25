from . import after_migrate


def execute_after_migrate_tasks():
	after_migrate.set_missing_uuids("Sales Invoice")
	after_migrate.set_missing_uuids("Payment Entry")
	after_migrate.enqueue_sat_catalogs_update()
	after_migrate.set_cfdi_settings()
	after_migrate.set_missing_cfdi_status("Sales Invoice")
	after_migrate.set_missing_cfdi_status("Payment Entry")
