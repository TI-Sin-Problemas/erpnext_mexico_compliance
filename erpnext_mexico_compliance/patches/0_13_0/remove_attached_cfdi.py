import time

import frappe
from frappe.utils import cint, get_sites, update_progress_bar
from frappe.utils.background_jobs import MAX_QUEUED_JOBS, get_queue
from rq.timeouts import JobTimeoutException

from erpnext_mexico_compliance.utils.decorators import activate_auto_commit

BATCH_SIZE = 200
FILTERS = [
	[["file_name", "like", "%_CFDI.pdf"], "or", ["file_name", "like", "%_CFDI.xml"]],
	"and",
	["attached_to_doctype", "in", ["Sales Invoice", "Payment Entry"]],
]


def get_max_jobs():
	max_jobs = cint(frappe.conf.get("max_queued_jobs")) or MAX_QUEUED_JOBS
	max_jobs += len(get_sites()) * 50

	# Substract BATCH_SIZE so the burst of delete_dynamic_links jobs stays under the hard limit
	max_jobs -= BATCH_SIZE

	return max_jobs


def _wait_until_queue_free(queue_name="default"):
	"""Block until the given queue has room below the overload threshold."""
	max_jobs = get_max_jobs()
	q = get_queue(queue_name)
	sleep_time = 5
	while q.count >= max_jobs:
		print(
			f"Queue {queue_name} is almost overloaded ({q.count}). Waiting {sleep_time} seconds for next batch."
		)
		time.sleep(sleep_time)
		q = get_queue(queue_name)
		sleep_time = min(sleep_time * 2, 60)


def execute():
	"""Enqueue removal of attached CFDI files as a background job."""
	file_qty = frappe.db.count("File", filters=FILTERS)

	if file_qty > get_max_jobs():
		q = frappe.enqueue(
			"erpnext_mexico_compliance.patches.0_13_0.remove_attached_cfdi.remove_cfdi_files",
			queue="long",
		)
		print(
			f"Found {file_qty} CFDI files to remove. Enqueuing job {q.func_name}. "
			"Check RQ Jobs > Long Queue for progress."
		)
	elif file_qty > 0:
		remove_cfdi_files()


@activate_auto_commit
def remove_cfdi_files():
	try:
		while True:
			files = frappe.get_all(
				"File",
				fields=["name", "file_name"],
				filters=FILTERS,
				order_by="file_name asc",
				limit=get_max_jobs(),
			)
			if not files:
				break

			l = len(files)
			for idx, file in enumerate(files):
				frappe.delete_doc("File", file.name)
				update_progress_bar(f"Removing old CFDI files ({file.file_name[:50]})", idx, l)
				if (idx + 1) % BATCH_SIZE == 0:
					_wait_until_queue_free()
					frappe.db.commit()

			_wait_until_queue_free()
			frappe.db.commit()

	except JobTimeoutException:
		frappe.enqueue(
			"erpnext_mexico_compliance.patches.0_13_0.remove_attached_cfdi.remove_cfdi_files",
			queue="long",
		)
