#!/bin/bash

# Ottieni la directory dove si trova il file start.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Directory dello script: $SCRIPT_DIR"

# Percorso dell'ambiente virtuale relativo alla stessa directory di start.sh
VENV_DIR="$SCRIPT_DIR/.env"

# Attiva l'ambiente virtuale
source "$VENV_DIR/bin/activate"

# Esegui il programma Python
python3 "$SCRIPT_DIR/program/src/main.py"

# Disattiva l'ambiente virtuale dopo l'esecuzione
deactivate