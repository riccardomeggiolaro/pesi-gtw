#!/bin/bash

# Ottieni la directory dove si trova il file start.sh
SCRIPT_DIR=$(dirname "$0")

echo "Directory dello script: $SCRIPT_DIR"

# Percorso dell'ambiente virtuale relativo alla stessa directory di start.sh
VENV_DIR="$SCRIPT_DIR/.env"

echo "Percorso dell'ambiente virtuale: $VENV_DIR"

SERVICE_FILE="/etc/systemd/system/pesi-gtw.service"

# Verifica se Python 3 è installato
if ! command -v python3 &> /dev/null; then
    echo "Python 3 non è installato. Installando..."
    sudo apt update
    sudo apt install python3 -y
fi

# Verifica se pip per Python 3 è installato
if ! command -v pip3 &> /dev/null; then
    echo "pip per Python 3 non è installato. Installando..."
    sudo apt install python3-pip -y
fi

if ! dpkg -l | grep -q "ufw"; then
    echo "UFW non è installato. Installazione in corso..."
    sudo apt-get update
    sudo apt-get install ufw
    echo "UFW è stato installato."
fi

# Configura le regole del firewall solo se UFW è installato
if command -v ufw &> /dev/null; then
    sudo ufw allow 80
    sudo ufw allow 8000
fi

# Crea un ambiente virtuale se non esiste
if [ ! -d "$VENV_DIR" ]; then
    echo "Creando un ambiente virtuale..."
    python3 -m venv "$VENV_DIR"
    echo "Ambiente virtuale creato in $VENV_DIR"
fi

# Attiva l'ambiente virtuale
source "$VENV_DIR/bin/activate"

# Installa i pacchetti da requirements.txt
pip install -r requirements.txt

# Disattiva l'ambiente virtuale
deactivate

# Verifica se il file di servizio esiste già
if [ -e "$SERVICE_FILE" ]; then
    echo "Il file $SERVICE_FILE esiste già. Non è stato creato nulla."
    exit 1
fi

# Contenuto del file di servizio
SERVICE_CONTENT="[Unit]
Description=PesiGTW application start
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=$SCRIPT_DIR/start.sh

[Install]
WantedBy=multi-user.target"

# Crea il file di servizio
echo "$SERVICE_CONTENT" | sudo tee "$SERVICE_FILE" > /dev/null

if [ $? -eq 0 ]; then
    echo "Il file di servizio $SERVICE_FILE è stato creato con successo."
    sudo systemctl daemon-reload
    sudo systemctl enable pesi-gtw.service
    sudo systemctl start pesi-gtw.service
else
    echo "Si è verificato un errore durante la creazione del file di servizio."
fi