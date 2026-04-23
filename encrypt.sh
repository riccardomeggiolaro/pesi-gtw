#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/program/src"
OUTPUT_DIR="$SCRIPT_DIR/dist"
echo "=== PyArmor Encryption Script ==="
echo "Source:  $SRC_DIR"
echo "Output:  $OUTPUT_DIR"

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

# Pulisce output precedente
if [ -d "$OUTPUT_DIR" ]; then
    echo "Rimozione output precedente..."
    rm -rf "$OUTPUT_DIR"
fi
mkdir -p "$OUTPUT_DIR"

echo ""
echo ">>> Cifratura sorgenti Python..."

# Cifra tutto src/ ricorsivamente mantenendo la struttura
$PYARMOR_CMD gen \
    --recursive \
    --output "$OUTPUT_DIR/program/src" \
    "$SRC_DIR"

echo ""
echo ">>> Copia file non-Python (HTML, JSON, config, log)..."

# Copia tutti i file non-Python preservando la struttura
find "$SRC_DIR" -type f ! -name "*.py" | while read -r file; do
    rel="${file#$SRC_DIR/}"
    dest_dir="$OUTPUT_DIR/program/src/$(dirname "$rel")"
    mkdir -p "$dest_dir"
    cp "$file" "$dest_dir/"
done

# Copia la cartella db (dati runtime, non cifrata)
if [ -d "$SCRIPT_DIR/program/db" ]; then
    echo ">>> Copia cartella db..."
    cp -r "$SCRIPT_DIR/program/db" "$OUTPUT_DIR/program/db"
fi

# Copia requirements.txt e script di avvio
echo ">>> Copia file di supporto..."
cp "$SCRIPT_DIR/requirements.txt" "$OUTPUT_DIR/requirements.txt"

# Genera start.sh puntando alla cartella dist
cat > "$OUTPUT_DIR/start.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.env"

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
fi

python3 "$SCRIPT_DIR/program/src/main.py"

[ -f "$VENV_DIR/bin/activate" ] && deactivate
EOF
chmod +x "$OUTPUT_DIR/start.sh"

# Genera setup.sh per il deploy del pacchetto cifrato
cat > "$OUTPUT_DIR/setup.sh" << 'SETUPEOF'
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="/etc/pesi-gtw/.env"
SERVICE_FILE="/etc/systemd/system/pesi-gtw.service"

command -v python3 &>/dev/null || { apt update && apt install -y python3; }
command -v pip3    &>/dev/null || apt install -y python3-pip
command -v virtualenv &>/dev/null || apt install -y virtualenv

sudo ufw allow 80
sudo ufw allow 8000

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    virtualenv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install -r "$SCRIPT_DIR/requirements.txt"
deactivate

if [ -e "$SERVICE_FILE" ]; then
    echo "Servizio già presente. Aggiornamento..."
    systemctl stop pesi-gtw.service || true
fi

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=PesiGTW application start
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pesi-gtw.service
systemctl start pesi-gtw.service
echo "Servizio avviato."
SETUPEOF
chmod +x "$OUTPUT_DIR/setup.sh"

echo ""
echo "=== Completato ==="
echo "Pacchetto cifrato in: $OUTPUT_DIR"
echo ""
echo "Struttura generata:"
find "$OUTPUT_DIR" -not -path '*/.git/*' | sort | sed "s|$OUTPUT_DIR||" | head -40
