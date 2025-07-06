"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt"""

from frappe.types.frappedict import _dict

from .hooks import app_name
from .ws_client import get_ws_client


def boot_session(bootinfo: _dict):
    """
    Extends the boot info dictionary with the "has_subscription" key.

    The value of "has_subscription" is a boolean indicating whether the current user
    has a subscription for the CFDI Web Service.

    Args:
        bootinfo (_dict): The boot info dictionary to be extended.

    Returns:
        None
    """
    ws = get_ws_client()
    subscription = ws.get_subscription_details()
    bootinfo[app_name] = {"has_subscription": subscription.has_subscription}
