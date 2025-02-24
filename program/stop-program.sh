#!/bin/bash

# Cerca i processi in ascolto sulla porta 8000
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