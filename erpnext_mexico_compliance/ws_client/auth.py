"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt"""

from requests.auth import AuthBase


class TokenAuth(AuthBase):  # pylint: disable=too-few-public-methods
    """Class to handle token authentication."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "token " + self.token
        return r
