# ==============================================================
# = Module......: md_pesa_dini					   =
# = Description.: Interfaccia di pesatura DINI			   =
# = Author......: Riccardo Meggiolaro				   =
# = Last rev....: 0.0002					   =
# -------------------------------------------------------------=
# 0.0002 : Implementato....
# 0.0001 : Creazione del modulo
# ==============================================================
import time
import json
import os
import lb_config
import lb_tool
import lb_utility
import lb_log
import serial
import md_webservice
from threading import Timer
import re
import asyncio
import time
from typing import Union

from datetime import datetime,timedelta, date
from dateutil.parser import parse

class RepeatTimer(Timer):
	def run(self):
		while not self.finished.wait(self.interval):
			self.function(*self.args, **self.kwargs)

# ==== MAINLOOP ===============================================
def mainprg():

	while lb_config.g_enabled:
		pesata_continua()
		try:
			lb_config.read_seriale = lb_config.seriale.readline().decode().replace("\r\n", "")
		except Exception as e:
			lb_log.error(e)
#		print(lb_config.read_seriale)
		if not lb_config.read_seriale:
			lb_config.diagnostic["vl"] = ""
			lb_config.diagnostic["rz"] = ""
		elif lb_config.read_seriale.startswith("{"):
			lb_config.pesata_pid = json.loads(lb_config.read_seriale)
			#salvataggio pesata 1
			if lb_config.pesata_pid["TIPO"] == "1" or lb_config.pesata_pid["TIPO"] == "3" or lb_config.pesata_pid["TIPO"] == "4":
				#print(lb_config.pesata_pid)
				PesataCheck()
				lb_utility.add(lb_config.pesata_pid)
			elif lb_config.pesata_pid["TIPO"] == "2":
				#print(lb_config.pesata_pid)
				PesataCheck()
				#salvataggio pesata 2
				#trovo pesa 1 con stesso PID1
				pesataTrovata = None
				#lb_config.pesata_pid["ID"] = 0
				if lb_config.pesata_pid["PID1"]:
					pesataTrovata = lb_utility.getByPid("PID1", lb_config.pesata_pid["PID1"])
				else:
				    pesataTrovata = lb_utility.getById(lb_config.pesata_pid["ID"], lb_config.pesata_pid["DATA1"], lb_config.pesata_pid["ORA1"])
				#per ogni chiave valore di pesata 1 controllo se è vuoto o se ha un valore, così da riempirlo in base alle condizioni
				if pesataTrovata != None:
					for key, value in pesataTrovata.items():
						#se il valore di key è diverso da vuoto in pesata 1 e vuoto in pesato 2 passo
						if pesataTrovata[key] != "" and lb_config.pesata_pid[key] == "":
							pass
						#se il valore di key è vuoto in pesata 1 e pieno in pesata 2 aggiorno il valore su pesata 1
						elif pesataTrovata[key] == "" and lb_config.pesata_pid[key] != "":
							pesataTrovata[key] = lb_config.pesata_pid[key]
						#se il valore di key è pieno sia su pesata 1 che su pesata 2 aggionro il valore su pesata 1
						elif pesataTrovata[key] != "" and lb_config.pesata_pid[key] != "":
							pesataTrovata[key] = lb_config.pesata_pid[key]
					#aggiorno il dict pesata 1 sul db pesate e salvo
					pesataAggiornata = pesataTrovata
					# lb_utility.delete("PID1", pesataAggiornata["PID1"])
					# lb_utility.add(pesataAggiornata)
					lb_utility.update(pesataTrovata["ID"], pesataTrovata["PID1"], pesataTrovata["DATA1"], pesataTrovata["ORA1"], pesataTrovata)
				else:
					lb_utility.add(lb_config.pesata_pid)
		elif len(lb_config.read_seriale.split(",")) == 4:
			lb_log.info(lb_config.read_seriale)
			if lb_config.read_seriale.split(",")[1].isdigit():
				#splitto la pesata in real time
				lst_peso = lb_config.read_seriale.split(",")
				#se la lista ha 4 valori salvo i valori su un dizionario globale
				if len(lst_peso) == 4:
					try:
						#gestisco i valori delle pesate
						gwstring = lst_peso[2].lstrip()
						gw = None
						if "." in gwstring:
						    gw = float(re.sub('[KkGg\x00\n]', '', lst_peso[2].lstrip()))
						else:
						    gw = int(re.sub('[KkGg\x00\n]', '', lst_peso[2].lstrip()))
						tpt = re.sub('[KkGg\x00\n]', '', lst_peso[3].lstrip())
						tstring = lst_peso[3].lstrip()
						t = None
						if "." in tstring:
						    t = float(re.sub('[PTKkGg\x00\n]', '', lst_peso[3].lstrip()))
						else:
						    t = int(re.sub('[PTKkGg\x00\n]', '', lst_peso[3].lstrip()))
						lb_config.pesa_real_time["status"] = lst_peso[0]
						#calcolo il tipo di peso
						lb_config.pesa_real_time["type"] = TypeWeight(lst_peso[3])
						lb_config.pesa_real_time["gross_weight"] = gw
						lb_config.pesa_real_time["tare"] = tpt
						#calcolo il peso netto
						lb_config.pesa_real_time["net_weight"] = NetWeight(gw, t)
						#calcolo l'unità di misura
						lb_config.pesa_real_time["unite_measure"] = UniteMeasure(gwstring)
					except Exception as e:
						lb_log.warning(e)
			elif lb_config.read_seriale.split(",")[1] == "VL":
				lst_vl = lb_config.read_seriale.split(",")
				lb_config.diagnostic["vl"] = str(lst_vl[2]) + " " + str(lst_vl[3])
