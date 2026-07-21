from datetime import datetime


def generate_serial_number_sequential(pn: str, sn_start: int, index: int) -> str:
    """
    Sequential mode:
    partnumber_serialnumber_date_1_02
    """
    sn_value = sn_start + index
    sn_formatted = f"{sn_value:06d}"

    now = datetime.now()
    formatted_date = now.strftime('%y%m%d')

    LINE = "1"
    STATION = "02"

    return f"{pn}_{sn_formatted}_{formatted_date}_{LINE}_{STATION}"


def generate_serial_number_datetime(pn: str) -> str:
    """
    Date/Time mode:
    partnumber_YYMMDDHHMMSS
    """
    now = datetime.now()
    formatted_date = now.strftime('%y%m%d%H%M%S')

    return f"{pn}_{formatted_date}"


def generate_serial_number_custom(fields_config: list, index: int) -> str:
    """
    Custom mode:
    field1_field2_...

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

    return "_".join(parts)


if __name__ == "__main__":
    test_pn = "PN12345"
    print(generate_serial_number_sequential(test_pn, sn_start=100, index=0))
    print(generate_serial_number_datetime(test_pn))

    test_fields = [
        {"value": "PN12345", "sequential": False},
        {"value": "", "sequential": True, "seq_type": "sequence", "start": 0},
        {"value": "LOT42", "sequential": False},
    ]
    print(generate_serial_number_custom(test_fields, index=0))
    print(generate_serial_number_custom(test_fields, index=1))