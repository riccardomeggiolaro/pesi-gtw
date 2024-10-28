import sqlite3
import lb_config
import json
import lb_log

def mainprg():
    while lb_config.g_enabled:
        db_pesate = lb_config.db_pesate

        # Specifica il nome del file SQLite
        nome_file_sqlite = "../db/database.db"

        # Crea una connessione al database
        conn = sqlite3.connect(nome_file_sqlite)

        # Ottieni un cursore per eseguire query SQL
        cursor = conn.cursor()

        # Ora puoi eseguire operazioni sul database come la creazione di tabelle e l'inserimento di dati

        # Esempio: Crea una tabella chiamata "persone" con due colonne
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesate (
                TIPO INTEGER NULL, 
                ID INTEGER NULL, 
                BIL INTEGER NULL, 
                DATA1 TEXT, 
                ORA1 TEXT, 
                DATA2 TEXT, 
                ORA2 TEXT, 
                PROG1 INTEGER NULL, 
                PROG2 INTEGER NULL, 
                BADGE TEXT, 
                TARGA TEXT,
                CLIENTE TEXT,
                FORNITORE TEXT,
                MATERIALE TEXT,
                NOTE1 TEXT,
                NOTE2 TEXT,
                PESO1 INTEGER NULL ,
                PID1 TEXT,
                PESO2 INTEGER NULL,
                PID2 TEXT,
                NETTO INTEGER NULL
            )
        ''')

        # Creazione degli indici per le colonne ID e PID1
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_id ON pesate(ID);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date1 ON pesate(DATA1);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pid1 ON pesate(PID1);')

        # Esempio: Inserisci dati nella tabella
        # import lb_config

        # Esempio di SELECT


        # cursor.execute("DELETE FROM pesate")

        # for pesata in db_pesate:
        #     lb_log.info(pesata)
        #     cursor.execute('''INSERT INTO pesate (
        #             TIPO, 
        #             ID, 
        #             BIL, 
        #             DATA1, 
        #             ORA1, 
        #             DATA2, 
        #             ORA2, 
        #             PROG1, 
        #             PROG2, 
        #             BADGE, 
        #             TARGA,
        #             CLIENTE,
        #             FORNITORE,
        #             MATERIALE,
        #             NOTE1,
        #             NOTE2,
        #             PESO1,
        #             PID1,
        #             PESO2,
        #             PID2,
        #             NETTO) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        #            (pesata["TIPO"], pesata["ID"], pesata["BIL"], pesata["DATA1"], pesata["ORA1"], pesata["DATA2"], pesata["ORA2"], pesata["PROG1"], pesata["PROG2"], pesata["BADGE"], pesata["TARGA"], pesata["CLIENTE"], pesata["FORNITORE"], pesata["MATERIALE"], pesata["NOTE1"], pesata["NOTE2"], pesata["PESO1"], pesata["PID1"], pesata["PESO2"], pesata["PID2"], pesata["NETTO"]))

        # Assicurati di "confermare" le modifiche e chiudere la connessione al database
        conn.commit()
        conn.close()

        while True:
             print("Ciao")

def start():
      lb_log.info("start")
      mainprg()
      while True:
        lb_log.info("Ciao")
      lb_log.info("end")

def init():
	pass
