"""
Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt
"""

import re


def is_match(pattern: str, string: str, flags=0) -> bool:
    """Check if a string matches a regular expression pattern.

    Args:
        pattern (str): The regular expression pattern to match.
        string (str): The string to check against the pattern.
        flags (int, optional): The flags to pass to the regular expression.
            Defaults to 0.

    Returns:
        bool: True if the string matches the pattern, False otherwise.
    """
    rgx_pattern = re.compile(pattern, flags)
    return bool(re.match(rgx_pattern, string))


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
    return is_match(
        r"^([A-ZÑ]|\&){3,4}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$",
        rfc,
    )


def is_valid_curp(curp: str) -> bool:
    """
    Validate a CURP (Clave nica de Registro de Poblacin) from Mexico.

    A CURP is a 18 character string that consists of a combination of letters and numbers.
    It is composed of a combination of the following elements in the following order:
    - 4 letters:
        - first letter of first last name
        - first internal vowel of first last name
        - first letter of second last name
        - first letter of name
    - 6 digits
        - year of birth
        - month of birth
        - day of birth
    - 1 letter (H or M for gender)
    - 2 letters (entity of birth)
    - 3 letters (first internal consonants of last name and name)
    - 2 digits
        - homonymy differentiator and century
        - verification digit

    Args:
        curp (str): The CURP to validate

    Returns:
        bool: True if the CURP is valid, False otherwise
    """
    return is_match(
        r"""^([A-Z][AEIOUX][A-Z]{2}
        \d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])
        [HM]
        (?:AS|B[CS]|C[CLMSH]|D[FG]|G[TR]|HG|JC|M[CNS]|N[ETL]|OC|PL|Q[TR]|S[PLR]|T[CSL]|VZ|YN|ZS)
        [B-DF-HJ-NP-TV-Z]{3}
        [A-Z\d])(\d)$""",
        curp,
        re.VERBOSE,
    )
