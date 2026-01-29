"""Copyright (c) 2024-2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe

from . import client


def get_ws_client() -> client.APIClient:
	"""Retrieves a WSClient instance based on the current CFDI Stamping Settings.

	Args:
		settings (CFDIStampingSettings, optional): The CFDI Stamping Settings document. Defaults to None.

	Returns:
		client.WSClient: A WSClient instance configured with the current API key and operation mode.
	"""
	settings = frappe.get_single("CFDI Stamping Settings")
	return client.APIClient(url=settings.api_url, api_key=settings.api_key, api_secret=settings.get_secret())


__all__ = ["get_ws_client"]
