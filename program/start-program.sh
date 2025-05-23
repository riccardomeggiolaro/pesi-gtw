#!/bin/bash

# Percorso dell'ambiente virtuale
VENV_DIR=".env"

# Verifica se l'ambiente virtuale esiste
if [ ! -d "$VENV_DIR" ]; then
    echo "Ambiente virtuale non trovato. Creazione in corso..."
    python3 -m venv "$VENV_DIR"
    echo "Ambiente virtuale creato in $VENV_DIR"
fi

# Attiva l'ambiente virtuale
source "$VENV_DIR/bin/activate"

# Esegui il programma Python
python3 /etc/pesi-gtw/program/src/main.py

# Disattiva l'ambiente virtuale dopo l'esecuzione
deactivate
