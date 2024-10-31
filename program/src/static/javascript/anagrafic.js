let body = document.getElementById("body")
let host = window.location.host
let hostname = window.location.hostname
let username = document.getElementById("username")
let firmware = document.getElementById("firmware")
let modelName = document.getElementById("modelName")
let serialNumber = document.getElementById("serialNumber")
let adc = document.getElementById("adc")
let mw = document.getElementById("mv")
let infomachine = document.getElementById("infomachine")
let load = document.querySelector(".load")

let pesata
window.onload = function(){  
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    if(value == ""){
		window.location.replace("http://"+host+"/login.html")
	}else{
		let websocket_pesata = new WebSocket("ws://"+hostname+":8000/wsanagrafica_in_corso/"+value)
		console.log("Connessione websocket")
		websocket_pesata.addEventListener("message", (event) => {
			let anagrafica_in_corso = JSON.parse(event.data)
			load.innerHTML = `
				<div style="display: relative; z-index: 4; text-align: center;">
            		<button class="btn btn-primary" type="button" disabled style="width: min-content;">
                		<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
							${anagrafica_in_corso}
					</button>
				</div>
			`
		})
		let url = "http://"+hostname+":8000/user/"+value
		fetch(url)
		.then(response => response.json())
		.then(json => {
			if(json.username){
				username.textContent = "Ciao, " + json.username
			}
		})
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

function sendAnagrafica(){
	load.classList.remove("displayNone")
	let textarea = document.querySelector("textarea")
	let textareaReplace = textarea.value
	let array = textareaReplace.split(",")
	console.log(array)
	let new_array = array.map(element => {
		let mini_array = element.split(";")
		let obj = {
			"license_plate": mini_array[0],
			"description": mini_array[1],
			"tare": mini_array[2]
		}
		return obj
	});
	console.log(new_array)
	fetch('http://'+hostname+':8000/anagraficatarghe', {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(new_array)
	})
	.then(response => response.json())
	.then(response => {
		console.log(response.message)
		alert(response.message)
		load.classList.toggle("displayNone")
	})
	.catch((e) => {
		console.log(e)
		alert(e)
		load.classList.toggle("displayNone")
	})
	load.innerHTML = `
		<div style="display: relative; z-index: 4; text-align: center;">
			<button class="btn btn-primary" type="button" disabled style="width: min-content;">
				<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
				Loading...
			</button>
		</div>
	`
}