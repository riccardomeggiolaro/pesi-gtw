from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

W, H = A4

doc = SimpleDocTemplate(
    "API.pdf",
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
)

base = getSampleStyleSheet()

BRAND   = colors.HexColor("#1a56db")
DARK    = colors.HexColor("#1e2a3a")
GRAY    = colors.HexColor("#6b7280")
BG_CODE = colors.HexColor("#f3f4f6")
BG_TH   = colors.HexColor("#e5edff")

s_title = ParagraphStyle("title", parent=base["Title"],
    fontSize=24, textColor=BRAND, spaceAfter=4, leading=30)
s_sub = ParagraphStyle("sub", parent=base["Normal"],
    fontSize=11, textColor=GRAY, spaceAfter=20)
s_h1 = ParagraphStyle("h1", parent=base["Heading1"],
    fontSize=15, textColor=DARK, spaceBefore=18, spaceAfter=6,
    borderPad=0, leading=20)
s_h2 = ParagraphStyle("h2", parent=base["Heading2"],
    fontSize=12, textColor=BRAND, spaceBefore=14, spaceAfter=4, leading=16)
s_body = ParagraphStyle("body", parent=base["Normal"],
    fontSize=9.5, textColor=DARK, spaceAfter=6, leading=14)
s_note = ParagraphStyle("note", parent=base["Normal"],
    fontSize=8.5, textColor=GRAY, spaceAfter=6, leading=13,
    leftIndent=10, borderPad=4)
s_code_inline = ParagraphStyle("codei", parent=base["Normal"],
    fontSize=9, fontName="Courier", textColor=colors.HexColor("#c0392b"),
    backColor=BG_CODE)
s_method = ParagraphStyle("method", parent=base["Normal"],
    fontSize=10, fontName="Courier-Bold", textColor=colors.white,
    backColor=BRAND, leading=14, leftIndent=6, rightIndent=6, spaceAfter=8)

def code_block(text):
    return [
        Spacer(1, 4),
        Table(
            [[Preformatted(text, ParagraphStyle("pre", fontName="Courier",
                fontSize=8, leading=12, textColor=DARK))]],
            colWidths=[W - 4*cm],
            style=TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), BG_CODE),
                ("BOX",        (0,0), (-1,-1), 0.5, colors.HexColor("#d1d5db")),
                ("LEFTPADDING",  (0,0), (-1,-1), 8),
                ("RIGHTPADDING", (0,0), (-1,-1), 8),
                ("TOPPADDING",   (0,0), (-1,-1), 6),
                ("BOTTOMPADDING",(0,0), (-1,-1), 6),
            ]),
        ),
        Spacer(1, 6),
    ]

def param_table(headers, rows):
    data = [headers] + rows
    col_n = len(headers)
    col_w = (W - 4*cm) / col_n
    ts = TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  BG_TH),
        ("TEXTCOLOR",    (0,0), (-1,0),  DARK),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#d1d5db")),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
    ])
    t = Table([[Paragraph(str(c), ParagraphStyle("tc", fontName=(
            "Helvetica-Bold" if r == 0 else "Helvetica"),
            fontSize=8.5, leading=11, textColor=DARK))
        for c in row] for r, row in enumerate(data)],
        colWidths=[col_w]*col_n,
        style=ts,
        repeatRows=1,
    )
    return [t, Spacer(1, 8)]

# ── CONTENT ─────────────────────────────────────────────────────────────────
story = []

# Title
story += [
    Spacer(1, 0.5*cm),
    Paragraph("API Reference", s_title),
    Paragraph("pesi-gtw — documentazione di integrazione", s_sub),
    HRFlowable(width="100%", thickness=1, color=BRAND, spaceAfter=18),
]

# ── 1. LOGIN ─────────────────────────────────────────────────────────────────
story += [Paragraph("1. Login — ottenere il token", s_h1)]
story += [Paragraph(
    "Il token è richiesto da tutte le API protette e scade dopo <b>2 giorni</b>. "
    "Dopo la scadenza è necessario effettuare nuovamente il login.", s_body)]

story += [Paragraph("Endpoint", s_h2)]
story += [Paragraph("GET &nbsp;/login/{username}/{password}", s_method)]

story += [Paragraph("Esempio cURL", s_h2)]
story += code_block("curl http://localhost:8000/login/admin/mypassword")

story += [Paragraph("Risposta", s_h2)]
story += code_block('{\n  "token": "abc123...xyz"\n}')

