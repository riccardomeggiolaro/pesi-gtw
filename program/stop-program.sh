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

# Cerca i processi in ascolto sulla porta 80
port80=80
port8000=8000
processes80=$(sudo lsof -t -i :$port80)
processes8000=$(sudo lsof -t -i :$port8000)

if [ -n "$processes80" ]; then
    for pid in $processes80; do
        sudo kill -9 "$pid"
        echo "Processo con PID $pid terminato."
    done
else
    echo "Nessun processo in ascolto sulla porta $port80."
fi

if [ -n "$processes8000" ]; then
    for pid in $processes8000; do
        sudo kill -9 "$pid"
        echo "Processo con PID $pid terminato."
    done
else
    echo "Nessun processo in ascolto sulla porta $port8000."
fi

# Disattiva l'ambiente virtuale dopo l'esecuzione
deactivate
