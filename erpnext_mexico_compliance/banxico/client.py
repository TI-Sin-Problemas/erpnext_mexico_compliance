"""Copyright (c) 2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

from .sectors.exchange_rates import DailyExchangeRates


class SIEClient:
	def __init__(self, token: str):
		self.daily_exchange_rates = DailyExchangeRates(token)
