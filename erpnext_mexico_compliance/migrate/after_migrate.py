import gc
import typing as t

import click
import frappe
from frappe.utils import update_progress_bar
from rq.timeouts import JobTimeoutException
from satcfdi.cfdi import CFDI

from erpnext_mexico_compliance import sat
from erpnext_mexico_compliance.controllers.common import CFDIStatus
from erpnext_mexico_compliance.utils.cfdi import get_uuid_from_xml
from erpnext_mexico_compliance.utils.decorators import activate_auto_commit
from erpnext_mexico_compliance.ws_client import get_ws_client, models


@activate_auto_commit
def set_missing_uuids(doctype: t.Literal["Sales Invoice", "Payment Entry"]):
	"""Sets the 'mx_uuid' field of all Sales Invoices or Payment Entries with the UUID extracted from their
	'mx_stamped_xml' field.

	Args:
		doctype (t.Literal["Sales Invoice", "Payment Entry"]): The doctype of the documents.
	"""
	FILTERS = {"mx_stamped_xml": ["is", "set"], "mx_uuid": ["is", "not set"]}

	query = frappe.qb.get_query(doctype, fields=["name", "mx_stamped_xml"], filters=FILTERS)
	docs = query.run()
	for idx, doc in enumerate(docs):
		name, xml = doc
		frappe.db.set_value(doctype, name, "mx_uuid", get_uuid_from_xml(xml))
		update_progress_bar(f"Setting missing UUIDs for {doctype}", idx, len(docs))


def enqueue_sat_catalogs_update():
	"""Queues a task to update the SAT Catalogs for the current site."""
	frappe.enqueue(sat.update_tax_regimes)
	frappe.enqueue(sat.update_cfdi_uses)
	frappe.enqueue(sat.update_payment_options)
	frappe.enqueue(sat.update_payment_methods)
	frappe.enqueue(sat.update_product_or_service_keys, queue="long")
	frappe.enqueue(sat.update_relationship_types)
	frappe.enqueue(sat.update_units_of_measure, queue="long")
	click.echo(f"Queued update of SAT Catalogs for {frappe.local.site}")


def set_cfdi_settings():
	"""Sets the CFDI Stamping Settings to the current site configuration."""
	settings = frappe.get_single("CFDI Stamping Settings")
	settings.save(ignore_version=True)


CHUNK_SIZE = 500


@activate_auto_commit
def _set_missing_cfdi_status(doctype: t.Literal["Sales Invoice", "Payment Entry"]):
	"""Sets the CFDI status of sales invoices and payment entries.

	Args:
		doctype (t.Literal["Sales Invoice", "Payment Entry"]): The doctype of the documents.
	"""
	test_mode = frappe.get_value("CFDI Stamping Settings", None, "test_mode")
	api = get_ws_client()

	try:
		while True:
			docs = frappe.get_all(
				doctype,
				filters={"mx_cfdi_status": ["is", "not set"], "mx_stamped_xml": ["is", "set"]},
				pluck="name",
				order_by="name",
				limit=CHUNK_SIZE,
			)

			if not docs:
				break

			for idx, name in enumerate(docs):
				mx_stamped_xml, ack = frappe.get_value(
					doctype, name, ["mx_stamped_xml", "cancellation_acknowledgement"]
				)
				cfdi: CFDI = CFDI.from_string(mx_stamped_xml.encode("utf-8"))  # type: ignore

				if test_mode:
					status = models.CfdiStatus.DocumentStatus.ACTIVE
				else:
					try:
						status = api.get_status(
							uuid=cfdi["Complemento"]["TimbreFiscalDigital"]["UUID"],
							issuer_rfc=cfdi["Emisor"]["Rfc"],
							receiver_rfc=cfdi["Receptor"]["Rfc"],
							total=cfdi["Total"],
						).status
					except Exception:
						status = models.CfdiStatus.DocumentStatus.ACTIVE

				if status == models.CfdiStatus.DocumentStatus.CANCELLED:
					value = CFDIStatus.CANCELLED.value

				elif status == models.CfdiStatus.DocumentStatus.ACTIVE and ack:
					value = CFDIStatus.PENDING_CANCELLATION.value

				elif status == models.CfdiStatus.DocumentStatus.ACTIVE and not ack:
					value = CFDIStatus.VALID.value

				else:
					frappe.log_error(f"Failed to set CFDI status for {doctype} {name}")
					continue

				frappe.db.set_value(doctype, name, "mx_cfdi_status", value)

				update_progress_bar(f"Setting {doctype} missing CFDI Status", idx, len(docs))
				del cfdi

			frappe.db.commit()
			gc.collect()

	except JobTimeoutException as e:
		frappe.log_error(
			title=f"JobTimeoutException in _set_missing_cfdi_status for {doctype}",
			message=str(e),
		)
		frappe.enqueue(
			"erpnext_mexico_compliance.migrate.after_migrate._set_missing_cfdi_status",
			queue="long",
			doctype=doctype,
		)


def set_missing_cfdi_status(doctype: t.Literal["Sales Invoice", "Payment Entry"]):
	"""Sets the CFDI status of sales invoices and payment entries.

	Args:
		doctype (t.Literal["Sales Invoice", "Payment Entry"]): The doctype of the documents.
	"""
	doc_qty = frappe.db.count(
		doctype, filters={"mx_cfdi_status": ["is", "not set"], "mx_stamped_xml": ["is", "set"]}
	)
	if doc_qty > CHUNK_SIZE:
		q = frappe.enqueue(
			"erpnext_mexico_compliance.migrate.after_migrate._set_missing_cfdi_status",
			queue="long",
			doctype=doctype,
		)
		click.echo(
			f"{doc_qty} {doctype} documents with missing CFDI status have been found, queue {q.func_name} has been created."
		)

	elif doc_qty > 0:
		_set_missing_cfdi_status(doctype)
	else:
		return
