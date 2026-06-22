from . import after_migrate


def execute_after_migrate_tasks():
	after_migrate.set_missing_uuids("Sales Invoice")
	after_migrate.set_missing_uuids("Payment Entry")
