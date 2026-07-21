import serial
import time
import configparser
from paths import external_path

config = configparser.ConfigParser()
config.read(external_path("config/printer_config.ini"))

SERIAL_PORT = config["PrinterSettings"]["port"]
BAUD_RATE = int(config["PrinterSettings"]["baud_rate"])
DATA_BITS = int(config["PrinterSettings"]["data_bits"])
PARITY = config["PrinterSettings"]["parity"]
STOP_BITS = float(config["PrinterSettings"]["stop_bits"])
FLOW_CONTROL = config["PrinterSettings"]["flow_control"]

SIMULATION_MODE = False


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


def get_printer_status(timeout=2):
    if SIMULATION_MODE:
        return {"paper_out": False, "ribbon_out": False, "head_open": False}
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            bytesize=DATA_BITS,
            parity=PARITY,
            stopbits=STOP_BITS,
            xonxoff=True,
            timeout=timeout
        )
        ser.write(b"~HS")
        ser.flush()
        time.sleep(0.3)
        raw = ser.read(300)
        ser.close()
        if not raw:
            print("Aucune réponse de l'imprimante (timeout ~HS).")
            return None
        return _parse_hs_response(raw)
    except Exception as e:
        print(f"Erreur lors de la requête de statut : {e}")
        return None


def _parse_hs_response(raw: bytes):
    text = raw.decode(errors="ignore")
    lines = [l for l in text.replace("\x02", "").split("\x03") if l.strip()]
    status = {"paper_out": False, "ribbon_out": False, "head_open": False, "paused": False}
    if len(lines) >= 1:
        f1 = lines[0].strip(",\r\n").split(",")
        if len(f1) > 2:
            status["paper_out"] = f1[1] == "1"
            status["paused"] = f1[2] == "1"
    if len(lines) >= 2:
        f2 = lines[1].strip(",\r\n").split(",")
        if len(f2) > 3:
            status["head_open"] = f2[2] == "1"
            status["ribbon_out"] = f2[3] == "1"
    return status


if __name__ == "__main__":
    test_zpl = """^XA
^FO50,50
^A0N,30,30
^FDTest impression^FS
^XZ"""

    success = send_to_printer(test_zpl)
    print(f"\nRésultat de l'envoi : {success}")

    status = get_printer_status()
    print(f"\nStatut brut reçu : {status}")