#				print(lb_config.diagnostic["vl"])
			elif lb_config.read_seriale.split(",")[1] == "RZ":
				lst_rz = lb_config.read_seriale.split(",")
				lb_config.diagnostic["rz"] = str(lst_rz[2]) + " " + str(lst_rz[3])
#				print(lb_config.diagnostic["rz"])
		elif lb_config.read_seriale.split(" ")[0] == "PW:":
			lst_pw_bt = lb_config.read_seriale.split(" ")
			lb_config.diagnostic["pw"] = str(lst_pw_bt[1]) + " V"
			lb_config.diagnostic["bt"] = str(lst_pw_bt[3]) + " V"
		time.sleep(0.4)

def PesataCheck():
	for key, value in lb_config.pesata_pid.items():
		if key != "TARGA":
			if IsDate(key, value):
				pass
			if IsTime(key, value):
	#			print("Is Time")
				pass
			if IsInt(key, value):
	#			print("Is Int")
				pass
		if key == "PID1" or key == "PID2":
			if IsPid(key, value):
				pass

def converti_data(data):
	# Dividi la data in giorno, mese e anno
    giorno, mese, anno = data.split('/')

    # Ottieni l'anno attuale
    anno_attuale = datetime.now().year
    
    # Ricomponi la data nel formato "dd/mm/yyyy"
    nuova_data = f"{giorno}/{mese}/{anno_attuale}"
    
    return nuova_data

def IsDate(key: str, value: str):
	try: 
		lb_config.pesata_pid[key] = converti_data(value)
		return True
	except ValueError:
		return False

def IsTime(key: str, value: str):
	try:
		return True
	except ValueError:
		return False

def IsInt(key: str, value: str):
	try: 
		numParse = int(value)
		lb_config.pesata_pid[key] = numParse
		return True
	except ValueError:
		return False
	
def IsPid(key: str, value: str):
	try:
		pid = ''.join(['0' if char == ' ' else char for char in value])
		lb_config.pesata_pid[key] = pid
		return True
	except ValueError:
		return False

#in base a se la tara è uguale a 0 o no stabilisco se è un peso lordo o netto 
def TypeWeight(tare: str):	
	t = tare.strip()
	if t.startswith("0"):
		return "GS"
	return "NT"

#ritorno la differenza tra il peso lordo e la tara
def NetWeight(gross_weight: Union[float, int], tare: Union[float, int]):
	net = gross_weight - tare
	return net

