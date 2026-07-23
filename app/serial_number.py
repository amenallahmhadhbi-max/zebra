from datetime import datetime


def generate_serial_number_sequential(pn: str, sn_start: int, index: int, separator: str = "_") -> str:
    """
    Sequential mode:
    partnumber<sep>serialnumber<sep>date<sep>1<sep>02
    """
    sn_value = sn_start + index
    sn_formatted = f"{sn_value:06d}"

    

    return separator.join([pn, sn_formatted])


def generate_serial_number_datetime(pn: str, separator: str = "_") -> str:
    """
    Date/Time mode:
    partnumber<sep>YYMMDDHHMMSS
    """
    now = datetime.now()
    formatted_date = now.strftime('%y%m%d%H%M%S')

    return separator.join([pn, formatted_date])


def generate_serial_number_custom(fields_config: list, index: int, separator: str = "_") -> str:
    """
    Custom mode:
    field1<sep>field2<sep>...

    fields_config: list of dicts, each like:
        {"value": str, "sequential": bool, "seq_type": "datetime"|"sequence", "start": int}
    index: position in the print batch (0, 1, 2, ...)
    """
    parts = []

    for field in fields_config:
        if field["sequential"]:
            if field["seq_type"] == "datetime":
                parts.append(datetime.now().strftime('%y%m%d%H%M%S'))
            else:
                value = field["start"] + index
                parts.append(f"{value:010d}")
        else:
            text = field["value"].strip()
            if text:
                parts.append(text)

    return separator.join(parts)


if __name__ == "__main__":
    test_pn = "PN12345"
    print(generate_serial_number_sequential(test_pn, sn_start=100, index=0, separator="-"))
    print(generate_serial_number_datetime(test_pn, separator="-"))

    test_fields = [
        {"value": "PN12345", "sequential": False},
        {"value": "", "sequential": True, "seq_type": "sequence", "start": 0},
        {"value": "LOT42", "sequential": False},
    ]
    print(generate_serial_number_custom(test_fields, index=0, separator="-"))
    print(generate_serial_number_custom(test_fields, index=1, separator="-"))