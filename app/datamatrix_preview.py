from pylibdmtx.pylibdmtx import encode
from PIL import Image


def generate_datamatrix_image(data: str):
    

    encoded = encode(data.encode("utf-8"))

    image = Image.frombytes(
        "RGB",
        (encoded.width, encoded.height),
        encoded.pixels
    )

    return image


if __name__ == "__main__":
    test_sn = "08_07_2026_15_30_45"
    img = generate_datamatrix_image(test_sn)
    img.save("test_datamatrix.png")
    print("Image sauvegardée : test_datamatrix.png")