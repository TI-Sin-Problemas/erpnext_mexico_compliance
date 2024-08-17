class WSClientException(Exception):
    """Base class for exceptions raised by the CFDI Web Service."""

    def __init__(self, message: str, code: str):
        super().__init__(f"{code}: {message}")
        self.message = message
        self.code = code


class WSExistingCfdiException(WSClientException):
    """Raised when an existing CFDI is found in the CFDI Web Service."""

    def __init__(self, message: str, code: str, data: str):
        super().__init__(message, code)
        self.data = data
