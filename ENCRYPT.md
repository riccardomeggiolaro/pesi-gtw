# Cifratura del progetto con PyArmor

Lo script `encrypt.sh` offusca tutti i sorgenti Python del progetto usando [PyArmor 9](https://pyarmor.readthedocs.io/) e produce nella cartella `dist/` un pacchetto pronto al deploy, con i file non-Python copiati intatti.

---

## Prerequisiti

- Python 3.x
- Virtualenv (`.venv` o `.env` nella root del progetto)
- Licenza PyArmor (Group License) registrata sul dispositivo

### Registrazione licenza (prima volta)

La Group License richiede tre passi eseguiti una sola volta sulla macchina di sviluppo:

```bash
# 1. Genera l'impronta del dispositivo
pyarmor reg -g 1

# 2. Combina l'impronta con il file licenza → crea pyarmor-device-regfile-6962.1.zip
pyarmor reg -g 1 ~/.pyarmor/pyarmor-regfile-6962.zip

# 3. Registra il dispositivo
pyarmor reg pyarmor-device-regfile-6962.1.zip

# Verifica: deve mostrare l'ID licenza (non "000000")
pyarmor --version
```

---

## Utilizzo

```bash
# Cifratura base — gira su qualsiasi macchina
./encrypt.sh

# Con binding al MAC — il codice funziona SOLO sulla macchina specificata
./encrypt.sh --mac aa:bb:cc:dd:ee:ff

# Registra la licenza e cifra in un solo comando
./encrypt.sh --license ~/pyarmor-regfile-6962.zip

# Registra la licenza + binding MAC
./encrypt.sh --license ~/pyarmor-regfile-6962.zip --mac aa:bb:cc:dd:ee:ff
```

### Trovare il MAC della macchina di destinazione

```bash
ip link show | grep "link/ether"
```

---

## Struttura output

```
dist/
├── program/
│   ├── src/
│   │   ├── main.py                  ← cifrato
│   │   ├── pyarmor_runtime_xxxxxx/  ← runtime PyArmor
│   │   │   ├── __init__.py
│   │   │   └── pyarmor_runtime.so
│   │   ├── config.json
│   │   ├── gateway.log
│   │   ├── lib/                     ← cifrato
│   │   ├── modules/                 ← cifrato
│   │   ├── app/                     ← cifrato
│   │   └── static/                  ← HTML copiati intatti
│   └── db/                          ← dati runtime copiati intatti
├── requirements.txt
├── start.sh                         ← avvio applicazione
└── setup.sh                         ← installazione servizio systemd
```

> I file `.py` originali non vengono modificati. La cartella `dist/` è rigenerata ad ogni esecuzione.

---

## Deploy sulla macchina di destinazione

Copia la cartella `dist/` sul server, poi:

```bash
# Installa dipendenze e crea il servizio systemd
sudo ./setup.sh

# Oppure avvia manualmente
./start.sh
```

### Requisiti sulla macchina di destinazione

- Python 3.x della stessa versione major/minor usata in fase di cifratura
- Stessa architettura (es. `linux.x86_64`)
- Se usato `--mac`: la macchina deve avere quell'indirizzo MAC

---

## Note

| Situazione | Comportamento |
|---|---|
| Nessun `--mac` | Il pacchetto gira su qualsiasi macchina |
| `--mac` specificato | Errore a runtime su macchine con MAC diverso |
| Licenza già registrata | `--license` può essere omesso |
| `dist/` già presente | Viene rimossa e ricreata automaticamente |
| `__pycache__` | Escluse dal pacchetto finale |
