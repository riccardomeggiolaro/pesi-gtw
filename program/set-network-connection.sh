#!/bin/bash

# Verifica se l'utente è root (amministratore)
if [ "$EUID" -ne 0 ]; then
    echo "Questo script deve essere eseguito con privilegi di amministratore (root)."
    exit 1
fi

# File di configurazione del network
NETWORK_CONFIG_FILE="/etc/network/interfaces"

# Chiedi all'utente di inserire i dati di rete
read -p "Inserisci interfaccia di rete (enp1s0, enp2s0): " NETWORK_INTERFACE
read -p "Inserisci l'indirizzo IP statico: " STATIC_IP
read -p "Inserisci l'indirizzo del gateway: " GATEWAY
read -p "Inserisci la subnet mask (es. 255.255.255.0): " NETMASK

# Modifica il file di configurazione di rete
echo "auto $NETWORK_INTERFACE" > $NETWORK_CONFIG_FILE
echo "iface $NETWORK_INTERFACE inet static" >> $NETWORK_CONFIG_FILE
echo "address $STATIC_IP" >> $NETWORK_CONFIG_FILE
echo "netmask $NETMASK" >> $NETWORK_CONFIG_FILE
echo "gateway $GATEWAY" >> $NETWORK_CONFIG_FILE

# Riavvia il servizio di rete per applicare la nuova configurazione
sudo service networking restart

# Ora l'indirizzo IP dovrebbe essere configurato staticamente

# Salva la configurazione in un file per ripristinarla in caso di riavvio
echo "NETWORK_CONFIG_FILE=$NETWORK_CONFIG_FILE" >> /etc/environment
echo "STATIC_IP=$STATIC_IP" >> /etc/environment
echo "GATEWAY=$GATEWAY" >> /etc/environment
echo "NETMASK=$NETMASK" >> /etc/environment

# Fatto
echo "Configurazione IP statico completata."
