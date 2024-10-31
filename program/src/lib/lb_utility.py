import asyncio
import hashlib
import pickle
import os
import ast
import json
import sqlite3

import lb_config
import lb_log

from datetime import datetime

def exec_return(run,package = "",module = "",pars={}):
	if package:
		str = "from " + package + " import " + module + "; xxxret="+module+"."+run
	elif module:
		str = "import " + module + "; xxxret="+module+"."+run
	else:
		str = "xxxret="+module+"."+run

	context = pars
	exec(str,context)

	return context['xxxret']

def md5sum_f(filename,format="s"):
	md5 = ""
	if os.path.exists(filename):
		if format == "s":
			with open(filename) as f:
				md5 = hashlib.md5(f.read().encode()).hexdigest()
		elif format == "b":
			with open(filename,"rb") as f:
				md5 = hashlib.md5(f.read()).hexdigest()
	return md5

# Calcolo differenziale tra due dizionari	
def dictdelta(nuovo,vecchio):
	delta = {}
	for el in nuovo:
		if el in vecchio:
			# verifico valori
			if not(nuovo[el] == vecchio[el]):
				delta[el]=nuovo[el]
		else:
			# Chiave non presente nel vecchio
			delta[el]=nuovo[el]

	return delta

def intnone(string):
	try:
		return int(string)
	except:
		return 0

def replacestringinfile(filepath,old_string,new_string):
	if os.path.exists(filepath):
		fin = open(filepath, "rt")
		data = fin.read()
		data = data.replace(old_string, new_string)
		fin.close()
		fin = open(filepath, "wt")
		fin.write(data)
		fin.close()

def searchlistofdict(slist,skey,svalue):
	idx = 0
	for p in slist:
		if p[skey] == svalue:
			return p,idx
		idx = idx + 1
	return None,-1


def set_defa(key,where,default):
	if not key in where:
		where[key]=default

async def Attend():
	i = 0
	while i < 20:				
		await asyncio.sleep(1)
		if not lb_config.pesata_in_esecuzione:
			break
		i = i + 1

def generate_insert_query(data):
    # Ottenere i nomi delle colonne e i valori non vuoti
    columns = ', '.join(key for key, value in data.items() if value != '')
    values = ', '.join(f"'{value}'" for key, value in data.items() if value != '')

    # Costruire la query completa
    insert_query = f'''
        INSERT INTO pesate ({columns})
        VALUES ({values});
    '''

    return insert_query

def add(pesata):
	try:
		nome_db_pesate = "../db/database.db"
		conn = sqlite3.connect(nome_db_pesate)
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO pesate (
				TIPO, 
				ID, 
				BIL, 
				DATA1, 
				ORA1, 
				DATA2, 
				ORA2, 
				PROG1, 
				PROG2, 
				BADGE, 
				TARGA,
				CLIENTE,
				FORNITORE,
				MATERIALE,
				NOTE1,
				NOTE2,
				PESO1,
				PID1,
				PESO2,
				PID2,
				NETTO) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
				(
					pesata["TIPO"],
					pesata["ID"],
					pesata["BIL"],
					pesata["DATA1"],
					pesata["ORA1"],
					pesata["DATA2"],
					pesata["ORA2"],
					pesata["PROG1"],
					pesata["PROG2"],
					pesata["BADGE"],
					pesata["TARGA"],
					pesata["CLIENTE"],
					pesata["FORNITORE"],
					pesata["MATERIALE"],
					pesata["NOTE1"],
					pesata["NOTE2"],
					pesata["PESO1"],
					pesata["PID1"],
					pesata["PESO2"],
					pesata["PID2"],
					pesata["NETTO"]))
		conn.commit()
		conn.close()
		lb_log.info("Pesata salvata")
		lb_config.pesata_in_esecuzione = False
	except sqlite3.Error as e:
		lb_log.error("Errore SQLite:", e)
	except:
		lb_log.error("Errore nel salvataggio della pesata %s"% (pesata))

