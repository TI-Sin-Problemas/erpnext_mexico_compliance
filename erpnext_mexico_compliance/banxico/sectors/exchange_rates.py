"""Copyright (c) 2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from .base import BaseSector


class DailyExchangeRates(BaseSector):
	DATE_OF_SETTLEMENT_SERIES = "SF60653"
	DATE_OF_DETERMINATION_SERIES = "SF43718"

	def to_settle_liabilities_metadata(self) -> dict:
		response = self.session.get(f"{self.base_url}/{self.DATE_OF_SETTLEMENT_SERIES}")
		data = response.json()
		bmx = data["bmx"]
		series = bmx["series"]

		return series[0]

	def to_settle_liabilities_data(
		self, start_date: date | None = None, end_date: date | None = None
	) -> list:
		if not start_date:
			start_date = datetime.now(tz=ZoneInfo("America/Mexico_City")).date()

		if not end_date:
			end_date = datetime.now(tz=ZoneInfo("America/Mexico_City")).date()

		formatted_start_date = start_date.strftime("%Y-%m-%d")
		formatted_end_date = end_date.strftime("%Y-%m-%d")

		url = f"{self.base_url}/{self.DATE_OF_SETTLEMENT_SERIES}/datos"
		url = f"{url}/{formatted_start_date}/{formatted_end_date}"

		data = self.get(url)
		bmx = data["bmx"]
		series = bmx["series"]

		return series[0]["datos"]


pass
