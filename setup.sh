#!/bin/bash

set -e  # Termina lo script in caso di errore

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Directory dello script: $SCRIPT_DIR"

VENV_DIR="/etc/pesi-gtw/.env"
echo "Percorso dell'ambiente virtuale: $VENV_DIR"

SERVICE_FILE="/etc/systemd/system/pesi-gtw.service"

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
sudo ufw allow 80
sudo ufw allow 8000

# Crea l'ambiente virtuale (solo se non esiste)
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Creazione dell'ambiente virtuale..."
    virtualenv "$VENV_DIR"
    echo "Ambiente virtuale creato in $VENV_DIR"
fi

# Attiva l'ambiente virtuale
source "$VENV_DIR/bin/activate"

# Installa i pacchetti da requirements.txt
pip install -r "$SCRIPT_DIR/requirements.txt"

# Disattiva l'ambiente virtuale
deactivate

# Crea il servizio solo se non esiste
if [ -e "$SERVICE_FILE" ]; then
    echo "Il file $SERVICE_FILE esiste già. Non è stato creato nulla."
    exit 1
fi

# Crea il file systemd
SERVICE_CONTENT="[Unit]
Description=PesiGTW application start
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/start.sh
Restart=always

[Install]
WantedBy=multi-user.target"

echo "$SERVICE_CONTENT" | tee "$SERVICE_FILE" > /dev/null

# Attiva il servizio
systemctl daemon-reload
systemctl enable pesi-gtw.service
systemctl start pesi-gtw.service
echo "Servizio systemd creato e avviato."