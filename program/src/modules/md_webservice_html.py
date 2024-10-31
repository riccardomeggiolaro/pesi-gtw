from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import lb_log
import lb_tool
from lb_tool import *
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import uvicorn
from os.path import exists




# ==== MAINLOOP ===============================================

app = FastAPI()

app.mount("/static/javascript", StaticFiles(directory="static/javascript"), name="javascript")
app.mount("/static/css", StaticFiles(directory="static/css"), name="css")
app.mount("/static/img", StaticFiles(directory="static/img"), name="img")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

def mainprg():

	app.add_middleware(
		CORSMiddleware, 
		allow_origins=["*"],
		allow_credentials=True,
	    allow_methods=["*"],
    	allow_headers=["*"],
	)
	
	@app.get("/{filename}", response_class=HTMLResponse)
	async def Static(request: Request, filename: str):
		file_exist = os.path.isfile(lb_config.pesigtw_path + "/src/static/"+filename)
		if file_exist:
			return templates.TemplateResponse(filename, {"request": request})
		return templates.TemplateResponse("404.html", {"request": request})	
	
	@app.get("/", response_class=HTMLResponse)
	async def Render(request: Request):
		return templates.TemplateResponse("login.html", {"request": request})
	
	uvicorn.run(app, host="0.0.0.0", port=80, log_level="info")


def start():
	lb_log.info("start")
	mainprg()
	lb_log.info("end")

def init():
	pass
