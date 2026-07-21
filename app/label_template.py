from paths import external_path


def build_zpl_label(pn: str, serial_number: str) -> str:

    with open(external_path("templates/label_mask.txt"), "r") as f:
        mask = f.read()

    zpl = mask.replace("{PN}", pn).replace("{SN}", serial_number)

    return zpl


if __name__ == "__main__":
    test_pn = "PN12345"
    test_sn = "PN12345_08072026153045"

    label = build_zpl_label(test_pn, test_sn)
    print(label)