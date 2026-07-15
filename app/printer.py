import serial
import time

# Configuration 
SIMULATION_MODE = True   # passe à False une fois l'imprimante branchée et testée

SERIAL_PORT = "COM3"     # à ajuster une fois le vrai port connu (Gestionnaire de périphériques)
BAUD_RATE = 9600         # à ajuster selon la doc de l'imprimante


def send_to_printer(zpl_code: str) -> bool:
    """
    Envoie le code ZPL à l'imprimante.
    Si SIMULATION_MODE est True, simule l'envoi (affichage console).
    Si False, envoie réellement les données via le port série (RS-232).
    """

    if SIMULATION_MODE:
        return _send_simulated(zpl_code)
    else:
        return _send_real(zpl_code)


def _send_simulated(zpl_code: str) -> bool:
    try:
        print("=" * 40)
        print("SIMULATION - Envoi à l'imprimante :")
        print("=" * 40)
        print(zpl_code)
        time.sleep(1)
        print("=" * 40)
        print("Impression simulée avec succès.")
        return True

    except Exception as e:
        print(f"Erreur lors de l'envoi (simulé) : {e}")
        return False


def _send_real(zpl_code: str) -> bool:
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        ser.write(zpl_code.encode("utf-8"))
        ser.close()

        print("Impression envoyée avec succès (mode réel).")
        return True

    except Exception as e:
        print(f"Erreur lors de l'envoi réel à l'imprimante : {e}")
        return False


if __name__ == "__main__":
    test_zpl = """^XA
^FO50,50
^A0N,30,30
^FDTest impression^FS
^XZ"""

    success = send_to_printer(test_zpl)
    print(f"\nRésultat de l'envoi : {success}")