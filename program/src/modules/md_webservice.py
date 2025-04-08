from io import BytesIO
import os

import aiosqlite
import openpyxl
import lb_config
import lb_log
import lb_config
from http.server import HTTPServer, BaseHTTPRequestHandler
from fastapi import FastAPI, HTTPException, Response, WebSocket, WebSocketDisconnect
from typing import Union
import uvicorn
import lb_tool
import lb_utility
from lb_tool import *
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio
import serial
import md_pesa_dini
from datetime import datetime, date
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import pandas as pd
from fastapi.responses import FileResponse
import sqlite3

# ==== MAINLOOP ===============================================

# create connectio manager of weight real time
class ConnectionManager:
	def __init__(self):
		self.active_connections: list[WebSocket] = []

	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.active_connections.append(websocket)

	def disconnect(self, websocket: WebSocket):
		self.active_connections.remove(websocket)

	async def send_personal_message(self, message: str, websocket: WebSocket):
		await websocket.send_text(message)

	async def broadcast(self, message: str):
		for connection in self.active_connections:
			try:
				await connection.send_json(message)
			except:
				#print("client down")
				self.disconnect(connection)
	
manager = ConnectionManager()
manager_diagnostic = ConnectionManager()
manager_anagrafica = ConnectionManager()

MAX_VALUES = 250

