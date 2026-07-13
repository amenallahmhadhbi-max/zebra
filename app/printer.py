def send_to_printer(zpl_code: str) -> bool:
   

    try:
        print("=" * 40)
        print("SIMULATION - Envoi à l'imprimante :")
        print("=" * 40)
        print(zpl_code)
        print("=" * 40)
        print("Impression simulée avec succès.")
        return True

    except Exception as e:
        print(f"Erreur lors de l'envoi (simulé) : {e}")
        return False


if __name__ == "__main__":
    test_zpl = """^XA
^FO50,50
^A0N,30,30
^FDTest impression^FS
^XZ"""

    success = send_to_printer(test_zpl)
    print(f"\nRésultat de l'envoi : {success}")