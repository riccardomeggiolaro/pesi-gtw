#!/bin/bash

set -e  # Termina lo script in caso di errore

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/var/pesi-gtw"
VENV_DIR="$INSTALL_DIR/.env"
SERVICE_FILE="/etc/systemd/system/pesi-gtw.service"

echo "Directory dello script: $SCRIPT_DIR"
echo "Directory di installazione: $INSTALL_DIR"

# Assicura che l'ambiente abbia gli strumenti necessari
if ! command -v python3 &> /dev/null; then
    echo "Python 3 non è installato. Installazione..."
    apt update
    apt install -y python3
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip per Python 3 non è installato. Installazione..."
    apt install -y python3-pip
fi

if ! command -v virtualenv &> /dev/null; then
    echo "virtualenv non è installato. Installazione..."
    apt install -y virtualenv
fi

if ! dpkg -l | grep -q "ufw"; then
    echo "UFW non è installato. Installazione..."
    apt install -y ufw
fi

# Configura UFW
ufw allow 80
ufw allow 8000

# Copia il pacchetto in /var/pesi-gtw
echo "Copia file in $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/." "$INSTALL_DIR/"

# Crea l'ambiente virtuale (solo se non esiste)
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Creazione dell'ambiente virtuale..."
    virtualenv "$VENV_DIR"
fi

# Installa i pacchetti
source "$VENV_DIR/bin/activate"
pip install -r "$INSTALL_DIR/requirements.txt"
deactivate

# Crea il servizio solo se non esiste
if [ -e "$SERVICE_FILE" ]; then
    echo "Il file $SERVICE_FILE esiste già. Non è stato creato nulla."
    exit 1
fi

# Crea il file systemd
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=PesiGTW application start
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Attiva il servizio
systemctl daemon-reload
systemctl enable pesi-gtw.service
systemctl start pesi-gtw.service
echo "Servizio systemd creato e avviato da $INSTALL_DIR."
