# Dimensions de l'étiquette (1 cm large x 1.5 cm haut, à 203 dpi)
DPI = 203
LABEL_WIDTH_CM = 1
LABEL_HEIGHT_CM = 1.5

LABEL_WIDTH_DOTS = int((LABEL_WIDTH_CM / 2.54) * DPI)   
LABEL_HEIGHT_DOTS = int((LABEL_HEIGHT_CM / 2.54) * DPI) 


def build_zpl_label(pn: str, serial_number: str) -> str:
    

    zpl = f"""^XA
^PW{LABEL_WIDTH_DOTS}
^LL{LABEL_HEIGHT_DOTS}

^FO5,5 ^A0N,18,18 ^FD{pn}^FS

^FO10,30 ^BXN,2,200 ^FD{serial_number}^FS

^XZ"""

    return zpl


if __name__ == "__main__":
    test_pn = "PN12345"
    test_sn = "08_07_2026_15_30_45"

    label = build_zpl_label(test_pn, test_sn)
    print(label)