import frappe
from erpnext.setup.utils import get_exchange_rate as erpnext_get_exchange_rate
from frappe.utils import getdate

from erpnext_mexico_compliance.banxico import get_sie_client


@frappe.whitelist()
def get_exchange_rate(from_currency, to_currency, transaction_date=None, args=None):
	if args == "for_selling" and from_currency == "USD" and to_currency == "MXN":
		sie = get_sie_client()
		date = getdate(transaction_date)
		data = sie.daily_exchange_rates.to_settle_liabilities_data(start_date=date, end_date=date)
		return data[0]["dato"]
	return erpnext_get_exchange_rate(from_currency, to_currency, transaction_date, args)
