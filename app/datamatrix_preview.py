from pystrich.datamatrix import DataMatrixEncoder


def generate_datamatrix_image(data: str):
    encoder = DataMatrixEncoder(data)
    image = encoder.get_pilimage(cellsize=8)
    return image.convert("RGB")


if __name__ == "__main__":
    test_sn = "08_07_2026_15_30_45"
    img = generate_datamatrix_image(test_sn)
    img.save("test_datamatrix.png")
    print("Image sauvegardée : test_datamatrix.png")