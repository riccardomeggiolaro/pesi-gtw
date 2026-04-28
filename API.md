# API Reference

Base URL: `http://<host>:8000`

---

## 1. Login — ottenere il token

```
GET /login/{username}/{password}
```

Il token è richiesto da tutte le API protette. Scade dopo **2 giorni**.

**Esempio**

```bash
curl http://localhost:8000/login/admin/mypassword
```

**Risposta**

```json
{
  "token": "abc123...xyz"
}
```

Salva il valore `token` e passalo negli endpoint successivi.

---

## 2. Lista pesate

### 2a. Lista semplice con paginazione

```
GET /lista_pesate?offset={offset}&limit={limit}&token={token}
```

| Parametro | Tipo    | Default | Descrizione                     |
|-----------|---------|---------|----------------------------------|
| `token`   | string  | —       | Token ottenuto dal login         |
| `offset`  | integer | `0`     | Indice di partenza               |
| `limit`   | integer | `3000`  | Numero massimo di record         |

**Esempio**

```bash
curl "http://localhost:8000/lista_pesate?token=abc123&offset=0&limit=50"
```

**Risposta**

```json
{
  "total_count": 1240,
  "total_net": 58320,
  "offset": 0,
  "limit": 50,
  "weighings": [
    {
      "TIPO": "PD",
      "ID": 1240,
      "BIL": "BIL01",
      "DATA1": "28/04/2026",
      "ORA1": "08:30:00",
      "DATA2": "28/04/2026",
      "ORA2": "08:32:15",
      "PROG1": 1240,
      "PROG2": 0,
      "BADGE": "",
      "TARGA": "AB123CD",
      "CLIENTE": "Rossi Srl",
      "FORNITORE": "",
      "MATERIALE": "Ghiaia",
      "NOTE1": "",
      "NOTE2": "",
      "PESO1": 32400,
      "PID1": 0,
      "PESO2": 14200,
      "PID2": 0,
      "NETTO": 18200
    }
  ]
}
```

---

### 2b. Lista con filtri

```
POST /pesate/{token}?offset={offset}&limit={limit}
```

Passa un array di filtri nel body per restringere i risultati.

**Body (JSON)**

```json
[
  {
    "campo": "MATERIALE",
    "operatore": "=",
    "valore": "Ghiaia",
    "separatore": "AND"
  },
  {
    "campo": "DATA1",
    "operatore": ">=",
    "valore": "01/04/2026",
    "separatore": ""
  }
]
```

| Chiave       | Descrizione                                     |
|--------------|-------------------------------------------------|
| `campo`      | Nome colonna (vedi campi sotto)                 |
| `operatore`  | `=`, `!=`, `>`, `<`, `>=`, `<=`, `LIKE`         |
| `valore`     | Valore di confronto                             |
| `separatore` | `AND` o `OR` (vuoto sull'ultimo filtro)         |

**Campi disponibili**

`TIPO`, `ID`, `BIL`, `DATA1`, `ORA1`, `DATA2`, `ORA2`, `PROG1`, `PROG2`,
`BADGE`, `TARGA`, `CLIENTE`, `FORNITORE`, `MATERIALE`, `NOTE1`, `NOTE2`,
`PESO1`, `PID1`, `PESO2`, `PID2`, `NETTO`

**Esempio**

```bash
curl -X POST "http://localhost:8000/pesate/abc123?offset=0&limit=100" \
  -H "Content-Type: application/json" \
  -d '[{"campo":"MATERIALE","operatore":"=","valore":"Ghiaia","separatore":""}]'
```

**Risposta** — stessa struttura del punto 2a.

---

## 3. Peso in tempo reale — WebSocket

```
WS /wspesata/{token}
```

La connessione invia un messaggio JSON ogni **200 ms** con il peso letto dalla bilancia.

**Esempio JavaScript**

```js
const token = "abc123...xyz";
const ws = new WebSocket(`ws://localhost:8000/wspesata/${token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Messaggio ricevuto**

```json
{
  "status": "Connessa",
  "type": "NT",
  "gross_weight": "32400",
  "tare": "14200",
  "net_weight": "18200",
  "unite_measure": "Kg"
}
```

| Campo           | Descrizione                                              |
|-----------------|----------------------------------------------------------|
| `status`        | `"Connessa"` / `"Pesa scollegata"`                       |
| `type`          | `"GS"` = peso lordo, `"NT"` = peso netto                |
| `gross_weight`  | Peso lordo                                               |
| `tare`          | Tara                                                     |
| `net_weight`    | Peso netto                                               |
| `unite_measure` | Unità di misura (`"Kg"`, `"g"`, …)                      |

> Se il token non è valido o è scaduto la connessione viene chiusa immediatamente.

---

## Note generali

- Tutti i pesi sono espressi nell'unità riportata in `unite_measure` (default `Kg`).
- I valori `-` indicano che la bilancia non è ancora connessa o non ha ancora fornito una lettura.
- Il token scade dopo 2 giorni: rilancia `/login` per ottenerne uno nuovo.
