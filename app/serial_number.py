from datetime import datetime


def generate_serial_number_sequential(pn: str, sn_start: int, index: int) -> str:
    """
    Mode séquentiel :
    partnumber_serialnumber_date_1_02
    """
    sn_value = sn_start + index
    sn_formatted = f"{sn_value:06d}"

    now = datetime.now()
    formatted_date = now.strftime('%y%m%d')

    LIGNE = "1"
    STATION = "02"

    return f"{pn}_{sn_formatted}_{formatted_date}_{LIGNE}_{STATION}"


def generate_serial_number_datetime(pn: str) -> str:
    """
    Mode Date/Heure :
    partnumber_AAMMJJHHMMSS
    """
    now = datetime.now()
    formatted_date = now.strftime('%y%m%d%H%M%S')

    return f"{pn}_{formatted_date}"


def generate_serial_number_custom(pn: str, extra_fields: list) -> str:
    """
    Mode Custom :
    partnumber_champ1_champ2_...
    - extra_fields : liste de textes libres saisis par l'utilisateur (0 à 5 éléments)
    """
    parts = [pn] + [f for f in extra_fields if f.strip()]
    return "_".join(parts)


if __name__ == "__main__":
    test_pn = "PN12345"
    print(generate_serial_number_sequential(test_pn, sn_start=100, index=0))
    print(generate_serial_number_datetime(test_pn))
    print(generate_serial_number_custom(test_pn, ["LOT42", "ligneA"]))