def mainprg():

	app = FastAPI()

	app.add_middleware(
		CORSMiddleware, 
		allow_origins=["*"],
		allow_credentials=True,
	    allow_methods=["*"],
    	allow_headers=["*"],
	)

	# function for login
	@app.get("/login/{username}/{password}")
	async def Login(username: str, password: str):
		login_response = HTTPException(status_code=404, detail="NOT AUTHENTICATED")
		try:
			user, id = lb_tool.SearchDictOfList(lb_config.db_users, "username", username) # search key value pair that contains username
			token = ""
			if user: # if user found hash password and check if is equal to password found
				if user["password"] == lb_tool.HashPassword(password): 
					token = lb_tool.CreateToken(username) # create token
					if token:
						login_response = login_res(token=token)
		except:
			login_response = HTTPException(status_code=400, detail="SYNTAX ERROR")
		return login_response

	# function for get personal data	
	@app.get("/user/{token}")
	async def User(token: str):
		message = HTTPException(status_code=404, detail="NOT AUTHENTICATED")
		try:
			tokenx, idx = lb_tool.SearchDictOfList(lb_config.db_tokens, "token", token)
			if tokenx != None and lb_tool.is_not_expired(tokenx["dateExpire"]):
				username = tokenx["username"]
				userz, idz = lb_tool.SearchDictOfList(lb_config.db_users, "username", username)
				if userz != None:
					return lb_tool.user(username=userz["username"], password=userz["password"], descrizione=userz["descrizione"], seclev=userz["seclev"])
		except:
			message = HTTPException(status_code=400, detail="SYNTAX ERROR")
		return message

	# function to add new user				
	@app.post("/adduser/{token}")
	async def Adduser(user: lb_tool.user, token: str):
		message = HTTPException(status_code=403, detail="NOT AUTHORIZATION")
		authorizated = False
		try:
			authorizated = lb_tool.IsAuthorizated(token)
			if authorizated:
				justUser, justId = lb_tool.SearchDictOfList(lb_config.db_users, "username", user.username)
				if justUser == None:
					newUser = {
						"username": user.username,
						"password": lb_tool.HashPassword(user.password),
						"descrizione": user.descrizione,
						"seclev": user.seclev
					}
					lb_config.db_users.append(newUser)
					fromIdUser = lb_tool.FromIdUser()
					db_users = lb_config.db_users[fromIdUser:]
					if lb_tool.Save(lb_config.path_users, db_users):
						message = {"message": "Nuovo utente aggiunto"}
					else:
						message = HTTPException(status_code=400, detail="ERROR ON SAVE")
				else:
					message = {"message": "Username già in uso"}
		except:
			message = HTTPException(status_code=400, detail="SYNTAX ERROR")
		return message

	# function to get list of user
	@app.get("/alluser/{token}")
	async def Alluser(token: str):
		message = HTTPException(status_code=403, detail="NO AUTHORIZATION")
		authorizated = False
		try:
			authorizated = lb_tool.IsAuthorizated(token)
			if authorizated:
				return lb_config.db_users
		except:
			message = HTTPException(status_code=400, detail="SYNTAX ERROR")
		return message

	# function to delete a user	
	@app.delete("/deleteuser/{username}/{token}")
	async def Deleteuse(username: str, token: str):
		message = ""
		authorizated = False
		try:
			authorizated = lb_tool.IsAuthorizated(token)
			if authorizated:
				userdelete, iddelete = lb_tool.SearchDictOfList(lb_config.db_users, "username", username)
				if userdelete != None and userdelete["username"] != "admin":
					del lb_config.db_users[iddelete]
					fromIdUser = lb_tool.FromIdUser()
					if lb_tool.Save(lb_config.path_users, lb_config.db_users[fromIdUser:]):
						message = {"message": "Utente eliminato"}
					else:
						message = {"message": "Errore nel salvataggio"}
				elif userdelete != None and userdelete["username"] == "admin":
					message = {"message": "Non puoi eliminare un amministratore"}
				else:
					message = {"message": "Username non trovato"}
			else:
				message = HTTPException(status_code=404, detail="NOT AUTHORIZATION")
		except:
			message = HTTPException(status_code=400, details="SYNTAX ERROR")
		return message
	
	# function to put a user
	@app.put("/putuser/{token}")
	async def Putuser(changes: dict, token: str):
		message = ""
		try:
			tokenx, idx = lb_tool.SearchDictOfList(lb_config.db_tokens, "token", token)
			if lb_tool.is_not_expired(tokenx["dateExpire"]):
				username = tokenx["username"]
				userz, idz = lb_tool.SearchDictOfList(lb_config.db_users, "username", username)
				if userz != None and userz["username"] != "admin":
					for key, value in changes.items():
						if key in userz:
							if key == "password":
								lb_config.db_users[idz][key] = lb_tool.HashPassword(value)
							else:
								lb_config.db_users[idz][key] = value
					fromIdUser = lb_tool.FromIdUser()
					if lb_tool.Save(lb_config.path_users, lb_config.db_users[fromIdUser:]):
						newToken = lb_tool.CreateToken(lb_config.db_users[idz]["username"])
						if newToken:
							message = {"message": "Utente modificato", "new_token": newToken}
				elif userz != None and userz["username"] == "admin":
					message = {"message": "Non puoi modificare un amministratore"}
				else:
					message = {"message": "Utente non trovato"}
			else:
				message = HTTPException(status_code=404, details="NOT AUTHENTICATED")
		except:
			message = HTTPException(status_code=400, details="SYNTAX ERROR")
		return message
	
	# function to change the password
	@app.get("/password/{token}/{password}")
	async def Password(token: str, password: str):
		message = ""
		try:
			tokenx, idx = lb_tool.SearchDictOfList(lb_config.db_tokens, "token", token)
			if lb_tool.is_not_expired(tokenx["dateExpire"]):
				username = tokenx["username"]
				userz, idz = lb_tool.SearchDictOfList(lb_config.db_users, "username", username)
				if userz != None and userz["username"] != "admin":
					if lb_config.db_users[idz]["password"] == lb_tool.HashPassword(password):
						message = {"message": True}
					else:
						message = {"message": False}
				else:
					message ={"message": "token non valido"}
			else:
				message = {"message": "token scaduto"}
		except:
			message = HTTPException(status_code=400, detail="SYNTAX ERROR")
		return message						

	# function to connect to manager connection of weight real time
	@app.websocket("/wspesata/{token}")
	async def websocket_endpoint(websocket: WebSocket, token: str):
		if lb_tool.TokenTrue(token):
			await manager.connect(websocket)
			#lb_config.last_pesata = lb_config.pesa_real_time["weight"]
			#await manager.broadcast(lb_config.pesa_real_time)			
			try:
				while True:
					await asyncio.sleep(0.2)
					 #if lb_config.pesa_real_time["weight"] != lb_config.last_pesata: 
					#lb_config.last_pesata = lb_config.pesa_real_time["weight"]						
					await manager.broadcast(lb_config.pesa_real_time)
			except WebSocketDisconnect:
				await manager.disconnect(websocket)
		else:
			return HTTPException(status_code=400, detail="NOT AUTHENTICATED")

	# function to connect to manager connection of diagnostic
	@app.websocket("/wsdiagnostic/{token}")
	async def websocket_diagnostic(websocket: WebSocket, token: str):
		if lb_tool.TokenTrue(token):
			await manager_diagnostic.connect(websocket)
			try:
				while True:
					await asyncio.sleep(0.2)
					await manager_diagnostic.broadcast(lb_config.diagnostic)
			except WebSocketDisconnect:
				await manager_diagnostic.disconnect(websocket)
		else:
			return HTTPException(status_code=400, detail="NOT AUTHENTICATED")
		
	# function to connect to manager connection of weight real time
	@app.websocket("/wsanagrafica_in_corso/{token}")
	async def websocket_anagrafica(websocket: WebSocket, token: str):
		if lb_tool.TokenTrue(token):
			await manager_anagrafica.connect(websocket)
			try:
				while True:
					await asyncio.sleep(0.2)
					if lb_config.anagrafica_in_corso:
						await manager_anagrafica.broadcast(lb_config.anagrafica_in_corso)
			except WebSocketDisconnect:
				await manager_anagrafica.disconnect(websocket)
		else:
			return HTTPException(status_code=400, detail="NOT AUTHENTICATED")
	
	# function to send message to weigher
	@app.get("/comando/{code}")
	async def Comando(code: str):
		md_pesa_dini.comando(code)	
		return {"message": code}

	# function get list of weight filtered
	@app.post("/pesate/{token}")
	async def Pesate(filtri: list, token: str, offset: int = 0, limit: int = 3000):
		try:
			if lb_tool.TokenTrue(token):
				if filtri != []:
					collect = []
					filtra = ""
					for d in filtri:
						campo = d['campo'].upper().strip()
						operatore = d['operatore'].strip()
						valore = d['valore']
						if isinstance(valore, str):
							filtra = filtra + "%s %s '%s'"% (campo, operatore, valore)
						else:
							filtra = filtra + "%s %s %s"% (campo, operatore, valore)
						if d != filtri[-1]:
							if 'separatore' in d:
								if d['separatore'].strip() == "and" or d['separatore'].strip() == 'or':
									filtra = filtra + " %s "%d['separatore'].strip()
								else:
									filtra = filtra + " and "
							else:
								filtra = filtra + " and "
					lb_log.info(filtra)
					pesate = await FiltraPesate(filtra, offset, limit)
					return pesate
				else:
					return await ListaPesate(offset, limit)
			else:
				return HTTPException(status_code=404, detail="NOT AUTHENTICATED")
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	@app.get("/filtra_pesate")
	async def FiltraPesate(filtri: str, offset: int = 0, limit: int = 100):
		try:
			file_db_pesate = "../db/database.db"
			async with aiosqlite.connect(file_db_pesate) as db:
				async with db.cursor() as cursor:
					# First query to get the total count of matching records
					count_query = f"SELECT COUNT(*) FROM pesate WHERE {filtri}"
					await cursor.execute(count_query)
					total_count = (await cursor.fetchone())[0]
					
					# For the main query, use parameterized queries for pagination
					# Keep the original complex ORDER BY clause
					main_query = f'''SELECT *
					FROM pesate
					WHERE {filtri}
					ORDER BY max(coalesce((datetime(substr(DATA1, 7, 4) || '-' || substr(DATA1, 4, 2) || '-' || substr(DATA1, 1, 2) || ' ' || substr(ORA1, 1, 2) || ':' || substr(ORA1, 4, 5))), 0), coalesce((datetime(substr(DATA2, 7, 4) || '-' || substr(DATA2, 4, 2) || '-' || substr(DATA2, 1, 2) || ' ' || substr(ORA2, 1, 2) || ':' || substr(ORA2, 4, 5))), 0)) DESC
    				LIMIT {limit} OFFSET {offset}'''
					
					await cursor.execute(main_query)
					
					pesate = await cursor.fetchall()
					
					# Third query to calculate the sum of both PESO1 and PESO2
					sum_query = f'''
					SELECT IFNULL(SUM(CAST(NETTO AS REAL)), 0) AS total_netto 
					FROM pesate 
					WHERE {filtri}
					'''
					await cursor.execute(sum_query)
					result = await cursor.fetchone()
					somma = result[0] if result[0] is not None else 0
					
					if pesate:
						return {
							"pesate": pesate, 
							"somma": somma,
							"total_count": total_count,
							"offset": offset,
							"limit": limit
						}
					else:
						return {
							"pesate": [], 
							"somma": 0,
							"total_count": 0,
							"offset": offset,
							"limit": limit
						}
		except aiosqlite.Error as e:
			return f"Errore nel recupero dei dati: {str(e)}"

	@app.get("/lista_pesate")
	async def ListaPesate(offset: int = 0, limit: int = 100):
		try:
			file_db_pesate = "../db/database.db"
			async with aiosqlite.connect(file_db_pesate) as db:
				async with db.cursor() as cursor:
					# First query to get the total count
					await cursor.execute("SELECT COUNT(*) FROM pesate")
					total_count = (await cursor.fetchone())[0]
					
					# Second query to get the paginated list of weights
					# Use parameterized queries for pagination
					query = f"SELECT * FROM pesate ORDER BY id DESC LIMIT {limit} OFFSET {offset}"
					
					await cursor.execute(query)
					
					pesate = await cursor.fetchall()
					
					# Third query to calculate the sum of both PESO1 and PESO2
					await cursor.execute('''
					SELECT IFNULL(SUM(CAST(NETTO AS REAL)), 0) AS total_netto 
					FROM pesate 
					''')
					result = await cursor.fetchone()
					somma = result[0] if result[0] is not None else 0
					
					if pesate:
						return {
							"pesate": pesate, 
							"somma": somma,
							"total_count": total_count,
							"offset": offset,
							"limit": limit
						}
					else:
						return {
							"pesate": [], 
							"somma": 0,
							"total_count": 0,
							"offset": offset,
							"limit": limit
						}
		except aiosqlite.Error as e:
			return f"Errore nel recupero dei dati: {str(e)}"

	@app.delete("/delete/pesate/{token}")
	async def DeletePesate(filtri: list, token: str):
		try:
			if lb_tool.TokenTrue(token):
				if filtri != []:
					collect = []
					filtra = ""
					for d in filtri:
						campo = d['campo'].upper().strip()
						operatore = d['operatore'].strip()
						valore = d['valore']
						if isinstance(valore, str):
							filtra = filtra + "%s %s '%s'"% (campo, operatore, valore)
						else:
							filtra = filtra + "%s %s %s"% (campo, operatore, valore)
						if d != filtri[-1]:
							if 'separatore' in d:
								if d['separatore'].strip() == "and" or d['separatore'].strip() == 'or':
									filtra = filtra + " %s "%d['separatore'].strip()
								else:
									filtra = filtra + " and "
							else:
								filtra = filtra + " and "
					lb_log.info(filtra)
					await DeleteFiltraPesate(filtra)
					return 200
				else:
					await DeleteListaPesate()
					return 200
			else:
				return HTTPException(status_code=404, detail="NOT AUTHENTICATED")
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")		

	# function to filter weight
	@app.delete("/delete/filtra_pesate")
	async def DeleteFiltraPesate(filtri: str):
		try:
			# Specifica il nome del file SQLite
			nome_file_sqlite = "../db/database.db"

			# Crea una connessione al database
			conn = sqlite3.connect(nome_file_sqlite)

			# Ottieni un cursore per eseguire query SQL
			cursor = conn.cursor()
			cursor.execute(f"DELETE FROM pesate WHERE {filtri}")
			conn.commit()
			conn.close()
		except Exception as e:
			lb_log.info(e)

	# function to get list of weight
	@app.delete("/delete/lista_pesate")
	async def DeleteListaPesate():
		try:
			# Specifica il nome del file SQLite
			nome_file_sqlite = "../db/database.db"

			# Crea una connessione al database
			conn = sqlite3.connect(nome_file_sqlite)

			# Ottieni un cursore per eseguire query SQL
			cursor = conn.cursor()
			cursor.execute("DELETE FROM pesate")
			conn.commit()
			conn.close()
		except Exception as e:
			lb_log.info(e)

	from fastapi.responses import StreamingResponse # Add to Top

	# function to export list of weight
	@app.post("/export/{type}/{token}")
	async def get_export_data(filtri: list, type: str, token: str):
		try:
			if lb_tool.TokenTrue(token):
				if filtri != []:
					collect = []
					filtra = ""
					for d in filtri:
						campo = d['campo'].upper().strip()
						operatore = d['operatore'].strip()
						valore = d['valore']
						if isinstance(valore, str):
							filtra = filtra + "%s %s '%s'"% (campo, operatore, valore)
						else:
							filtra = filtra + "%s %s %s"% (campo, operatore, valore)
						if d != filtri[-1]:
							if 'separatore' in d:
								if d['separatore'].strip() == "and" or d['separatore'].strip() == 'or':
									filtra = filtra + " %s "%d['separatore'].strip()
								else:
									filtra = filtra + " and "
							else:
								filtra = filtra + " and "
					lb_log.info(filtra)
					pesate = await FiltraPesate(filtra, "")
					file = await Export(pesate, type)
					return file
				else:					
					pesate = await ListaPesate("")
					file = await Export(pesate, type)
					lb_log.info(pesate)
					return file
			else:
				return HTTPException(status_code=404, detail="NOT AUTHENTICATED")
		except Exception as e:
			return HTTPException(status_code=400, detail=f"{e}")

	# function to format list of weight by type pass as parameter 
	async def Export(pesate: list, type: string):
		df = pd.DataFrame(
			pesate,			
			columns=["TIPO", "ID", "BIL", "DATA1", "ORA1", "DATA2", "ORA2", "PROG1", "PROG2", "BADGE", "TARGA", "CLIENTE", "FORNITORE", "MATERIALE",
				"NOTE1", "NOTE2", "PESO1", "PID1", "PESO2", "PID2", "NETTO"]
		)

		# Reorder columns to match the specified order
		columns_order = ["TIPO", "ID", "PROG1", "PROG2", "CLIENTE", "TARGA", "FORNITORE", "MATERIALE", "BADGE", "NETTO", "DATA1", "ORA1", "PESO1", "DATA2", "ORA2", "PESO2", "PID1", "PID2", "NOTE1", "NOTE2", "BIL"]
		# Filter columns that are present in the dataframe and reorder them
		df = df[[col for col in columns_order if col in df.columns]]  
  
		df.drop(columns=["ID"], inplace=True)
		df.drop(columns=["TIPO"], inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["prog_one"] == False:
			df.drop(columns=["PROG1"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["prog_two"] == True:
				df.rename(columns={"PROG2": "PROG"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["prog_two"] == False:
			df.drop(columns=["PROG2"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["prog_one"] == True:
				df.rename(columns={"PROG1": "PROG"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["pid_one"] == False:
			df.drop(columns=["PID1"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["pid_two"] == True:
				df.rename(columns={"PID2": "PID"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["pid_two"] == False:
			df.drop(columns=["PID2"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["pid_one"] == True:
				df.rename(columns={"PID1": "PID"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["bil"] == False:
			df.drop(columns=["BIL"], inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["customer"] == False:
			df.drop(columns=["CLIENTE"], inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["supplier"] == False:
			df.drop(columns=["FORNITORE"], inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["material"] == False:
			df.drop(columns=["MATERIALE"], inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["plate"] == False:
			df.drop(columns=["TARGA"], inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["net_weight"] == False:
			df.drop(columns=["NETTO"], inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["date_time_one"] == False:
			df.drop(columns=["DATA1", "ORA1"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["date_time_two"] == True:
				df.rename(columns={"DATA2": "DATA"}, inplace=True)
				df.rename(columns={"ORA2": "ORA"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["weight_one"] == False:
			df.drop(columns=["PESO1"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["weight_two"] == True:
				df.rename(columns={"PESO2": "PESO"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["date_time_two"] == False:
			df.drop(columns=["DATA2", "ORA2"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["date_time_one"] == True:
				df.rename(columns={"DATA1": "DATA"}, inplace=True)
				df.rename(columns={"ORA1": "ORA"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["weight_two"] == False:
			df.drop(columns=["PESO2"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["weight_one"] == True:
				df.rename(columns={"PESO1": "PESO"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["note_one"] == False:
			df.drop(columns=["NOTE1"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["note_two"] == True:
				df.rename(columns={"NOTE2": "NOTE"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["note_two"] == False:
			df.drop(columns=["NOTE2"], inplace=True)
			if lb_config.setup["settings_machine"]["list_settings"]["note_one"] == True:
				df.rename(columns={"NOTE1": "NOTE"}, inplace=True)
		if lb_config.setup["settings_machine"]["list_settings"]["badge"] == False:
			df.drop(columns=["BADGE"], inplace=True)

		if type == "csv":
			return StreamingResponse(
				iter([df.to_csv(index=False)]),
				media_type="text/csv",
				headers={"Content-Disposition": "attachment; filename=data.csv"}
			)
		# Se il tipo è XLSX
		else:
			# Creare un file Excel in memoria
			output = BytesIO()
			with pd.ExcelWriter(output, engine="openpyxl") as writer:
				df.to_excel(writer, index=False, sheet_name="Sheet1")
			output.seek(0)

			# Restituire il file Excel come risposta in streaming
			return StreamingResponse(
				output,
				media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
				headers={"Content-Disposition": "attachment; filename=data.xlsx"}
			)

	# function to send a message to weigher
	@app.post("/sendmessage")
	async def SendMessage(message: lb_tool.message_req):
		try:
			if lb_tool.TokenTrue(message.token):
				ms = message.seconds*1000
				hexms = hex(ms).replace("0x", "")
				if ms and hexms:
					md_pesa_dini.comando("DINT" + str(message.seconds*1000))
					md_pesa_dini.comando("DISP00" + message.text)
					return {"message": "messaggio inviato alla pesa"}
				return {"message": "errore nell'invio del messaggio alla pesa"}
			else:
				return HTTPException(status_code=404, detail="NOT AUTHENTICATED")
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")
	
	# function to get info about machine
	@app.get("/infomachine/{token}")
	async def InfoMachine(token: str):
		try:
			if lb_tool.TokenTrue(token):
				return lb_config.diagnostic
			else:
				return HTTPException(status_code=404, detail="NOT AUTHENTICATED")
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")
	# function to get info about machine after login
	@app.get("/infomachinelogin")
	async def InfoMachineLogin():
		try:
			return lb_config.diagnostic
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")       
	
	# function for opcua
	@app.get("/opcua/{token}")
	async def OpcuaConf(token: str):
		try:
			if lb_tool.TokenTrue(token):
				lb_config.setup["opcua"]["activated"] = not lb_config.setup["opcua"]["activated"]
				lb_tool.Save(lb_config.path_setup, lb_config.setup)
				return {"activated": lb_config.setup["opcua"]["activated"]}
			return {"message": "non autenticato"}
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")
	
	# function to set opcua configuration
	@app.post("/setup/opcua/{token}")
	async def SetupOpcua(setup: lb_tool.setup_opcua, token: str):
		try:
			if lb_tool.TokenTrue(token):
				lb_config.setup["opcua"]["ip"] = setup.ip
				lb_config.setup["opcua"]["port"] = setup.port
				lb_config.setup["opcua"]["node_realtime"] = setup.node_realtime
				lb_config.setup["opcua"]["node_lastweight"] = setup.node_lastweight
				lb_config.setup["opcua"]["node_datetime"] = setup.node_datetime
				lb_config.setup["opcua"]["node_tare"] = setup.node_tare
				if lb_tool.Save(lb_config.path_setup, lb_config.setup):
					return {"message": "Modificato con successo"}
				return {"message": "Errore nel salvataggio"}
			return {"message": "non autenticato"}
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	# function to get data of macchine configuration
	@app.get("/setup/settingsmachine")
	async def SettingsMachine():
		return {"message": lb_config.setup["settings_machine"]}

	# function to set serial name
	@app.post("/setnomeseriale")
	async def SetNomeSeriale(setup_nameserial: lb_tool.setup_nameserial):
		message = ""
		authorizated = False
		try:
			authorizated = lb_tool.IsAuthorizated(setup_nameserial.token)
			if authorizated:
				try:
					lb_config.seriale = serial.Serial(setup_nameserial.name_serial, 9600, timeout=0.5)
					os.system("chmod 777 " + lb_config.nome_seriale)
				except:
					return {"status_code": 500, "message": "La porta che hai inserito non è valida"}
				lb_config.setup["settings_machine"]["name_serial"] = setup_nameserial.name_serial
				if lb_tool.Save(lb_config.path_setup, lb_config.setup):
					lb_config.nome_seriale = lb_config.setup["settings_machine"]["name_serial"]
					return {"status_code": 200, "message": "Porta seriale modificata con successo"}
			else:
				message = HTTPException(status_code=404, detail="NOT AUTHORIZATION")
		except:
			message = HTTPException(status_code=400, details="SYNTAX ERROR")
		return message

	# function to set if license plate is required
	@app.get("/setup/licenseplaterequired/{condition}/{token}")
	async def LicensePlateRequired(condition: bool, token: str):
		try:
			if lb_tool.TokenTrue(token):
				lb_config.setup["settings_machine"]["license_plate_required"] = condition
				if lb_tool.Save(lb_config.path_setup, lb_config.setup):
					return {"message": "Changed succesfully"}
				return {"message": "Errore nel salvataggio"}
			else:
				return {"message": "non autenticato"}
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")
			
	# function to set list view
	@app.post("/setup/list/{token}")
	async def SetList(token: str, setup: lb_tool.list_settings):
		try:
			if lb_tool.IsAuthorizated(token):
				for key, value in setup:
					if value != None:
						lb_config.setup["settings_machine"]["list_settings"][key] = value					
				lb_tool.Save(lb_config.path_setup, lb_config.setup)
				return lb_config.setup["settings_machine"]["list_settings"]
			else:
				return HTTPException(status_code=404, detail="NOT AUTHORIZATION")
		except:
			return HTTPException(status_code=400, details="SYNTAX ERROR")

	# function to set buttons view
	@app.post("/setup/buttons/{token}")
	async def SetList(token: str, setup: lb_tool.buttons_settings):
		try:
			if lb_tool.IsAuthorizated(token):
				for key, value in setup:
					if value != None:
						lb_config.setup["settings_machine"]["buttons_settings"][key] = value					
				lb_tool.Save(lb_config.path_setup, lb_config.setup)
				return lb_config.setup["settings_machine"]["buttons_settings"]
			else:
				return HTTPException(status_code=404, detail="NOT AUTHORIZATION")
		except:
			return HTTPException(status_code=400, details="SYNTAX ERROR")

	# function to set max weight
	@app.get("/setup/maxweigth/{weigth}/{token}")
	async def MaxWeigth(weigth: int, token: str):
		try:
			if lb_tool.TokenTrue(token):
				lb_config.setup["settings_machine"]["max_weigth"] = weigth
				if lb_tool.Save(lb_config.path_setup, lb_config.setup):
					lb_config.minWeight = lb_config.setup["settings_machine"]["division_selected"] * 20
					return {"message": "Modificato con successo"}
				return {"message": "Errore nel salvataggio"}
			else:
				return {"message": "non autenticato"}
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	# function to set division selected
	@app.get("/setup/divisionselected/{division}/{token}")
	async def DivisionSelected(division: int, token: str):
		try:
			if lb_tool.TokenTrue(token):
				lb_config.setup["settings_machine"]["division_selected"] = division
				if lb_tool.Save(lb_config.path_setup, lb_config.setup):
					lb_config.minWeight = lb_config.setup["settings_machine"]["division_selected"] * 20
					return {"message": "Modificato con successo"}
				return {"message": "Errore nel salvataggio"}
			else:
				return {"message": "non autenticato"}
		except:
			return HTTPException(status_code=400, detail="SYNTAX ERROR")
	
	# function to get checksum
	@app.get("/checksum/{stringa}")
	async def Checksum(stringa: str):
		return lb_tool.Checksum(stringa)

	# function to insert anagrafic of license plate
	@app.post("/anagrafica_automezzi/{action}")
	async def Automezzi(automezzi: list, action: str):
		try:
			quantity = len(automezzi)
			i = 1
			lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			n = 1
			for automezzo in automezzi:
				if len(automezzo["tara"])>6:
					return {"message": "Errore nella stringa '{}' con indice '{}', la tara è troppo alta".format(automezzo, n)}
				if len(automezzo["descrizione"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione ha troppi caratteri".format(automezzo, n)}
				if len(automezzo["targa"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la targa ha troppi caratteri".format(automezzo, n)}
				if int(automezzo["pesatura_rimorchio"])>1:
					return {"message": "Errore nella stringa '{}' con indice '{}', la pesatura rimorchio ha troppi caratteri".format(automezzo, n)}
				if len(automezzo["totale_prime_pesate1"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale prime pesate 1 è troppo alto".format(automezzo, n)}
				if len(automezzo["totale_seconde_pesate1"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale seconde pesate 1 è troppo alto".format(automezzo, n)}
				if len(automezzo["totale_pesate"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale pesate è troppo alto".format(automezzo, n)}
				if len(automezzo["totale_prime_pesate2"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale prime pesate 2 è troppo alto".format(automezzo, n)}
				if len(automezzo["totale_seconde_pesate2"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale seconde pesate 2 totale è troppo alto".format(automezzo, n)}
				n = n + 1
			for automezzo in automezzi:
				if automezzo["empty"] == True:
					pos = automezzo["pos"]
					checksum = lb_tool.Checksum("NULL")
					stringa = "WREC,3,{},NULL,{}".format(pos, checksum)
					md_pesa_dini.comando(stringa)
				else:
					stringa =  "{};{};{};{};{};{};{};{};{};".format(automezzo["targa"], automezzo["descrizione"], automezzo["tara"], automezzo["pesatura_rimorchio"], "0", "0", "0", "0", "0")
					pos = automezzo["pos"]
					checksum = lb_tool.Checksum(stringa)
					stringa = "WREC,3,{},{},{}".format(pos, stringa, checksum)
					md_pesa_dini.comando(stringa)
					lb_log.info(f"{automezzo['pos']}/500")
				await asyncio.sleep(0.1)
				i = i + 1
				lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			lb_config.pesata_in_esecuzione = False
			lb_config.anagrafica_in_corso = ""
			message = ""
			if quantity > 1:
				message = "Fornitori"
			else:
				message = "Fornitore"
			return message + " " + action
		except Exception as e:
			print("errore: {}".format(e))				
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	@app.post("/anagrafica_materiali/{action}")
	async def Materiali(materiali: list, action: str):
		try:
			quantity = len(materiali)
			i = 1
			lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			n = 1
			for materiale in materiali:
				if len(materiale["pos"])!=4:
					return {"message": "Errore nella stringa '{}' con indice '{}', la posizione deve avere 4 caratteri".format(materiale, n)}        
				if len(materiale["descrizione1"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione 1 ha troppi caratteri".format(materiale, n)}
				if len(materiale["descrizione2"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione 2 ha troppi caratteri".format(materiale, n)}
				if len(materiale["totale_prime_pesate1"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale prime pesate 1 è troppo alto".format(materiale, n)}
				if len(materiale["totale_seconde_pesate1"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale seconde pesate 1 è troppo alto".format(materiale, n)}
				if len(materiale["totale_pesate"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale pesate è troppo alto".format(materiale, n)}
				if len(materiale["totale_prime_pesate2"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale prime pesate 2 è troppo alto".format(materiale, n)}
				if len(materiale["totale_seconde_pesate2"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale seconde pesate 2 totale è troppo alto".format(materiale, n)}
				n = n + 1
			for materiale in materiali:
				if materiale["empty"] == True:
					pos = materiale["pos"]
					checksum = lb_tool.Checksum("NULL")
					stringa = "WREC,1,{},NULL,{}".format(pos, checksum)
					md_pesa_dini.comando(stringa)
				else:
					stringa =  "{};{};{};{};{};{};{};".format(materiale["descrizione1"], materiale["descrizione2"], "0", "0", "0", "0", "0")
					pos = materiale["pos"]
					checksum = lb_tool.Checksum(stringa)
					stringa = "WREC,1,{},{},{}".format(pos, stringa, checksum)
					md_pesa_dini.comando(stringa)
					lb_log.info(f"{materiale['pos']}/500")
				await asyncio.sleep(0.1)
				i = i + 1
				lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			lb_config.pesata_in_esecuzione = False
			lb_config.anagrafica_in_corso = ""
			message = ""
			if quantity > 1:
				message = "Materiali"
			else:
				message = "Materiale"
			return message + " " + action
		except Exception as e:
			lb_log.info("errore: {}".format(e))				
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	@app.post("/anagrafica_fornitori/{action}")
	async def Fornitori(fornitori: list, action: str):
		try:
			quantity = len(fornitori)
			i = 1
			lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			n = 1
			for fornitore in fornitori:
				if len(fornitore["pos"])!=4:
					return {"message": "Errore nella stringa '{}' con indice '{}', la posizione deve avere 4 caratteri".format(fornitore, n)}        
				if len(fornitore["descrizione1"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione 1 ha troppi caratteri".format(fornitore, n)}
				if len(fornitore["descrizione2"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione 2 ha troppi caratteri".format(fornitore, n)}
				if len(fornitore["descrizione3"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione 3 ha troppi caratteri".format(fornitore, n)}
				if len(fornitore["totale_prime_pesate1"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale prime pesate 1 è troppo alto".format(fornitore, n)}
				if len(fornitore["totale_seconde_pesate1"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale seconde pesate 1 è troppo alto".format(fornitore, n)}
				if len(fornitore["totale_pesate"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale pesate è troppo alto".format(fornitore, n)}
				if len(fornitore["totale_prime_pesate2"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale prime pesate 2 è troppo alto".format(fornitore, n)}
				if len(fornitore["totale_seconde_pesate2"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale seconde pesate 2 totale è troppo alto".format(fornitore, n)}
				n = n + 1
			for fornitore in fornitori:
				if fornitore["empty"] == True:
					pos = fornitore["pos"]
					checksum = lb_tool.Checksum("NULL")
					stringa = "WREC,6,{},NULL,{}".format(pos, checksum)
					md_pesa_dini.comando(stringa)
				else:
					stringa =  "{};{};{};{};{};{};{};{};".format(fornitore["descrizione1"], fornitore["descrizione2"], fornitore["descrizione3"], "0", "0", "0", "0", "0")
					pos = fornitore["pos"]
					checksum = lb_tool.Checksum(stringa)
					stringa = "WREC,6,{},{},{}".format(pos, stringa, checksum)
					md_pesa_dini.comando(stringa)
					lb_log.info(f"{fornitore['pos']}/500")
				await asyncio.sleep(0.1)
				i = i + 1
				lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			lb_config.pesata_in_esecuzione = False
			lb_config.anagrafica_in_corso = ""
			message = ""
			if quantity > 1:
				message = "Fornitori"
			else:
				message = "Fornitore"
			return message + " " + action
		except Exception as e:
			print("errore: {}".format(e))				
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	@app.post("/anagrafica_clienti/{action}")
	async def Clienti(clienti: list, action: str):
		try:
			quantity = len(clienti)
			i = 1
			lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			n = 1
			for cliente in clienti:
				if len(cliente["pos"])!=4:
					return {"message": "Errore nella stringa '{}' con indice '{}', la posizione deve avere 4 caratteri".format(cliente, n)}        
				if len(cliente["descrizione1"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione 1 ha troppi caratteri".format(cliente, n)}
				if len(cliente["descrizione2"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione 2 ha troppi caratteri".format(cliente, n)}
				if len(cliente["descrizione3"])>20:
					return {"message": "Errore nella stringa '{}' con indice '{}', la descrizione 3 ha troppi caratteri".format(cliente, n)}
				if len(cliente["totale_prime_pesate1"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale prime pesate 1 è troppo alto".format(cliente, n)}
				if len(cliente["totale_seconde_pesate1"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale seconde pesate 1 è troppo alto".format(cliente, n)}
				if len(cliente["totale_pesate"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale pesate è troppo alto".format(cliente, n)}
				if len(cliente["totale_prime_pesate2"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale prime pesate 2 è troppo alto".format(cliente, n)}
				if len(cliente["totale_seconde_pesate2"])>10:
					return {"message": "Errore nella stringa '{}' con indice '{}', il totale seconde pesate 2 totale è troppo alto".format(cliente, n)}
				n = n + 1
			for cliente in clienti:
				if "empty" in cliente:
					pos = cliente["pos"]
					checksum = lb_tool.Checksum("NULL")
					stringa = "WREC,0,{},NULL,{}".format(pos, checksum)
					md_pesa_dini.comando(stringa)
				else:
					stringa =  "{};{};{};{};{};{};{};{};".format(cliente["descrizione1"], cliente["descrizione2"], cliente["descrizione3"], "0", "0", "0", "0", "0")
					pos = cliente["pos"]
					checksum = lb_tool.Checksum(stringa)
					stringa = "WREC,0,{},{},{}".format(pos, stringa, checksum)
					md_pesa_dini.comando(stringa)
					lb_log.info(f"{cliente['pos']}/500")
				await asyncio.sleep(0.1)
				i = i + 1
				lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			lb_config.pesata_in_esecuzione = False
			lb_config.anagrafica_in_corso = ""
			message = ""
			if quantity > 1:
				message = "Clienti"
			else:
				message = "Cliente"
			return message + " " + action
		except Exception as e:
			print("errore: {}".format(e))				
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	@app.post("/anagrafica_tessere/{action}")
	async def Tessere(tessere: list, action: str):
		try:
			quantity = len(tessere)
			i = 1
			lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			n = 1
			for tessera in tessere:
				if len(tessera["pos"])!=4:
					return {"message": "Errore nella stringa '{}' con indice '{}', la posizione deve avere 4 caratteri".format(tessera, n)}        
				if len(tessera["codice"])>30:
					return {"message": "Errore nella stringa '{}' con indice '{}', il codice ha troppi caratteri".format(tessera, n)}
				if len(tessera["cli"])>4:
					return {"message": "Errore nella stringa '{}' con indice '{}', il cli ha troppi caratteri".format(tessera, n)}
				if len(tessera["mat"])>4:
					return {"message": "Errore nella stringa '{}' con indice '{}', il mat ha troppi caratteri".format(tessera, n)}
				if len(tessera["aut"])>4:
					return {"message": "Errore nella stringa '{}' con indice '{}', il aut è troppo alto".format(tessera, n)}
				if len(tessera["for"])>4:
					return {"message": "Errore nella stringa '{}' con indice '{}', il for è troppo alto".format(tessera, n)}
				if int(tessera["ric_conf_pes"])>1:
					return {"message": "Errore nella stringa '{}' con indice '{}', il ric conf pes ha troppi caratteri".format(tessera, n)}
				if int(tessera["direzione"])<1 and int(tessera["direzione"])>3:
					return {"message": "Errore nella stringa '{}' con indice '{}', la direzione è troppo alta".format(tessera, n)}
				n = n + 1
			for tessera in tessere:
				if tessera["empty"] == True:
					pos = tessera["pos"]
					checksum = lb_tool.Checksum("NULL")
					stringa = "WREC,5,{},NULL,{}".format(pos, checksum)
					md_pesa_dini.comando(stringa)
				else:
					stringa =  "{};{};{};{};{};{};{};".format(tessera["codice"], tessera["cli"], tessera["mat"], tessera["aut"], tessera["for"], tessera["ric_conf_pes"], tessera["direzione"])
					pos = tessera["pos"]
					checksum = lb_tool.Checksum(stringa)
					stringa = "WREC,5,{},{},{}".format(pos, stringa, checksum)
					md_pesa_dini.comando(stringa)
					lb_log.info(f"{tessera['pos']}/500")
				await asyncio.sleep(0.1)
				i = i + 1
				lb_config.anagrafica_in_corso = "{}/{}".format(i, quantity)
			lb_config.pesata_in_esecuzione = False
			lb_config.anagrafica_in_corso = ""
			message = ""
			if quantity > 1:
				message = "Tessere"
			else:
				message = "Tessera"
			return message + " " + action
		except Exception as e:
			print("errore: {}".format(e))				
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	# function for print
	@app.get("/print/{token}/")
	async def Print(token: str):
		try:
			if lb_tool.TokenTrue(token):
				if type(lb_config.pesa_real_time["gross_weight"]) != int or lb_config.pesa_real_time["gross_weight"] <= 0:
					return {"message": "la pesata non può essere eseguita se il peso è 0 o sotto lo 0"}
				if lb_config.pesa_real_time["gross_weight"] > lb_config.setup["settings_machine"]["max_weigth"] or lb_config.pesa_real_time["gross_weight"] < lb_config.minWeight:
					return {"message": "the weight must be between {} and {}".format(lb_config.minWeight, lb_config.setup["settings_machine"]["max_weigth"])}
				if lb_config.pesa_real_time["status"] == "US":
					return {"message": "peso instabile"}
				lb_config.pesata_in_esecuzione = True
				md_pesa_dini.comando("P")
				await lb_utility.Attend()
				if lb_config.pesata_in_esecuzione:
					lb_config.pesata_in_esecuzione = False
					return {"message": "Dati non acquisiti"}
				return {"message": "Dati acquisiti"}
			else:
				return {"message": "non autenticato"}
		except:
			lb_config.pesata_in_esecuzione = False
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	# function for weight1
	@app.get("/weight1/{token}/")
	async def Weigth1(token: str, targa: Union[str, None] = None):
		try:
			if lb_tool.TokenTrue(token):
				if type(lb_config.pesa_real_time["gross_weight"]) != int or lb_config.pesa_real_time["gross_weight"] <= 0:
					return {"message": "la pesata non può essere eseguita se il peso è 0 o sotto lo 0"}
				if lb_config.pesa_real_time["gross_weight"] > lb_config.setup["settings_machine"]["max_weigth"] or lb_config.pesa_real_time["gross_weight"] < lb_config.minWeight:
					return {"message": "il peso deve essere compreso tra {} e {}".format(lb_config.minWeight, lb_config.setup["settings_machine"]["max_weigth"])}
				if lb_config.pesa_real_time["status"] == "US":
					return {"message": "peso instabile"}
				lb_config.pesata_in_esecuzione = True
				if lb_config.setup["settings_machine"]["license_plate_required"] == True and not targa:
					lb_config.pesata_in_esecuzione = False
					return {"message": "targa richiesta"}
				if targa:
					stringa = targa + "; ;         0;0;         0;         0;0;         0;         0;"
					checksum = lb_tool.Checksum(stringa)
					stringa = "WREC,3,0000," + stringa + "," + checksum
					md_pesa_dini.comando(stringa)
					await asyncio.sleep(1)
				md_pesa_dini.comando("WREC,2,0000,ID;ING;3;0;0;,25")
				await lb_utility.Attend()
				if lb_config.pesata_in_esecuzione:
					lb_config.pesata_in_esecuzione = False
					return {"message": "Dati non acquisiti"}
				return {"message": "Dati acquisiti"}
			else:
				return {"message": "non autenticato"}
		except:
			lb_config.pesata_in_esecuzione = False
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	# function for weight2 by id
	@app.get("/weight2/{idx}/{token}")
	async def Weight2(idx: str, token: str):
		try:
			if lb_tool.TokenTrue(token):
				if type(lb_config.pesa_real_time["gross_weight"]) != int or lb_config.pesa_real_time["gross_weight"] <= 0:
					return {"message": "la pesata non può essere eseguita se il peso è 0 o sotto lo 0"}
				if lb_config.pesa_real_time["gross_weight"] > lb_config.setup["settings_machine"]["max_weigth"] or lb_config.pesa_real_time["gross_weight"] < lb_config.minWeight:
					return {"message": "il peso deve essere compreso tra {} e {}".format(lb_config.minWeight, lb_config.setup["settings_machine"]["max_weigth"])}
				if lb_config.pesa_real_time["status"] == "US":
					return {"message": "peso instabile"}
				lb_config.pesata_in_esecuzione = True
				while len(idx) < 3:
					idx = "0" + idx
				stringa = "ID;" + idx + ";3;0;0";
				checksum = lb_tool.Checksum(stringa)
				md_pesa_dini.comando("WREC,2,0000," + stringa + "," + checksum)
				await lb_utility.Attend()
				if lb_config.pesata_in_esecuzione == True:
					lb_config.pesata_in_esecuzione = False
					return {"message": "Dati non acquisiti"}
				return {"message": "Dati acquisiti"}
			else:
				return {"message": "non autenticato"}
		except:
			lb_config.pesata_in_esecuzione = False		
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	# function for weight2
	@app.get("/weight2/{token}/")
	async def Weigth1(token: str, targa: Union[str, None] = None):
		try:
			if lb_tool.TokenTrue(token):
				if type(lb_config.pesa_real_time["gross_weight"]) != int or lb_config.pesa_real_time["gross_weight"] <= 0:
					return {"message": "la pesata non può essere eseguita se il peso è 0 o sotto lo 0"}
				if lb_config.pesa_real_time["gross_weight"] > lb_config.setup["settings_machine"]["max_weigth"] or lb_config.pesa_real_time["gross_weight"] < lb_config.minWeight:
					return {"message": "il peso deve essere compreso tra {} e {}".format(lb_config.minWeight, lb_config.setup["settings_machine"]["max_weigth"])}
				if lb_config.pesa_real_time["status"] == "US":
					return {"message": "peso instabile"}
				lb_config.pesata_in_esecuzione = True
				if targa:
					stringa = targa + "; ;         0;0;         0;         0;0;         0;         0;"
					checksum = lb_tool.Checksum(stringa)
					stringa = "WREC,3,0000," + stringa + "," + checksum
					md_pesa_dini.comando(stringa)
					await asyncio.sleep(1)
				md_pesa_dini.comando("WREC,2,0000,ID;OUT;3;0;0;,3f")
				await asyncio.sleep(3)
				await lb_utility.Attend()
				if lb_config.pesata_in_esecuzione == True:
					lb_config.pesata_in_esecuzione = False
					return {"message": "Dati non acquisiti"}
				return {"message": "Dati acquisiti"}
			else:
				return {"message": "non autenticato"}
		except:
			lb_config.pesata_in_esecuzione = False
			return HTTPException(status_code=400, detail="SYNTAX ERROR")

	uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def start():
	lb_log.info("start")
	mainprg()
	lb_log.info("end")

def init():
	pass

