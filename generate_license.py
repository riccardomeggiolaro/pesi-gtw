#!/usr/bin/env python3
"""
Uso: python3 generate_license.py <MAC_ADDRESS> [output_path]

Esempio:
    python3 generate_license.py AA:BB:CC:DD:EE:FF
    python3 generate_license.py AA:BB:CC:DD:EE:FF /percorso/license.lic

Per ottenere il MAC della macchina di destinazione:
    Linux:  ip link show   oppure   cat /sys/class/net/eth0/address
    Mac:    ifconfig
    Win:    ipconfig /all
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "program/src/lib"))
import lb_license

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mac = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) >= 3 else "program/db/license.lic"

    if lb_license.generate(mac, out):
        print(f"Licenza generata: {out}")
        print(f"MAC: {mac.upper()}")
    else:
        print("Errore nella generazione della licenza")
        sys.exit(1)

if __name__ == "__main__":
    main()
