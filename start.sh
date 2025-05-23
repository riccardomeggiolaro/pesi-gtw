#!/bin/bash

# Ottieni la directory dove si trova il file start.sh
SCRIPT_DIR=$(dirname "$0")

echo "Directory dello script: $SCRIPT_DIR"

# Percorso dell'ambiente virtuale relativo alla stessa directory di start.sh
VENV_DIR="$SCRIPT_DIR/.env"

echo "Percorso dell'ambiente virtuale: $VENV_DIR"

# Verifica se l'ambiente virtuale esiste
if [ ! -d "$VENV_DIR" ]; then
    echo "Ambiente virtuale non trovato. Creazione in corso in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    echo "Ambiente virtuale creato in $VENV_DIR"
fi

# Attiva l'ambiente virtuale
source "$VENV_DIR/bin/activate"

# Esegui il programma Python
python3 "$SCRIPT_DIR/program/src/main.py"

# Disattiva l'ambiente virtuale dopo l'esecuzione
deactivate