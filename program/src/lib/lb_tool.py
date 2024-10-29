######## MODELS ############################

from pydantic import BaseModel
import lb_config
import json
import string
import random
from datetime import datetime, date, timedelta
import lb_config
import hashlib
from typing import Union

class login_res(BaseModel):
    token: str

class message_req(BaseModel):
	text: str
	seconds: int
	token: str 

class targa_req(BaseModel):
	targa: str
	nomeveicolo: str
	tara: int
	token: str
	
class user(BaseModel):
	username: str
	password: str
	descrizione: str
	seclev: int
	
class setup_opcua(BaseModel):
	ip: str
	port: int
	node_realtime: str
	node_lastweight: str
	node_datetime: str
	node_tare: str

class setup_nameserial(BaseModel):
	token: str
	name_serial: str

class list_settings(BaseModel):
	progr: Union[bool, None]
	pid: Union[bool, None]
	bil: Union[bool, None]
	customer: Union[bool, None]
	supplier: Union[bool, None]
	material: Union[bool, None]
	plate: Union[bool, None]
	net_weight: Union[bool, None]
	date_time_one: Union[bool, None]
	weight_one: Union[bool, None]
	date_time_two: Union[bool, None]
	weight_two: Union[bool, None]

class buttons_settings(BaseModel):
	tare: Union[bool, None]
	p_tare: Union[bool, None]
	zero: Union[bool, None]
	print: Union[bool, None]
	weight_one: Union[bool, None]
	weight_two: Union[bool, None]

######## UTILITY ############################

import os
from datetime import datetime, timedelta

def Load(fileName):
	list = []
	fp = lb_config.db_path + fileName
	if os.path.exists(fp):
		try:
			with open(fp, "r") as file:
				list = json.loads(file.read())
		except:
			lb_log.error("(Load)Impossibile importare: %s"% fp)
	else:
		lb_log.error("(Load)File non trovato: %s"% fp)
	return list

def Save(fileName, list):
	fp = lb_config.db_path + fileName
	if os.path.exists(fp):
		try:
			with open(fp, "w") as file:
				my_json = json.dumps(list, indent=4)
				file.write(my_json)
				return True
		except:
			lb_log.error("(Dumps)Impossibile sovrascrivere il file: %s"% fp)
	else:
		lb_log.error("(Dumps)File non trovato: %s"% fp)
	return False

def SearchDictOfList(slist, skey, svalue):
	idx = 0
	for p in slist:
		if p[skey] == svalue:
			return p, idx
		idx = idx + 1
	return None, -1

def is_not_expired(datetime_expire):
    datetime_object_expire = datetime.strptime(datetime_expire, '%d/%m/%Y %H:%M:%S')
    if datetime_object_expire > datetime.now():
        return True
    else:
        return False

def IsAuthorizated(token):
	authorizated = False
	tokenx, idx = SearchDictOfList(lb_config.db_tokens, "token", token)
	if tokenx != None:
		if is_not_expired(tokenx["dateExpire"]):
			userz, idz = SearchDictOfList(lb_config.db_users, "username", tokenx["username"])
			if userz != None:
				if userz["seclev"] == 5:
					authorizated = True
	return authorizated

def FromIdUser():
	idUser = 0
	if lb_config.db_users[0]["username"] == "admin":
		idUser = 1
	return idUser

def HashPassword(password):
	plaintext = password.encode()
	d = hashlib.sha3_256(plaintext)
	hash = d.hexdigest()
	return hash

def CreateToken(username):
	characters = username + string.ascii_letters + string.digits + string.ascii_letters
	token = ''.join(random.choice(characters) for i in range(54))
	dateCreate = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	dateExpire = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M:%S") 
	myDict = {"username": username, "token": token, "dateCreate": dateCreate, "dateExpire": dateExpire}
	lb_config.db_tokens.append(myDict)
	if Save(lb_config.path_tokens, lb_config.db_tokens):
		return token
	return ""
	
def TokenTrue(token):
	tokenx, idx = SearchDictOfList(lb_config.db_tokens, "token", token)
	if tokenx != None:
		if is_not_expired(tokenx["dateExpire"]):
			return True	
	return False
	
def Checksum(stringa):
	totale = 0
	for i in stringa:
		totale = totale + ord(i)
	totale_esa = hex(totale)
	return totale_esa[-2:]
	
def CreatePascode(number: int):
	stringa = ""
	for n in str(number):
		stringa = stringa + chr(65+int(n))
	return stringa
