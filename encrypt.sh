#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/program/src"
OUTPUT_DIR="$SCRIPT_DIR/dist"
LICENSE_FILE=""
MAC_ADDRESS=""

# Parsing argomenti: --license <file>  --mac <xx:xx:xx:xx:xx:xx>
while [[ $# -gt 0 ]]; do
    case "$1" in
        --license) LICENSE_FILE="$2"; shift 2 ;;
        --mac)     MAC_ADDRESS="$2";  shift 2 ;;
        *) echo "Argomento sconosciuto: $1"; exit 1 ;;
    esac
done

echo "=== PyArmor Encryption Script ==="
echo "Source:  $SRC_DIR"
echo "Output:  $OUTPUT_DIR"
[ -n "$MAC_ADDRESS" ] && echo "MAC bind: $MAC_ADDRESS"

# Cerca il virtualenv (.venv ha priorità su .env)
VENV_DIR=""
for candidate in "$SCRIPT_DIR/.venv" "$SCRIPT_DIR/.env"; do
    if [ -f "$candidate/bin/activate" ]; then
        VENV_DIR="$candidate"
        break
    fi
done

if [ -n "$VENV_DIR" ]; then
    echo "Virtualenv: $VENV_DIR"
    source "$VENV_DIR/bin/activate"
    PIP="pip"
else
    echo "Nessun virtualenv trovato, uso Python di sistema."
    PIP="pip3"
fi

# Verifica che pyarmor sia installato (come comando CLI)
if ! command -v pyarmor &>/dev/null; then
    echo "PyArmor non trovato. Installazione..."
    $PIP install pyarmor
fi

PYARMOR_CMD="pyarmor"
echo "PyArmor versione: $($PYARMOR_CMD --version 2>&1 | head -1)"

# Registra la licenza se passata come argomento
if [ -n "$LICENSE_FILE" ]; then
    if [ ! -f "$LICENSE_FILE" ]; then
        echo "ERRORE: file licenza non trovato: $LICENSE_FILE"
        exit 1
    fi
    echo ">>> Registrazione licenza: $LICENSE_FILE"
    $PYARMOR_CMD reg "$LICENSE_FILE"
fi

# Valida formato MAC se fornito
if [ -n "$MAC_ADDRESS" ]; then
    if ! echo "$MAC_ADDRESS" | grep -qP '^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$'; then
        echo "ERRORE: formato MAC non valido (atteso xx:xx:xx:xx:xx:xx): $MAC_ADDRESS"
        exit 1
    fi
fi

# Pulisce output precedente
if [ -d "$OUTPUT_DIR" ]; then
    echo "Rimozione output precedente..."
    rm -rf "$OUTPUT_DIR"
fi
mkdir -p "$OUTPUT_DIR"

echo ""
echo ">>> Cifratura sorgenti Python..."

# Cifra tutto src/ ricorsivamente.
# PyArmor aggiunge automaticamente basename(SRC_DIR) all'output,
# quindi --output dist/program produce dist/program/src/
BIND_OPT=""
[ -n "$MAC_ADDRESS" ] && BIND_OPT="--bind-device $MAC_ADDRESS"

$PYARMOR_CMD gen \
    --recursive \
    --output "$OUTPUT_DIR/program" \
    $BIND_OPT \
    "$SRC_DIR"

echo ""
echo ">>> Sposta runtime PyArmor dentro src/ (necessario per l'import)..."
# pyarmor gen mette il runtime in dist/program/ ma main.py lo cerca
# nella stessa cartella; lo spostiamo dentro src/
RUNTIME_DIR=$(find "$OUTPUT_DIR/program" -maxdepth 1 -type d -name "pyarmor_runtime_*" | head -1)
if [ -n "$RUNTIME_DIR" ]; then
    mv "$RUNTIME_DIR" "$OUTPUT_DIR/program/src/"
fi

echo ""
echo ">>> Copia file non-Python (HTML, JSON, config, log)..."

# Copia tutti i file non-Python (escluse __pycache__) preservando la struttura
find "$SRC_DIR" -type f ! -name "*.py" ! -path "*/__pycache__/*" | while read -r file; do
    rel="${file#$SCRIPT_DIR/program/}"
    dest_dir="$OUTPUT_DIR/program/$(dirname "$rel")"
    mkdir -p "$dest_dir"
    cp "$file" "$dest_dir/"
done

# Rimuove eventuali __pycache__ copiati da pyarmor
find "$OUTPUT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Copia la cartella db (dati runtime, non cifrata)
if [ -d "$SCRIPT_DIR/program/db" ]; then
    echo ">>> Copia cartella db..."
    cp -r "$SCRIPT_DIR/program/db" "$OUTPUT_DIR/program/db"
fi

# Copia requirements.txt
echo ">>> Copia file di supporto..."
cp "$SCRIPT_DIR/requirements.txt" "$OUTPUT_DIR/requirements.txt"

echo ""
echo "=== Completato ==="
echo "Pacchetto cifrato in: $OUTPUT_DIR"
echo ""
echo "Struttura generata:"
find "$OUTPUT_DIR" -not -path '*/.git/*' | sort | sed "s|$OUTPUT_DIR||" | head -40
