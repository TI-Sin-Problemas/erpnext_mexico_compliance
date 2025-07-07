"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt"""

from frappe.types.frappedict import _dict
from frappe.utils.caching import redis_cache

from .hooks import app_name
from .ws_client import get_ws_client


@redis_cache(ttl=43200)  # Cache for 12 hours
def _get_subscription_details():
    """Retrieves the app subscription details for the current instance.

    The subscription details are retrieved using the CFDI Web Service.
    The response is cached for 12 hours using Redis.

    Returns:
        dict: The subscription details.
    """
    ws = get_ws_client()
    return ws.get_subscription_details()


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
    subscription = _get_subscription_details()
    bootinfo[app_name] = {"has_subscription": subscription.has_subscription}