def getByPid(key, value):
	try:
		nome_db_pesate = "../db/database.db"
		conn = sqlite3.connect(nome_db_pesate)
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM pesate WHERE %s = '%s' AND TIPO = 1 LIMIT 1"% (key, value))
		row = cursor.fetchone()
		if(row is None):
			lb_log.info("Pesata non trovata %s %s"% (key, value))
			return None
		conn.commit()
		conn.close()
		return 	{
			"TIPO": row[0],
			"ID": row[1],
			"BIL": row[2],
			"DATA1": row[3],
			"ORA1": row[4],
			"DATA2": row[5],
			"ORA2": row[6],
			"PROG1": row[7],
			"PROG2": row[8],
			"BADGE": row[9],
			"TARGA": row[10],
			"CLIENTE": row[11],
			"FORNITORE": row[12],
			"MATERIALE": row[13],
			"NOTE1": row[14],
			"NOTE2": row[15],
			"PESO1": row[16],
			"PID1": row[17],
			"PESO2": row[18],
			"PID2": row[19],
			"NETTO": row[20]
		}
	except sqlite3.Error as e:
		lb_log.error("Errore SQLite:", e)
	except:
		lb_log.error("Errore nella ricerca della pesata %s %s"% (key, value))
		
def getById(id1, data1, ora1):
	try:
		nome_db_pesate = "../db/database.db"
		conn = sqlite3.connect(nome_db_pesate)
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM pesate WHERE ID = %s AND DATA1 = '%s' AND ORA1 = '%s' AND TIPO = 1 LIMIT 1"% (id1, data1, ora1))
		row = cursor.fetchone()
		if(row is None):
			lb_log.info("Pesata non trovata ID %s"% (id1))
			return None
		conn.commit()
		conn.close()
		return 	{
			"TIPO": row[0],
			"ID": row[1],
			"BIL": row[2],
			"DATA1": row[3],
			"ORA1": row[4],
			"DATA2": row[5],
			"ORA2": row[6],
			"PROG1": row[7],
			"PROG2": row[8],
			"BADGE": row[9],
			"TARGA": row[10],
			"CLIENTE": row[11],
			"FORNITORE": row[12],
			"MATERIALE": row[13],
			"NOTE1": row[14],
			"NOTE2": row[15],
			"PESO1": row[16],
			"PID1": row[17],
			"PESO2": row[18],
			"PID2": row[19],
			"NETTO": row[20]
		}
	except sqlite3.Error as e:
		lb_log.error("Errore SQLite:", e)
	except:
		lb_log.error("Errore nella ricerca della pesata ID %s"% (id1))

def delete(key, value):
	try:
		nome_db_pesate = "../db/database.db"
		conn = sqlite3.connect(nome_db_pesate)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM pesate WHERE %s = '%s' LIMIT 1"% (key, value))
		conn.commit()
		conn.close()
	except sqlite3.Error as e:
		lb_log.error("Errore SQLite:", e)
	except:
		lb_log.error("Errore nella cancellazione della pesata %s %s"% (key, value))

def generate_update_query(data, id1, pid1, data1, ora1):
	# Creare la parte SET della query con i valori non vuoti
	set_clause = ', '.join(f"{key} = '{value}'" for key, value in data.items() if value != '')
	# Costruire la query completa
	update_query = f'''
		UPDATE pesate
		SET {set_clause}
		WHERE ID = {id1} AND PID1 = '{pid1}' AND DATA1 = '{data1}' AND ORA1 = '{ora1}' AND TIPO = 1;
	'''
	return update_query

def update(id1, pid1, data1, ora1, pesata):
	try:
		update_query = generate_update_query(pesata, id1, pid1, data1, ora1)
		nome_db_pesate = "../db/database.db"
		conn = sqlite3.connect(nome_db_pesate)
		cursor = conn.cursor()
		cursor.execute(update_query)
		conn.commit()
		conn.close()
		lb_log.info("Pesata aggiornata")
		lb_config.pesata_in_esecuzione = False
	except sqlite3.Error as e:
		lb_log.error("Errore SQLite:", e)
	except:
		lb_log.error("Errore nell'aggiornamento della pesata %s" % (pesata))

