# Cifratura del progetto con PyArmor

Lo script `encrypt.sh` offusca tutti i sorgenti Python del progetto usando [PyArmor 9](https://pyarmor.readthedocs.io/) e produce nella cartella `dist/` il codice cifrato con i file non-Python copiati intatti.

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
└── pesi-gtw/                        ← cartella pronta al deploy
    ├── requirements.txt
    ├── setup.sh
    ├── start.sh
    ├── license.key                  ← chiave licenza del cliente
    └── program/
        ├── db/                      ← dati runtime copiati intatti
        └── src/
            ├── main.py              ← cifrato
            ├── pyarmor_runtime_xxxxxx/  ← runtime PyArmor
            │   ├── __init__.py
            │   └── pyarmor_runtime.so
            ├── config.json
            ├── gateway.log
            ├── lib/                 ← cifrato (include lb_license.py)
            ├── modules/             ← cifrato
            ├── app/                 ← cifrato
            └── static/              ← HTML copiati intatti
```

> I file `.py` originali non vengono modificati. La cartella `dist/` è rigenerata ad ogni esecuzione. Il deploy sul server è gestito da `setup.sh`.

---

## Gestione licenze cliente

### Generare una chiave per un cliente

```bash
# Ottieni il MAC della macchina del cliente
ip link show | grep "link/ether"

# Genera la chiave e salvala su file
python gen_license.py aa:bb:cc:dd:ee:ff --out license.key
```

Metti `license.key` nella root del progetto prima di eseguire `./encrypt.sh`: verrà copiato automaticamente in `dist/pesi-gtw/`.

### Revocare una licenza

Non distribuire un nuovo pacchetto con la chiave di quel cliente. La chiave è valida solo sul MAC originale.

---

## Note

| Situazione | Comportamento |
|---|---|
| Nessun `--mac` | Il pacchetto gira su qualsiasi macchina |
| `--mac` specificato | Errore a runtime su macchine con MAC diverso |
| Licenza già registrata | `--license` può essere omesso |
| `dist/` già presente | Viene rimossa e ricreata automaticamente |
| `__pycache__` | Escluse dal pacchetto finale |
