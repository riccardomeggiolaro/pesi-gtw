#!/bin/bash

SERVICE_FILE="/etc/systemd/system/pesigtw.service"

# Chiedi all'utente di inserire l'indirizzo IP desiderato
read -p "Vuoi inserire un'indirizzo IP statico: (Y/n) " risposta

# Applica la configurazione IP statico

if [ "$risposta" = "Y" ] && [ -e "$SERVICE_FILE" ]; then
    ./stop-program.sh
    ./set-network-connection.sh
    sudo systemctl restart pesigtw.service
elif [ "$risposta" = "Y" ] &&  ! [ -e "$SERVICE_FILE" ]; then
    ./set-network-connection.sh
fi

# Verifica se Midnight Commander (mc) è installato
if ! dpkg -l | grep -q 'mc '; then
    echo "Midnight Commander (mc) non è installato. Installazione in corso..."
    sudo apt-get install mc -y
    echo "Midnight Commander (mc) è stato installato"
fi

# Verifica se sudo è installato
if ! dpkg -l | grep -q "sudo"; then
	echo "Sudo non è installato. Installazione in corso..."
	sudo apt-get update
	sudo apt-get install sudo -y
	sudo adduser baronpesi sudo
	echo "Sudo è stato installato"
fi

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

if [ ! -w /dev/ttyS0 ] || [ ! -w /dev/ttyS1 ]; then
    echo "Abilitando le porte seriali..."
    sudo chmod 777 /dev/ttyS0
    sudo chmod 777 /dev/ttyS1
fi

# Torna alla directory padre
cd ..

pip install -r requirements.txt --break-system-packages

cd ..

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
ExecStart=/etc/PesiGTW/program/start-program.sh

[Install]
WantedBy=multi-user.target"

# Crea il file di servizio
echo "$SERVICE_CONTENT" | sudo tee "$SERVICE_FILE" > /dev/null

if [ $? -eq 0 ]; then
    echo "Il file di servizio $SERVICE_FILE è stato creato con successo."
    sudo systemctl daemon-reload
    sudo systemctl enable pesigtw.service
    sudo systemctl start pesigtw.service
else
    echo "Si è verificato un errore durante la creazione del file di servizio."
fi
