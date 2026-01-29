"""
Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt

Utility functions
"""

import math

import frappe
import pyqrcode
from frappe import _
from frappe.locale import get_number_format
from frappe.utils import flt, get_defaults, in_words


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


def money_in_words(
	number: str | float | int,
	main_currency: str | None = None,
	fraction_currency: str | None = None,
):
	"""Converts a number to a string with currency and fraction currency.

	Based on `frappe.utils.money_in_words`, but addapted for Mexican format

	Args:
		number (str | float | int): The number to convert.
		main_currency (str, optional): The main currency. Defaults to None.

	Returns:
		str: The string representation of the number with currency and fraction currency.
	"""
	try:
		# note: `flt` returns 0 for invalid input and we don't want that
		number = float(number)
	except ValueError:
		return ""

	number = flt(number)
	if number < 0:
		return ""

	d = get_defaults()
	if not main_currency:
		main_currency = d.get("currency", "MXN")

	if not fraction_currency:
		fraction_currency = frappe.db.get_value("Currency", main_currency, "fraction", cache=True)

	number_format = get_number_format()

	fraction_units = frappe.db.get_value("Currency", main_currency, "fraction_units", cache=True)
	if fraction_units:
		fraction_length = math.ceil(math.log10(fraction_units))
	elif not fraction_units or not fraction_currency:
		fraction_units = fraction_length = 0

	n = f"%.{fraction_length}f" % number

	numbers = n.split(".")
	main, fraction = numbers if len(numbers) > 1 else [n, "00"]

	if len(fraction) < fraction_length:
		zeros = "0" * (fraction_length - len(fraction))
		fraction += zeros

	in_million = True
	if number_format.string == "#,##,###.##":
		in_million = False

	fraction = f"{fraction}/100"

	main = in_words(main, in_million).title()
	if main_currency == "MXN":
		main = f"{main} pesos"

	return f"{main} {fraction} {_(main_currency, context='Currency')}"
