let body = document.getElementById("body")
let host = window.location.host
let hostname = window.location.hostname
let username = document.getElementById("username")
let firmware = document.getElementById("firmware")
let modelName = document.getElementById("modelName")
let serialNumber = document.getElementById("serialNumber")
let adc = document.getElementById("adc")
let mw = document.getElementById("mv")
let pw = document.getElementById("pw")
let bt = document.getElementById("bt")
let infomachine = document.getElementById("infomachine")

let pesata
window.onload = function(){  
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    if(value == ""){
		window.location.replace("http://"+host+"/login.html")
	}else{
		let url = "http://"+hostname+":8000/user/"+value
		fetch(url)
		.then(response => response.json())
		.then(json => {
			if(json.username){
				username.textContent = "Ciao, " + json.username
			}
		})
		let websocket_pesata = new WebSocket("ws://"+hostname+":8000/wsdiagnostic/"+value)
		console.log("Connessione websocket")
		websocket_pesata.addEventListener("message", (event) => {
			diagnostic = JSON.parse(event.data)
			firmware.textContent = diagnostic.firmware
			modelName.textContent = diagnostic.model_name
			serialNumber.textContent = diagnostic.serial_number
			adc.textContent = diagnostic.rz
			mv.textContent = diagnostic.vl
			pw.textContent = diagnostic.pw
			bt.textContent = diagnostic.bt
			console.log(diagnostic.pw)
		});
		websocket_pesata.onopen = () => {
			console.log('Connessione aperta');
		};		
		websocket_pesata.onclose = (event) => {
			adc.textContent = "---"
			mv.textContent = "---"
			pw.textContent = "---"
			bt.textContent = "Connessione al server della pesa perso"
		};
		websocket_pesata.onerror = (error) => {
			adc.textContent = "---"
			mv.textContent = "---"
			pw.textContent = "---"
			bt.textContent = "Connessione al server della pesa perso"
		};
		let urlinfomachine = "http://"+hostname+":8000/infomachine/"+value
		fetch(urlinfomachine)
		.then(response => response.json())
		.then(json => {
			infomachine.textContent = "Firmware: " + json.firmware + " | Model name: " + json.model_name + " | Serial number: " + json.serial_number
			console.log(json)
		})
		body.classList.remove("displayNone")
	}
}    

let logout = document.getElementById("logout")
function Logout(){
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    let date = new Date();
    document.cookie = "tokenBaron="+value + "; expires=" + "Thu, 01 Jan 1970 00:00:00 UTC";
	window.location.replace("http://"+host+"/login.html")
};
