import os
import json
import time
import shutil

import lb_utility
import lb_log
import lb_tool

from datetime import datetime
from dateutil import tz

import subprocess

import serial

def initialize():

	global pesata
	global g_config
	global g_status
	global g_config_ts
	global g_enabled
	global g_token
	global g_devices
	global g_timer
	global g_initialized
	global g_vers
	global g_idle
	global g_gnss
	global g_workpath
	global g_telemetry
	global g_btbufout
	global g_dbpath
	global g_drvpath
	global g_defalogfile
	global g_tz
	global g_bt_client_socket
	global g_wifi_client_socket

	global db

	global g_serversock
	global g_sslastrasmit
	global g_list_of_clients
	global g_caninterf

	global db_path
	global path_users
	global path_tokens
	global path_pesate
	global path_setup
	global db_users
	global db_tokens
	global db_pesate
	global setup
	global hostname
	global host
	global pesa_real_time
	global last_pesata
	global seriale
	global nome_seriale
	global read_seriale
	global websockets
	global pesata_pid
	global diagnostic
	global pascode
	global superuser
	global valore_alterno
	global pesata_in_esecuzione
	global minWeight
	global weigher_on
	global config_path
	global pesigtw_path
	global anagrafica_in_corso
	global timeRepeat
	global timeRead

	anagrafica_in_corso = ""
	config_path = os.path.dirname(__file__)
	pesigtw_path = config_path.replace("/src/lib", "")
	weigher_on = False
	pesata_in_esecuzione = False
	valore_alterno = 0
	diagnostic = {
					"status": "Pesa scollegata",
					"firmware": "",
					"model_name": "",
					"serial_number": "",
					"vl": "",
					"rz": "",
					"pw": "",
					"bt": ""
				}
	pascode = ""
	superuser = "admin"
	pesata_pid = dict()
	seriale = ""
	read_seriale = ""
	last_pesata = ""
	pesa_real_time = {
	                    "status": "Pesa scollegata", 
	                    "type": "-", 
	                    "gross_weight": "-", 
	                    "tare": "-",
	                    "net_weight": "-",
	                    "unite_measure": "-"
                    }
	hostname = ""
	host = ""
	db_path = pesigtw_path + "/db"
	path_users = "/users.json"
	path_tokens = "/tokens.json"
	path_pesate = "/pesate.json"
	path_setup = "/setup.json"
	db_users = lb_tool.Load(path_users)
	db_tokens = lb_tool.Load(path_tokens)
	db_pesate = lb_tool.Load(path_pesate)
	setup = lb_tool.Load(path_setup)
	nome_seriale = setup["settings_machine"]["name_serial"]
	pesata = list()
	g_vers = "0.0004"
	g_config = {}
	g_status = {}
	g_telemetry = {}
	g_enabled = True
	g_token = ""
	g_devices = []
	g_timer = []
	g_initialized = False
	g_idle = True
	g_gnss = {}
	g_btbufout = []
	g_dbpath = ""
	g_drvpath = ""
	g_serversock = None
	g_workpath = ""
	g_config_ts = ""
	g_defalogfile = pesigtw_path + "/file.log"
	g_tz = tz.gettz('Europe / Rome')
	g_bt_client_socket = None
	g_wifi_client_socket = None
	g_list_of_clients = {}
	g_sslastrasmit = None
	g_caninterf = {}
	minWeight = setup["settings_machine"]["division_selected"] * 20
	timeRead = 1
	timeRepeat = 0.5

	# DB
	db = {}
	db["_info"] = {"updated": []}
	
	lb_log.info("config initialize")
	readconfig()

def saveconfig():
	global g_config,g_config_ts
	global g_tz,g_workpath
	lb_log.info("save config file: config.json")
	with open(g_workpath+"config.json", "w") as config:
		config.write(json.dumps(g_config,indent=4,sort_keys=True))

def readconfig():
	global g_config,g_config_ts
	global g_tz,g_workpath
	xloadbackup = False
	
	if os.path.exists(g_workpath+"config.json"):
		lb_log.info("read config file: config.json")
		g_config_ts = os.stat(g_workpath+"config.json").st_mtime
		try:
			with open(g_workpath+"config.json", "r") as config:
				data=config.read()
				g_config = json.loads(data)
		except:
			lb_log.error("error loading : config.json")
			# Errore nell'apertura della configurazione
			xloadbackup = True
	else:
		lb_log.error("missing configuration : config.json")
		xloadbackup = True

	if xloadbackup:
		# Provo a ripristinare una copia di backup
		if os.path.exists(g_workpath+"config.backup"):
			lb_log.warning("read BACKUP config file: config.backup")
			g_config_ts = os.stat(g_workpath+"config.backup").st_mtime
			try:
				with open(g_workpath+"config.backup", "r") as config:
					data=config.read()
					g_config = json.loads(data)
			except:
				lb_log.error("error loading : config.backup")
			else:
				# Backup caricato correttamente
				# Salvo la configurazione
				lb_log.info("backup restored")
				saveconfig()			
		else:
			lb_log.error("missing backup")

	if "locale" in g_config:
		g_tz = tz.gettz(g_config["locale"]["timezone"]) 

# ==== MAINLOOP ===============================================
def mainprg():
	global g_enabled,g_config_ts,g_workpath
	secwait = 5
	while g_enabled:
		# Verifico presenza file di configurazione
		if os.path.exists(g_workpath+"config.json"):
			# Verifico timestamp configurazione
			if not os.stat(g_workpath+"config.json").st_mtime == g_config_ts:
				readconfig()
		elif os.path.exists(g_workpath+"config.backup"):
			# Presente solo configurazione di backup
			readconfig()
		time.sleep(secwait)
	
def start():
	lb_log.info("start")
	mainprg()
	lb_log.info("end")