#ottengo le lettere che indicano l'unità di misura da uns stringa contente un peso e l'unità di misura	
def UniteMeasure(weight: Union[float, int]):
	um = ""
	for l in weight:
		if l in "KkGg":
			um = um + l
	return um

#comando da mandare alla pesa
def comando(cmd):
	command = (cmd + chr(13)+chr(10)).encode()
	lb_config.seriale.write(command)

def ver():
	while True:
		try:
			if lb_config.nome_seriale:
				lb_config.seriale = serial.Serial(lb_config.nome_seriale, 9600, timeout=lb_config.timeRead)
				comando("VER")
				lb_config.read_seriale = lb_config.seriale.readline().decode().replace("\r\n", "")
				values = lb_config.read_seriale.split(",")
				lb_config.diagnostic["firmware"] = values[1]
				lb_config.diagnostic["model_name"] = values[2]
				comando("SN")
				lb_config.read_seriale = lb_config.seriale.readline().decode().replace("\r\n", "")
				lb_config.diagnostic["serial_number"] = int(lb_config.read_seriale[3:].lstrip())
				pascode = lb_tool.CreatePascode(lb_config.diagnostic["serial_number"])
				userAdmin = {
					"username": "admin",
					"password": lb_tool.HashPassword(pascode),
					"descrizione": "Admin",
					"seclev": 5
				}
				comando("DINT2710")
				comando("DISP00" + str(lb_config.hostname) + " " + str(lb_config.host))
				if lb_config.diagnostic["firmware"] and lb_config.diagnostic["model_name"] and lb_config.diagnostic["serial_number"]:
					lb_config.diagnostic["status"] = "Pesa collegata"
					lb_config.weigher_on = True
					lb_config.db_users.insert(0, userAdmin)
					lb_log.info("SUPERUSER: " + lb_config.db_users[0]["username"])
					lb_log.info("PASCODE: " + pascode)
					lb_log.info("INFOSTART: " + "Accensione con successo")
					lb_log.info("FIRMWARE: " + lb_config.diagnostic["firmware"]) 
					lb_log.info("MODELNAME: " + lb_config.diagnostic["model_name"])
					lb_log.info("SERIALNUMBER: " + str(lb_config.diagnostic["serial_number"]))
					break
		except Exception as e:
			lb_log.error(e)
						

#se c'è almeno una connessione socket mando il comando di lettura alla pesa
def pesata_continua():
	if len(md_webservice.manager_diagnostic.active_connections):
		if lb_config.valore_alterno == 1:
			comando("MVOL")
		elif lb_config.valore_alterno == 2:
			comando("RAZF")
		else:
			comando("ALIMN")			
			lb_config.valore_alterno = 0
		if lb_config.read_seriale:
			lb_config.pesa_real_time["status"] = "MANUTENZIONE"
			lb_config.diagnostic["status"] = "MANUTENZIONE"
		lb_config.valore_alterno = lb_config.valore_alterno + 1
		lb_config.pesa_real_time["type"] = "--"
		lb_config.pesa_real_time["gross_weight"] = "--"
		lb_config.pesa_real_time["tare"] = "--"
	if len(md_webservice.manager.active_connections) and len(md_webservice.manager_diagnostic.active_connections) == 0 and not lb_config.pesata_in_esecuzione and not lb_config.anagrafica_in_corso:
		comando("R")
	if lb_config.pesata_in_esecuzione:
		lb_config.pesa_real_time["status"] = "pesata in corso"
		lb_config.diagnostic["status"] = "pesata in corso"
	if lb_config.anagrafica_in_corso:
		lb_config.pesa_real_time["status"] = "anagrafica in corso"
		lb_config.diagnostic["status"] = "anagrafica in corso"
	if not lb_config.read_seriale and not lb_config.pesata_in_esecuzione:
		lb_config.pesa_real_time["status"] = "pesa scollegata"
		lb_config.diagnostic["status"] = "pesa scollegata"

def start():
	lb_log.info("start")
	ver()
	#inserisco thread parallelo per pesate in continua
	mainprg()
	lb_log.info("end")

def init():
	pass
