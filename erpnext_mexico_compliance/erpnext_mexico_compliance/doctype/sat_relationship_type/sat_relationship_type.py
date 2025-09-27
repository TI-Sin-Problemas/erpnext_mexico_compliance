# Copyright (c) 2025, TI Sin Problemas and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SATRelationshipType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		code: DF.Data
		description: DF.Data
		enabled: DF.Check
		valid_from: DF.Date | None
	# end: auto-generated types
	pass
