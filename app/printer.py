import serial
import time
import configparser

# Chargement confi fichier .ini 
config = configparser.ConfigParser()
config.read("config/printer_config.ini")

SERIAL_PORT = config["PrinterSettings"]["port"]
BAUD_RATE = int(config["PrinterSettings"]["baud_rate"])
DATA_BITS = int(config["PrinterSettings"]["data_bits"])
PARITY = config["PrinterSettings"]["parity"]
STOP_BITS = float(config["PrinterSettings"]["stop_bits"])
FLOW_CONTROL = config["PrinterSettings"]["flow_control"]

SIMULATION_MODE = False   # passe à False une fois l'imprimante branchée et testée


def send_to_printer(zpl_code: str) -> bool:
   

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
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            bytesize=DATA_BITS,
            parity=PARITY,
            stopbits=STOP_BITS,
            xonxoff=True,
            timeout=2
        )
        ser.write(zpl_code.encode("utf-8"))
        ser.flush()
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