class WSClientException(Exception):

    def __init__(self, message: str, code: str):
        super().__init__(f"{code}: {message}")
        self.message = message
        self.code = code
