# Copyright (c) 2025, TI Sin Problemas and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DefaultCSD(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Link
		csd: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
