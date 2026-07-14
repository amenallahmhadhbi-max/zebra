from datetime import datetime


def generate_serial_number(pn: str) -> str:

    now = datetime.now()

    formatted_date = now.strftime('%d%m%Y%H%M%S')

    serial_number = f"{pn}_{formatted_date}"

    return serial_number


if __name__ == "__main__":
    test_pn = "PN12345"
    print(generate_serial_number(test_pn))