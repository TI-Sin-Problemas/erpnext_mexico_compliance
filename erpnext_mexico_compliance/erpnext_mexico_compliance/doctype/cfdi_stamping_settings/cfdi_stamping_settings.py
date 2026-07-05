"""Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt"""

import typing as t
from enum import StrEnum

import frappe
from frappe import _
from frappe.email.doctype.email_template.email_template import get_email_template
from frappe.model.document import Document
from frappe.utils.caching import redis_cache

from erpnext_mexico_compliance import ws_client

if t.TYPE_CHECKING:
	from frappe.email.doctype.email_template.email_template import EmailTemplate


class EmailContactType(StrEnum):
	ALL_BILLING_CONTACTS = "All Billing Contacts"
	DOCUMENT_CONTACT = "Document Contact"


class CFDIStampingSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.cfdi_email_template.cfdi_email_template import (
			CFDIEmailTemplate,
		)
		from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.cfdi_pdf_template.cfdi_pdf_template import (
			CFDIPDFTemplate,
		)
		from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.default_csd.default_csd import (
			DefaultCSD,
		)

		api_key: DF.Data | None
		api_secret: DF.Password | None
		default_csds: DF.Table[DefaultCSD]
		email_templates: DF.Table[CFDIEmailTemplate]
		enable_low_credits_warning: DF.Check
		low_credits_threshold: DF.Int
		pdf_templates: DF.Table[CFDIPDFTemplate]
		send_email_on_stamp: DF.Check
		send_email_to: DF.Literal["", "All Billing Contacts", "Document Contact"]
		stamp_on_submit: DF.Check
		test_mode: DF.Check
	# end: auto-generated types

	def get_secret(self) -> str:
		"""Retrieves the API secret.

		Returns:
			str: The API secret.
		"""
		return self.get_password("api_secret")

	def get_token(self) -> str:
		"""Retrieves the API token.

		Returns:
			str: The API token.
		"""
		return f"{self.api_key}:{self.get_secret()}"

	@frappe.whitelist()
	def get_available_credits(self) -> int:
		"""Retrieves the available credits from the CFDI Web Service.

		Returns:
			int: The number of available credits.
		"""
		ws = ws_client.get_ws_client()
		response = ws.get_subscription()
		return response["available_credits"]

	def check_low_credits(self):
		remaining_credits = self.get_available_credits()
		if remaining_credits < self.low_credits_threshold:
			frappe.msgprint(
				msg=_("Warning: {} CFDI credits remaining.").format(remaining_credits),
				indicator="orange",
				alert=True,
			)

	def _validate_children(self):
		"""
		Validates that there are no duplicated PDF templates per company and document type.

		It checks all the PDF templates in the `pdf_templates` child table and
		throws an exception if there are any duplicates for the same company and
		document type.
		"""
		existing_templates = set()
		for template in self.pdf_templates:
			value = (template.company, template.document_type)
			if value in existing_templates:
				frappe.throw(_("Duplicated PDF template for {} and {}").format(*value))
			existing_templates.add(value)

	def validate_email_settings(self):
		if self.send_email_on_stamp:
			if not self.send_email_to:
				frappe.throw(_("Please select a type of contact to send the email to"))

	def validate(self):
		"""Validates the CFDI Stamping Settings."""
		self._validate_children()
		self.validate_email_settings()

	@property
	def is_premium(self) -> bool:
		"""Determines if the account is a premium subscriber.

		Checks if both the API key and API secret are set. If either is missing,
		the account is not considered premium. Otherwise, it verifies the premium
		status through an external check.

		Returns:
			bool: True if the account is premium, False otherwise.
		"""
		if not self.api_key or not self.api_secret:
			return False
		try:
			return get_is_premium()
		except frappe.exceptions.ValidationError:
			return False

	def set_field_from_site_config(self, field):
		"""Sets a field from the site config if it is set.

		Args:
			field (str): The name of the field to set.
		"""
		value = frappe.conf.get(f"cfdi_{field}")
		doc_field = self.meta.get_field(field)

		current_value = getattr(self, field)
		if doc_field.fieldtype == "Password" and current_value:
			current_value = self.get_password(field)

		if value is not None and current_value != value:
			msg = _(
				"The value of {0} is set from the site config and cannot be changed here. Only the site admin can change it."
			).format(_(doc_field.label))
			frappe.msgprint(msg)
			setattr(self, field, value)

	def before_validate(self):
		self.set_field_from_site_config("api_key")
		self.set_field_from_site_config("api_secret")
		self.set_field_from_site_config("test_mode")

	@property
	def api_url(self):
		"""Determines the URL of the CFDI Web Service API.

		If the account is in test mode, it returns the staging URL. Otherwise, it
		return the production URL.

		Returns:
			str: The URL of the CFDI Web Service API.
		"""
		if bool(self.test_mode):
			return "https://cfdi.tisp-staging.com"
		return "https://tisinproblemas.com"

	def can_send_emails(self, doctype: t.Literal["Payment Entry", "Sales Invoice"]) -> bool:
		"""Determines if the account can send emails for a given document type.

		Args:
			doctype (t.Literal["Payment Entry", "Sales Invoice"]): The document type to check.

		Returns:
			bool: True if the account can send emails, False otherwise.
		"""
		is_doctype_included = doctype in [t.document_type for t in self.email_templates]
		return bool(all([self.is_premium, self.send_email_on_stamp, self.send_email_to, is_doctype_included]))

	def get_email_template(
		self, doctype: t.Literal["Payment Entry", "Sales Invoice"], doc: dict
	) -> dict[str, str]:
		"""Return the processed HTML of an email template with the given doc context

		Args:
			doctype (t.Literal["Payment Entry", "Sales Invoice"]): The document type
			doc (dict): The document context as a dictionary

		Returns:
			dict: The processed HTML of the email template as a dictionary with the following keys:
				- subject: The subject of the email
				- message: The HTML content of the email
		"""
		template = next(t for t in self.email_templates if t.document_type == doctype)
		return get_email_template(template.email_template, doc)


@redis_cache(ttl=43200)  # Cache for 12 hours
def get_is_premium() -> bool:
	"""
	Checks if the current account has a valid premium subscription.

	It uses the Web Service client to retrieve the subscription details and
	checks if the subscription is valid. The result is cached for 12 hours.

	Returns:
		bool: True if the account has a valid premium subscription, False otherwise.
	"""
	ws = ws_client.get_ws_client()
	subscription = ws.get_subscription()
	return subscription["has_subscription"]
