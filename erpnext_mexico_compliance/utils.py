"""
Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt

Utility functions
"""

import pyqrcode


def qr_as_base64(content: str, scale: int = 2, quiet_zone: int = 1) -> str:
    """Generates a QR code from the provided content and returns it in base64-encoded PNG format.

    Args:
        content (str): The content to encode in the QR code.
        scale (int, optional): The scale factor for the QR code image. Defaults to 2.
        quiet_zone (int, optional): The width of the quiet zone around the QR code. Defaults to 1.

    Returns:
        str: The base64-encoded PNG representation of the QR code.
    """
    qr = pyqrcode.create(content)
    return qr.png_as_base64_str(scale=scale, quiet_zone=quiet_zone)
