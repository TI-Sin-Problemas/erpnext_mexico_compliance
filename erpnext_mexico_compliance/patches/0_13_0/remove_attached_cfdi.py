import time

import frappe
from frappe.utils import cint, get_sites
from frappe.utils.background_jobs import MAX_QUEUED_JOBS, get_queue

CHUNK_SIZE = 5000
BATCH_SIZE = 200

BASE_FILTERS = [
	["file_name", "like", "%CFDI%"],
	"and",
	[["file_name", "like", "%.pdf"], "or", ["file_name", "like", "%.xml"]],
	"and",
	["attached_to_doctype", "in", ["Sales Invoice", "Payment Entry"]],
]


def _activate_auto_commit(func):
	"""Temporarily set auto_commit_on_many_writes to True."""

	def wrapper(*args, **kwargs):
		old = frappe.db.auto_commit_on_many_writes
		frappe.db.auto_commit_on_many_writes = True
		try:
			func(*args, **kwargs)
		finally:
			frappe.db.auto_commit_on_many_writes = old

	return wrapper


def _wait_until_queue_free(queue_name="default"):
	"""Block until the given queue has room below the overload threshold."""
	max_jobs = cint(frappe.conf.get("max_queued_jobs")) or MAX_QUEUED_JOBS
	max_jobs += len(get_sites()) * 50

	q = get_queue(queue_name)
	sleep_time = 5
	while q.count >= max_jobs:
		time.sleep(sleep_time)
		q = get_queue(queue_name)
		sleep_time = min(sleep_time * 2, 60)


def execute():
	"""Enqueue removal of attached CFDI files as a background job."""
	frappe.enqueue(
		"erpnext_mexico_compliance.patches.0_13_0.remove_attached_cfdi.remove_cfdi_files_background",
		queue="long",
	)
	print("Enqueued CFDI cleanup job. Check RQ Jobs > Long Jobs for progress.")


@_activate_auto_commit
def remove_cfdi_files_background(last_name=None):
	"""Remove a chunk of attached CFDI files, then re-enqueue for the next chunk."""
	last_committed = last_name
	try:
		filters = list(BASE_FILTERS)
		if last_name:
			filters += ["and", ["name", ">", last_name]]

		if not last_name:
			total = frappe.db.count("File", filters=filters)
			if not total:
				print("No CFDI files to delete.")
				return
			print(f"Deleting {total} CFDI files")

		file_names = frappe.get_all(
			"File",
			filters=filters,
			pluck="name",
			order_by="file_name asc",
			limit=CHUNK_SIZE,
		)

		if not file_names:
			print("Done. Deleted all CFDI files.")
			return

		for idx, file_name in enumerate(file_names):
			frappe.delete_doc("File", file_name)
			if (idx + 1) % BATCH_SIZE == 0:
				frappe.db.commit()
				last_committed = file_name
				_wait_until_queue_free("default")

		frappe.db.commit()
		last_committed = file_names[-1]
		print(f"Progress: deleted up to {file_names[-1]}")

		if len(file_names) == CHUNK_SIZE:
			_wait_until_queue_free("long")
			for _attempt in range(3):
				try:
					frappe.enqueue(
						"erpnext_mexico_compliance.patches.0_13_0.remove_attached_cfdi.remove_cfdi_files_background",
						queue="long",
						last_name=file_names[-1],
					)
					break
				except frappe.QueueOverloaded:
					if _attempt == 2:
						raise
					time.sleep(5)
					_wait_until_queue_free("long")
		else:
			print("Done. Deleted all CFDI files.")
	except Exception:
		import traceback

		traceback.print_exc()
		if last_committed != last_name:
			_wait_until_queue_free("long")
			frappe.enqueue(
				"erpnext_mexico_compliance.patches.0_13_0.remove_attached_cfdi.remove_cfdi_files_background",
				queue="long",
				last_name=last_committed,
			)
			print(f"Failure: recovery enqueued from {last_committed}")
		else:
			print("Failure: no committed progress, nothing to recover.")
		raise
