# =======================================================
# 		GESTIONE LOGGER				=
# =======================================================
import os
import json
import time
import inspect

import lb_config

from importlib import reload
from datetime import datetime

l_initiliazed = False

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


# ==== MAINLOOP ===============================================
def mainprg():
	secwait = 5
	while lb_config.g_enabled:
		# Gestisco log
		if os.path.exists(lb_config.g_defalogfile):
			file_size = os.path.getsize(lb_config.g_defalogfile)/1048576
			# Verifico dimensione massima ammessa file di log
			if file_size >= lb_config.g_config["log"]["max-size-mb"]:
				os.remove(lb_config.g_defalogfile)
		time.sleep(secwait)

def init():
	lb_config.g_defalogfile = lb_config.g_workpath+"gateway.log"

def debug(msg):
	defa_logfile = lb_config.g_defalogfile
	now = datetime.now() # current date and time
	module = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0].lower()
	if len(module) > 10:
		module = module[:9]+"~"
	else:
		module = module.ljust(10)
	module = module + "|"
	print("")

	print("(debug)"+now.strftime("%Y/%m/%d %H:%M:%S"),module,msg,end="")

def info(msg):
	defa_logfile = lb_config.g_defalogfile
	now = datetime.now() # current date and time
	module = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0].lower()
	if msg is not str:
		msg = str(msg)

	if len(module) > 10:
		module = module[:9]+"~"
	else:
		module = module.ljust(10)
	module = module + "|"
	newline()
	if lb_config.g_defalogfile:
		with open(lb_config.g_defalogfile, 'a') as f:
			f.write(("I")+now.strftime(" %Y/%m/%d %H:%M:%S ")+module.ljust(10)+msg)

	print(f"{bcolors.OKGREEN}(info){bcolors.ENDC}",end="")
	print(now.strftime("%Y/%m/%d %H:%M:%S"),module,msg,end="")

def newline():
	defa_logfile = lb_config.g_defalogfile
	if defa_logfile:
		with open(defa_logfile, 'a') as f:
			f.write(chr(13)+chr(10))

	print("")

def warning(msg):
	defa_logfile = lb_config.g_defalogfile
	now = datetime.now() # current date and time
	module = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0].lower()
	if msg is not str:
		msg = str(msg)

	if len(module) > 10:
		module = module[:9]+"~"
	else:
		module = module.ljust(10)
	module = module + "|"
	newline()
	if defa_logfile:
		with open(defa_logfile, 'a') as f:
			f.write(("W")+now.strftime(" %Y/%m/%d %H:%M:%S ")+module.ljust(10)+msg)

	print(f"{bcolors.WARNING}(warn){bcolors.ENDC}",now.strftime("%Y/%m/%d %H:%M:%S"),module,msg,end="")

def error(msg):
	defa_logfile = lb_config.g_defalogfile
	now = datetime.now() # current date and time
	module = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0].lower()
	if msg is not str:
		msg = str(msg)

	if len(module) > 10:
		module = module[:9]+"~"
	else:
		module = module.ljust(10)
	module = module + "|"
	newline()
	if lb_config.g_defalogfile:
		with open(lb_config.g_defalogfile, 'a') as f:
			f.write(("E")+now.strftime(" %Y/%m/%d %H:%M:%S ")+module.ljust(10)+msg)

	print(f"{bcolors.FAIL}(err!){bcolors.ENDC}",now.strftime("%Y/%m/%d %H:%M:%S"),module,msg,end="")

def inline(msg,att=""):
	if msg is not str:
		msg = str(msg)
	if att:
		print(att,end="")
	if lb_config.g_defalogfile:
		with open(lb_config.g_defalogfile, 'a') as f:
			f.write(msg)

	print(msg,end="")
	if att:
		print(f"{bcolors.ENDC}",end="")


def start():
	info("start")
	mainprg()
	info("end")

