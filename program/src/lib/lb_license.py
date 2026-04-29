import hmac
import hashlib
import uuid
import os

_SECRET = b"pesi-gtw-baron-2024"

def _get_mac() -> str:
    mac = uuid.getnode()
    return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))

def _sign(mac: str) -> str:
    return hmac.new(_SECRET, mac.encode(), hashlib.sha256).hexdigest()

def generate(mac: str, license_path: str) -> bool:
    try:
        signature = _sign(mac.upper())
        with open(license_path, "w") as f:
            f.write(mac.upper() + "\n" + signature + "\n")
        return True
    except Exception as e:
        print("Errore generazione licenza:", e)
        return False

def verify(license_path: str) -> bool:
    try:
        if not os.path.exists(license_path):
            return False
        with open(license_path, "r") as f:
            lines = f.read().splitlines()
        if len(lines) < 2:
            return False
        licensed_mac = lines[0].upper()
        signature = lines[1]
        current_mac = _get_mac().upper()
        expected = _sign(licensed_mac)
        if not hmac.compare_digest(signature, expected):
            return False
        return licensed_mac == current_mac
    except Exception as e:
        print("Errore verifica licenza:", e)
        return False
