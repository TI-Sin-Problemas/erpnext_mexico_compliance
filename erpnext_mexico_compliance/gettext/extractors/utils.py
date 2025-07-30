# Based on https://github.com/frappe/frappe/blob/develop/frappe/gettext/extractors/utils.py#L96
EXCLUDE_SELECT_OPTIONS = [
    "naming_series",
    "number_format",
    "float_precision",
    "currency_precision",
    "minimum_password_score",
    "icon",
]


def extract_messages_from_docfield(doctype: str, field: dict):
    """Extract translatable strings from docfield definition.

    `field` should have the following keys:

    - fieldtype: str
    - fieldname: str
    - label: str (optional)
    - description: str (optional)
    - options: str (optional)
    """
    fieldtype = field.get("fieldtype")
    fieldname = field.get("fieldname")
    label = field.get("label")
    # print(f"Doctype: {doctype}, Field: {fieldname}, Type: {fieldtype}, Label: {label}")
    if label:
        yield label, f"Label of the {fieldname} ({fieldtype}) field in DocType '{doctype}'"
        _label = label
    else:
        _label = fieldname

    if description := field.get("description"):
        yield description, f"Description of the '{_label}' ({fieldtype}) field in DocType '{doctype}'"

    if message := field.get("options"):
        if fieldtype == "Select" and fieldname not in EXCLUDE_SELECT_OPTIONS:
            select_options = [
                option
                for option in message.split("\n")
                if option and not option.isdigit()
            ]

            yield from (
                (
                    option,
                    f"Option for the '{_label}' ({fieldtype}) field in DocType '{doctype}'",
                )
                for option in select_options
            )
        elif fieldtype == "HTML":
            yield message, f"Content of the '{_label}' ({fieldtype}) field in DocType '{doctype}'"
