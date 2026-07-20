"""Copyright (c) 2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

import requests


class BaseSector:
	base_url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

	def __init__(self, token: str):
		self.token = token
		self.session = requests.Session()
		self.session.headers.update({"Bmx-Token": token, "Accept": "application/json"})

	def get(self, url: str) -> dict:
		self.response = self.session.get(url)
		self.response.raise_for_status()
		return self.response.json()
