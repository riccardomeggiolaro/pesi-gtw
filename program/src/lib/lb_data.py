# =============================================================
# =                - GESTIONE DATI -                          =
# =============================================================
import time
import json
import os
import hashlib

import lb_config
import lb_log
import lb_utility

# ==== MAINLOOP ===============================================
def mainprg():
	secwait = 0.5
	maxrecordset = 4000
	#lb_config.g_status
	while lb_config.g_enabled:
		if lb_config.g_status["socket"]["is_connected"]:
			# =======================================================
			# pathfinder (è un buffer, localmente non dovrebbe esistere)
			# =======================================================
			rcnt = len(lb_config.db["pathfinder"])
			rcpr = 0
			if rcnt > 0:
				recordset = []
				lstb = []
				rstr = ""
				rlen = 0
				lb_log.info("pathfinder:resync buffer:")
				for rec in lb_config.db["pathfinder"]:
					rstr = rec["dt"]+chr(2)+str(rec["lt"])+chr(2)+str(rec["lo"])+chr(2)+str(rec["al"])+chr(2)+str(rec["ut"])+chr(2)+rec["np"]+chr(2)+str(rec["kh"])+chr(2)+str(rec["cp"])
					# Lista di backup per successiva archiviazione
					lstb.append(rec)
					# Recordset
					recordset.append(rstr)
					# Lunghezza stream
					rlen = rlen + len(rstr)
					# Record processati
					rcpr = rcpr + 1
					if rlen >= maxrecordset:
						# Raggiunta la massima lunghezza ammessa per un recordset
						break
				if lb_client.transmit(32,recordset):
					for rec in lstb:
						lb_config.db["pathfinder"].remove(rec)
						savedata("pathfinder")
					lb_log.inline(str(rcpr)+"/"+str(rcnt))
				else:
					# Errore nella trasmissione del dataset
					lb_log.warning("error sync: pathfinder")
			# =======================================================
			# currentjob_rows
			# =======================================================
			if "currentjob_rows" in lb_config.db["_info"]["updated"]:
				sendb(lb_config.db["currentjob_rows"],"currentjob_rows",["job","rowid","rowtype","idstype","idscode","poid","poilat","poilon","poialt","state"])
			# =======================================================
			# currentjob_geo
			# =======================================================
			if "currentjob_geo" in lb_config.db["_info"]["updated"]:
				sendb(lb_config.db["currentjob_geo"],"currentjob_geo")
			# =======================================================
			# Tabelle da propagare (verso i client)
			# =======================================================
			# glb_telemetry
			# =======================================================


			# Azzero stato tabelle da sincronizzare
			lb_config.db["_info"]["updated"] = []

		time.sleep(secwait)



def savedata(dbname,list=None):
	dbfile = os.path.splitext(dbname)[0] + ".json"
	out_file = open(lb_config.g_dbpath+dbfile, "w")
	if list is None:
		list = lb_config.db[dbname]
	json.dump(list, out_file, indent = 4, sort_keys=False, default=str)		
	out_file.close()
	if not dbfile in lb_config.db["_info"]["updated"]:
		lb_config.db["_info"]["updated"].append(dbname)
	return True

def start():
	lb_log.info("start")
	mainprg()
	lb_log.info("end")

def sendb(data,dbname,fieldlist=[]):
	payload = []
	jhash,payload = dumprecords(data,"db/"+dbname,fieldlist)

	if len(payload):
		lb_log.info("sending %s"% dbname)
	else:
		lb_log.info("sending %s:no payload(abort)"% dbname)

def dumprecords(qry,dbname="",fieldlist=[]):
	# Simulo file json e relativo HASH
	jrec = json.dumps(qry,indent=4,sort_keys=True)
	jrec_hash = hash(jrec,32)
	payload = []
	if dbname:
		payload.append(dbname)
	# Calcolo datastream
	datatrack = ""
	if len(qry):
		# Se fieldlist vuota la calcolo su tutti i campi
		if len(fieldlist) == 0:
			fieldlist = qry[0].keys()

		for field in fieldlist:
			if datatrack:
				datatrack = datatrack + "+chr(2)+"
			if type(qry[0][field]) is str:
				datatrack = datatrack + 'rec["'+field+'"]'
			elif type(qry[0][field]) is int:
				datatrack = datatrack + 'str(rec["'+field+'"])'
			elif type(qry[0][field]) is float:
				datatrack = datatrack + 'str(rec["'+field+'"])'
			else:
				lb_log.warning(field +":"+str(type(qry[0][field])))
		for rec in qry:
			#lb_log.debug(datatrack)
			payload.append(eval(datatrack))

	return jrec_hash,payload


def hash(string,lenght=1):
	return int.from_bytes(hashlib.shake_128(string.encode()).digest(lenght),"little")


