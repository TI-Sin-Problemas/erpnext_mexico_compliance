import frappe

from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.cfdi_stamping_settings.cfdi_stamping_settings import (
	CFDIStampingSettings,
)

from .client import SIEClient


def get_sie_client() -> SIEClient:
	settings: CFDIStampingSettings = frappe.get_single("CFDI Stamping Settings")  # type: ignore
	token = settings.get_sie_api_token()
	return SIEClient(token)  # type: ignore
