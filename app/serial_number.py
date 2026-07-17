from datetime import datetime


def generate_serial_number(pn: str, sn_start: int, index: int) -> str:
    """
    Construit le contenu complet du Data Matrix :
    partnumber_serialnumber_date_1_02

    - sn_start : numéro de série de départ saisi par l'utilisateur
    - index    : position dans le lot d'impression (0, 1, 2, ...)
    """
    sn_value = sn_start + index
    sn_formatted = f"{sn_value:06d}"  # zero-padding sur 6 chiffres, ajuste selon besoin

    now = datetime.now()
    formatted_date = now.strftime('%y%m%d')  # ajuste le format selon ce qu'attend ton encadreur

    LIGNE = "1"
    STATION = "02"

    full_code = f"{pn}_{sn_formatted}_{formatted_date}_{LIGNE}_{STATION}"

    return full_code


if __name__ == "__main__":
    test_pn = "PN12345"
    print(generate_serial_number(test_pn, sn_start=100, index=0))
    print(generate_serial_number(test_pn, sn_start=100, index=1))