"""Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt"""

# import frappe
from frappe.model.document import Document


class CancellationReason(Document):
    """Invoice Cancellation Reason"""

    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        code: DF.Data
        description: DF.Data
        requires_relationship: DF.Check
    # end: auto-generated types
