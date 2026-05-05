import hashlib
import uuid
import socket

def get_machine_id():
    try:
        with open("/etc/machine-id") as f:
            return f.read().strip()
    except:
        return ""

def fingerprint():
    data = "-".join([
        get_machine_id(),
        str(uuid.getnode()),
        socket.gethostname()
    ])
    return hashlib.sha256(data.encode()).hexdigest()