# Based on https://github.com/frappe/frappe/blob/develop/frappe/gettext/extractors/custom_field.py"""
import json

import _io

from .utils import extract_messages_from_docfield


def extract(fileobj: _io.BufferedReader, *args, **kwargs):
    """
    Extract messages from Custom Field fixtures. To be used by babel extractor.

    :param fileobj: the file-like object the messages should be extracted from
    :rtype: `iterator`
    """
    data = json.load(fileobj)

    if not isinstance(data, list):
        return

    messages = []

    for custom_field in data:
        doctype = custom_field.get("dt")
        messages.extend(extract_messages_from_docfield(doctype, custom_field))

    yield from ((None, "_", message, [comment]) for message, comment in messages)
