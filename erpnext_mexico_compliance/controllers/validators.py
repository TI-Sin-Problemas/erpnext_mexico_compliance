"""
Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import re


def is_valid_rfc(rfc: str) -> bool:
    """Validate a RFC (Registro Federal de Contribuyentes) from Mexico.

    A RFC is a 13 character string that consists of a combination of letters and numbers.
    It is composed of a combination of the following elements in the following order:
    - 3 or 4 letters
    - 2 numbers (year of birth)
    - 2 numbers (month of birth)
    - 2 numbers (day of birth)
    - 3 letters (homologation key)

    Args:
        rfc (str): The RFC to validate

    Returns:
        bool: True if the RFC is valid, False otherwise
    """
    pattern = re.compile(
        r"^([A-ZÑ]|\&){3,4}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$"
    )
    return bool(re.match(pattern, rfc))
