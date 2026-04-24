import hmac
import hashlib
import uuid
import sys
from pathlib import Path

_SECRET = b"e3f1a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0"

def _mac() -> str:
    mac_int = uuid.getnode()
    return "".join(f"{(mac_int >> (8 * i)) & 0xff:02x}" for i in range(5, -1, -1))

def check(license_path: str):
    try:
        key = Path(license_path).read_text().strip()
        expected = hmac.new(_SECRET, _mac().encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(key, expected):
            raise ValueError
    except Exception:
        print("Licenza non valida o assente.")
        sys.exit(1)
