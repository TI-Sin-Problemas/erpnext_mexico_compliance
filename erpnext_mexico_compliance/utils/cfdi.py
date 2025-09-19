from satcfdi.cfdi import CFDI


def get_uuid_from_xml(xml: str | bytes) -> str | None:
    """
    Returns the UUID from a CFDI XML string or bytes.

    Args:
        xml (str | bytes): The CFDI XML string or bytes.

    Returns:
        str | None: The UUID if the XML is valid, otherwise None.
    """
    if isinstance(xml, str):
        xml = xml.encode("utf-8")
    cfdi = CFDI.from_string(xml)
    return cfdi.get("Complemento", {}).get("TimbreFiscalDigital", {}).get("UUID")
