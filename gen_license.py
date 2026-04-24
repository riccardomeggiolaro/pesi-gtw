#!/usr/bin/env python3
"""
Genera la chiave di licenza per un dispositivo dato il suo MAC address.
Usare SOLO lato sviluppatore — non distribuire questo file.

Uso:
    python gen_license.py aa:bb:cc:dd:ee:ff
    python gen_license.py aa:bb:cc:dd:ee:ff --out license.key
"""

import hmac
import hashlib
import sys
import argparse
from pathlib import Path

# Stessa chiave segreta presente in lb_license.py (protetta da PyArmor)
_SECRET = b"e3f1a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0"

def generate(mac: str) -> str:
    mac_clean = mac.replace(":", "").replace("-", "").lower()
    if len(mac_clean) != 12 or not all(c in "0123456789abcdef" for c in mac_clean):
        raise ValueError(f"MAC non valido: {mac}")
    return hmac.new(_SECRET, mac_clean.encode(), hashlib.sha256).hexdigest()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera licenza PyArmor per MAC address")
    parser.add_argument("mac", help="MAC address (es. aa:bb:cc:dd:ee:ff)")
    parser.add_argument("--out", help="Salva la chiave su file (es. license.key)")
    args = parser.parse_args()

    try:
        key = generate(args.mac)
    except ValueError as e:
        print(f"Errore: {e}")
        sys.exit(1)

    print(f"MAC:     {args.mac}")
    print(f"Chiave:  {key}")

    if args.out:
        Path(args.out).write_text(key + "\n")
        print(f"Salvata: {args.out}")
