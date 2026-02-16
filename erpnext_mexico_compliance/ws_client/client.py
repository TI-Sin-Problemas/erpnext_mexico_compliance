"""Copyright (c) 2022-2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

import json

import frappe
from frappe import _
from frappe.frappeclient import FrappeClient
from satcfdi.cfdi import CFDI

from . import models


class APIClient(FrappeClient):
	def post_process(self, response):
		try:
			return super().post_process(response)
		except Exception:
			ret = None

		rjson = response.json()
		if rjson and rjson.get("exc_type"):
			msgs = json.loads(rjson.get("_server_messages", "[]"))

			if not msgs:
				msgs = [
					{
						"message": response.text,
						"raise_exception": True,
						"as_table": False,
						"indicator": "red",
					}
				]

			for m in msgs:
				if isinstance(m, dict):
					kwargs = m
				else:
					kwargs = json.loads(m)

				frappe.msgprint(
					kwargs["message"],
					_("CFDI Web Service Error"),
					kwargs["raise_exception"],
					kwargs["as_table"],
					indicator=kwargs["indicator"],
				)

		if ret is None:
			frappe.throw(response.text, title=_("CFDI Web Service Error"))
		return ret

	def post_api(self, method, data=None):  # type: ignore
		if data is None:
			data = {}
		res = self.session.post(
			f"{self.url}/api/method/{method}", data=data, verify=self.verify, headers=self.headers
		)
		return self.post_process(res)

	def stamp(self, cfdi: CFDI) -> dict:
		"""Stamps the provided CFDI.

		Args:
			cfdi (CFDI): The CFDI to be stamped.

		Returns:
			dict: The API response containing the stamped CFDI XML.
		"""
		xml_cfdi = cfdi.xml_bytes().decode("utf-8")
		return self.post_api("tisp_apps.api.v1.cfdi.stamp", data={"xml": xml_cfdi})

	def cancel_cfdi(self, signing_certificate: str, cfdi: CFDI, reason: str, substitute_uuid: str):
		"""Cancels a CFDI using the provided signing certificate, CFDI, reason, and optional
		substitute UUID.

		Args:
			signing_certificate (str): The name of the Digital Signing Certificate DocType to use
				for cancellation.
			cfdi (CFDI): The CFDI to be cancelled.
			reason (str): The reason for cancellation.
			substitute_uuid (str, optional): The substitute UUID for cancellation. Defaults to None.

		Returns:
			dict: The API response containing the cancellation acknowledgement XML.
		"""
		csd = frappe.get_doc("Digital Signing Certificate", signing_certificate)
		data = {
			"key": csd.get_key_b64(),
			"cer": csd.get_certificate_b64(),
			"password": csd.get_password(),
			"uuid": cfdi["Complemento"]["TimbreFiscalDigital"]["UUID"],
			"issuer_rfc": cfdi["Emisor"]["Rfc"],
			"receiver_rfc": cfdi["Receptor"]["Rfc"],
			"total": cfdi["Total"],
			"cancellation_reason": reason,
			"substitute_uuid": substitute_uuid,
		}
		return self.post_api("tisp_apps.api.v1.cfdi.cancel", data=data)

	def get_subscription(self):
		"""Retrieves the subscription details from the CFDI Web Service.

		Returns:
			dict: The API response containing the subscription details.
		"""
		return self.get_api("tisp_apps.api.v1.cfdi.subscription_details")

	def get_status(self, cfdi: CFDI):
		"""Retrieves the status of a CFDI from the CFDI Web Service.

		Args:
			cfdi (CFDI): The CFDI to retrieve the status of.

		Returns:
			dict: The API response containing the status of the CFDI.
		"""
		params = {
			"uuid": cfdi["Complemento"]["TimbreFiscalDigital"]["UUID"],
			"issuer_rfc": cfdi["Emisor"]["Rfc"],
			"receiver_rfc": cfdi["Receptor"]["Rfc"],
			"total": cfdi["Total"],
		}
		response = self.get_api("tisp_apps.api.v1.cfdi.status", params=params)
		return models.CfdiStatus.from_dict(response)