story += [Paragraph(
    "Conserva il valore <b>token</b> e passalo negli endpoint successivi.", s_body)]

story += [HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"), spaceAfter=8)]

# ── 2. LISTA PESATE ───────────────────────────────────────────────────────────
story += [Paragraph("2. Lista pesate", s_h1)]

# 2a
story += [Paragraph("2a. Lista semplice con paginazione", s_h2)]
story += [Paragraph("GET &nbsp;/lista_pesate?offset={offset}&amp;limit={limit}&amp;token={token}", s_method)]

story += param_table(
    ["Parametro", "Tipo", "Default", "Descrizione"],
    [
        ["token",  "string",  "—",      "Token ottenuto dal login"],
        ["offset", "integer", "0",      "Indice di partenza (0 = dal più recente)"],
        ["limit",  "integer", "3000",   "Numero massimo di record restituiti"],
    ]
)

story += [Paragraph("Esempio cURL", s_h2)]
story += code_block(
    'curl "http://localhost:8000/lista_pesate?token=abc123&offset=0&limit=50"'
)

story += [Paragraph("Risposta", s_h2)]
story += code_block("""\
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
}""")

story += [Paragraph("Campi del record pesata", s_h2)]
story += param_table(
    ["Campo", "Descrizione"],
    [
        ["TIPO",       "Tipo pesata"],
        ["ID",         "ID univoco progressivo"],
        ["BIL",        "Identificativo bilancia"],
        ["DATA1/ORA1", "Data e ora prima pesata"],
        ["DATA2/ORA2", "Data e ora seconda pesata"],
        ["PROG1/PROG2","Progressivo operazione"],
        ["BADGE",      "Badge operatore"],
        ["TARGA",      "Targa veicolo"],
        ["CLIENTE",    "Nome cliente"],
        ["FORNITORE",  "Nome fornitore"],
        ["MATERIALE",  "Tipo materiale"],
        ["NOTE1/NOTE2","Note libere"],
        ["PESO1/PESO2","Peso lordo prima/seconda pesata (unità bilancia)"],
        ["PID1/PID2",  "ID tara pre-impostata"],
        ["NETTO",      "Peso netto risultante"],
    ]
)

# 2b
story += [Paragraph("2b. Lista con filtri", s_h2)]
story += [Paragraph(
    "Invia un array JSON nel body per filtrare i risultati. "
    "I filtri vengono combinati nell'ordine in cui sono forniti.", s_body)]
story += [Paragraph(
    "POST &nbsp;/pesate/{token}?offset={offset}&amp;limit={limit}", s_method)]

story += [Paragraph("Body (Content-Type: application/json)", s_h2)]
story += code_block("""\
[
  {
    "campo":      "MATERIALE",
    "operatore":  "=",
    "valore":     "Ghiaia",
    "separatore": "AND"
  },
  {
    "campo":      "DATA1",
    "operatore":  ">=",
    "valore":     "01/04/2026",
    "separatore": ""
  }
]""")

story += param_table(
    ["Chiave", "Descrizione"],
    [
        ["campo",      "Nome colonna (vedi campi disponibili sopra)"],
        ["operatore",  "=  !=  >  <  >=  <=  LIKE"],
        ["valore",     "Valore di confronto"],
        ["separatore", "AND o OR  (stringa vuota sull'ultimo filtro)"],
    ]
)

story += [Paragraph("Esempio cURL", s_h2)]
story += code_block("""\
curl -X POST "http://localhost:8000/pesate/abc123?offset=0&limit=100" \\
  -H "Content-Type: application/json" \\
  -d '[{"campo":"MATERIALE","operatore":"=","valore":"Ghiaia","separatore":""}]'""")

story += [Paragraph("La risposta ha la stessa struttura del punto 2a.", s_note)]
story += [HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"), spaceAfter=8)]

# ── 3. WEBSOCKET ──────────────────────────────────────────────────────────────
story += [Paragraph("3. Peso in tempo reale — WebSocket", s_h1)]
story += [Paragraph(
    "Apri una connessione WebSocket per ricevere il peso aggiornato ogni <b>200 ms</b>. "
    "Se il token non è valido o è scaduto la connessione viene chiusa immediatamente.", s_body)]

story += [Paragraph("Endpoint", s_h2)]
story += [Paragraph("WS &nbsp;/wspesata/{token}", s_method)]

story += [Paragraph("Esempio JavaScript", s_h2)]
story += code_block("""\
const token = "abc123...xyz";
const ws = new WebSocket(`ws://localhost:8000/wspesata/${token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

ws.onclose = () => console.log("Connessione chiusa (token scaduto?)");""")

story += [Paragraph("Messaggio ricevuto (JSON)", s_h2)]
story += code_block("""\
{
  "status":        "Connessa",
  "type":          "NT",
  "gross_weight":  "32400",
  "tare":          "14200",
  "net_weight":    "18200",
  "unite_measure": "Kg"
}""")

story += param_table(
    ["Campo", "Valori possibili", "Descrizione"],
    [
        ["status",        '"Connessa" / "Pesa scollegata"', "Stato connessione bilancia"],
        ["type",          '"GS" = lordo,  "NT" = netto',    "Tipo lettura attiva"],
        ["gross_weight",  "numero o  \"-\"",                "Peso lordo"],
        ["tare",          "numero o  \"-\"",                "Tara"],
        ["net_weight",    "numero o  \"-\"",                "Peso netto"],
        ["unite_measure", '"Kg",  "g",  …',                 "Unità di misura"],
    ]
)

story += [Paragraph(
    'Il valore "-" indica che la bilancia non è ancora connessa o non ha fornito una lettura.',
    s_note)]

story += [HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"), spaceAfter=8)]

# ── 4. CONFIGURAZIONE PESA ────────────────────────────────────────────────────
story += [Paragraph("4. Configurazione della pesa", s_h1)]
story += [Paragraph(
    "Restituisce la configurazione corrente della bilancia. "
    "<b>Non richiede token.</b>", s_body)]

story += [Paragraph("Endpoint", s_h2)]
story += [Paragraph("GET &nbsp;/setup/settingsmachine", s_method)]

story += [Paragraph("Esempio cURL", s_h2)]
story += code_block("curl http://localhost:8000/setup/settingsmachine")

story += [Paragraph("Risposta", s_h2)]
story += code_block("""\
{
  "message": {
    "name_serial": "/dev/ttyUSB0",
    "license_plate_required": false,
    "options_divisions": [1, 2, 5, 10, 20, 50, 100, 200],
    "division_selected": 10,
    "max_weigth": 60000,
    "list_settings": {
      "prog_one": true,   "prog_two": true,
      "pid_one": true,    "pid_two": true,
      "bil": true,
      "customer": { "use": true, "rename": "Operatore" },
      "supplier": { "use": true, "rename": null },
      "material": { "use": true, "rename": null },
      "plate":    { "use": true, "rename": null },
      "net_weight": true,
      "date_time_one": true,  "weight_one": true,
      "date_time_two": true,  "weight_two": true,
      "note_one": false,      "note_two": false,
      "badge": false
    },
    "buttons_settings": {
      "tare": true,  "p_tare": true,  "zero": true,
      "print": false, "weight_one": false, "weight_two": false
    }
  }
}""")

story += param_table(
    ["Campo", "Descrizione"],
    [
        ["name_serial",             "Porta seriale a cui è collegata la bilancia"],
        ["license_plate_required",  "Se true la targa è obbligatoria per completare la pesata"],
        ["options_divisions",       "Valori di divisione disponibili"],
        ["division_selected",       "Divisione attualmente in uso"],
        ["max_weigth",              "Portata massima della bilancia (stessa unità delle pesate)"],
        ["list_settings",           "Visibilità e rinomina dei campi nella lista pesate"],
        ["buttons_settings",        "Pulsanti abilitati nell'interfaccia operatore"],
    ]
)

story += [Paragraph("Dettaglio list_settings", s_h2)]
story += [Paragraph(
    "Ogni campo con <b>use: false</b> è nascosto nell'interfaccia. "
    "Il campo <b>rename</b> sostituisce l'etichetta di default (null = etichetta originale).",
    s_body)]

story += [Paragraph("Dettaglio buttons_settings", s_h2)]
story += param_table(
    ["Chiave", "Pulsante"],
    [
        ["tare",       "Tara manuale"],
        ["p_tare",     "Tara pre-impostata"],
        ["zero",       "Azzeramento bilancia"],
        ["print",      "Stampa scontrino"],
        ["weight_one", "Acquisizione prima pesata"],
        ["weight_two", "Acquisizione seconda pesata"],
    ]
)

doc.build(story)
print("PDF generato: API.pdf")
