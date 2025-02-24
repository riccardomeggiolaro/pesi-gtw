# =============================================================
#						- DAT GTW -							  =
# =============================================================
import os
import time
import hashlib
import threading
import sys
import importlib
import signal
import subprocess
import glob
import fastapi

from importlib import reload
from datetime import datetime

class GracefulKiller:
	kill_now = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)

	def exit_gracefully(self, *args):
		lb_log.info("SIGTEM exit")
		lb_config.g_enabled = False

# ==== MAINLOOP ===============================================
def mainprg():
	secwait = 0.5
	lb_config.g_status["board"]={}
	lb_config.g_status["board"]["status-code"] = 0
	lb_config.g_status["board"]["status-code"]=0
	lb_config.g_status["board"]["network"]={}
	lb_config.g_status["board"]["cpu"]={}
	lb_config.g_status["board"]["battery"]={}
	lb_config.g_status["board"]["gsm"]={}
	lb_config.g_status["board"]["gsm"]["imei"]=""
	lb_config.g_status["socket"]={}
	lb_config.g_status["socket"]["server"]=""
	lb_config.g_status["socket"]["port"]=0
	lb_config.g_status["socket"]["is_connected"]=False
	lb_config.g_status["operative"]={}

	# Importazione DB	
	
	thr_logger = threading.Thread(target=lb_log.start)
	thr_data = threading.Thread(target=lb_data.start)
	thr_config = threading.Thread(target=lb_config.start)
	
	# MODULI - Produco elenco moduli
	md_list = glob.glob(lb_config.g_workpath+"modules/md_*.py")
	md_thr = {}
	lb_log.info("loading modules...")
	for modpath in md_list:
		filename = os.path.basename(modpath)
		modulename = os.path.splitext(filename)[0]
		lb_log.info("..."+modulename)
		md_thr[modulename]={}
		md_thr[modulename]["filename"] = filename
		md_thr[modulename]["module"] = importlib.import_module(modulename, package=None)
		md_thr[modulename]["module"].init()
		md_thr[modulename]["thread"] = threading.Thread(target=md_thr[modulename]["module"].start, daemon=True)
		md_thr[modulename]["thread"].start()
		
	# Importazione modulo applicativo
	lb_log.info("loading app module :"+lb_config.g_config["application"]["module"])
	APP = importlib.import_module(lb_config.g_config["application"]["module"], package=None)
	APP.init()

	thr_app = threading.Thread(target=APP.wrk_main)

	while lb_config.g_enabled:
		# === THREAD Livello 0:
		# Config
		if not thr_config.is_alive():
			thr_config = threading.Thread(target=lb_config.start)
			thr_config.start()
		# Drivers
		# Logging
		if not thr_logger.is_alive():
			thr_logger = threading.Thread(target=lb_log.start)
			thr_logger.start()


		# === THREAD Livello 3: Moduli caricati solamente dopo l'inizializizzazione dei drivers
		# Telemetry
		# Data
		if not thr_data.is_alive():
			thr_data = threading.Thread(target=lb_data.start)
			thr_data.start()
		# Application BL
		if not thr_app.is_alive():
			thr_app = threading.Thread(target=APP.wrk_main)
			thr_app.start()
		# Moduli
		for modname in md_thr.keys():
			if not md_thr[modname]["thread"].is_alive():
				md_thr[modname]["thread"] = threading.Thread(target=md_thr[modname]["module"].start)
				md_thr[modname]["thread"].start()
		# Attesa loop
		time.sleep(secwait)

	# Chiusura thread collegati
	#lb_log.info("ending threads:")
	#for modname in md_thr.keys():
	#	if md_thr[modname]["thread"].is_alive():
	#		lb_log.info("..killing: %s"% modname)
	#		md_thr[modname]["thread"].kill()

import socket
def Ip():
    try:
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    s.connect(("8.8.8.8", 80))
	    hostname = s.getsockname()[0]
	    s.close()
	    host = socket.gethostname()
	    return hostname, host
    except:
        return "0.0.0.0", "debianpesa"

if __name__ == "__main__":
	killer = GracefulKiller()
	x_workpath = os.path.dirname(__file__) + "/"
#	pesigtw_path = x_workpath.replace("/src/", "/")
#	ssh = pesigtw_path + "start.sh"
#	os.system(ssh)
	print("system path: "+x_workpath)
	print("navigate: ",end="")
	os.chdir(x_workpath)
	sys.path.append(os.path.join(x_workpath,"app/"))
	sys.path.append(os.path.join(x_workpath,"drivers/"))
	sys.path.append(os.path.join(x_workpath,"lib/"))
	sys.path.append(os.path.join(x_workpath,"modules/"))
	sys.path.append(os.path.join(x_workpath,"extlib/"))
	print("done")

	import lb_log
	import lb_config
	import lb_tool
	# Processo il dato

	import lb_data
	import lb_utility

	# able port usb

	lb_config.initialize()

	lb_config.g_workpath = x_workpath + "/"
	lb_config.g_dbpath = lb_config.g_workpath + "db/"
	lb_config.hostname, lb_config.host = Ip()
	os.system("chmod 777 " + lb_config.nome_seriale)
	print("IP: " + lb_config.hostname)
	
	# Impostazione file di log
	lb_log.init()

	lb_log.info("====================== BARON DAT GTW rel."+lb_config.g_vers+" =======================")

	if lb_config.g_enabled:
		mainprg()
	lb_log.info("exitpoint.")
	print("")

	#sys.exit()
