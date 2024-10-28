let body = document.getElementById("body")
let host = window.location.host
let hostname = window.location.hostname
let username = document.getElementById("username")
let type = document.getElementById("type")
let weight = document.getElementById("weight")
let tare = document.getElementById("tare")
let status = document.getElementById("status")
let btnTara = document.getElementById("btn-tara")
let btnZero = document.getElementById("btn-zero")
let btnpcWeight1 = document.getElementById("btnpc-weight1")
let btnsmWeight1 = document.getElementById("btnsm-weight1")
let btnpcPrint = document.getElementById("btnpc-print")
let btnsmPrint = document.getElementById("btnsm-print")
let btnPrint = document.getElementById("btn-print")
let infomachine = document.getElementById("infomachine")
let licensePlate = document.getElementById("licensePlate")
let licensePlate2 = document.getElementById("licensePlate2")
let descriptionLicensePlate = document.getElementById("descriptionLicensePlate")
let licensePlateRequired
let buttonLicensePlate = document.getElementById("buttonLicensePlate")
let select = document.getElementById("select")
let buttonWeight2 = document.getElementById("buttonWeight2")
let infoMovimenti = document.getElementById("infoMovimenti")
let infoMovimenti2 = document.getElementById("infoMovimenti2")
let value
let presetTareActive
let formDropdown = document.getElementById("formDropdown")
let formInput = document.getElementById("formInput")

let pesata
window.onload = function(){  
	buttonWeight2.disabled = true
    value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    if(value == ""){
		window.location.replace("http://"+host+"/login.html")
	}else{
		let websocket_pesata = new WebSocket("ws://"+hostname+":8000/wspesata/"+value)
		console.log("Connessione websocket")
		websocket_pesata.addEventListener("message", (event) => {
			pesata = JSON.parse(event.data)
			type.textContent = TypeWeight(pesata.type)
			weight.textContent = String(pesata.net_weight) + pesata.unite_measure 
			tare.textContent = String(pesata.tare) + pesata.unite_measure
			status.textContent = Status(pesata.status)
			if(pesata.tare.startsWith("PT") || pesata.type == "NT"){
				btnpcWeight1.disabled = true
				btnsmWeight1.disabled = true	
				btnpcPrint.disabled = true
				btnsmPrint.disabled = true
				btnpcWeight1.style.opacity = 0.5
				btnsmWeight1.style.opacity = 0.5
				btnpcPrint.style.opacity = 0.5
				btnsmPrint.style.opacity = 0.5
				if(!formDropdown.classList.contains("displayNone")){
					formDropdown.classList.toggle("displayNone")
				}
				if(formInput.classList.contains("displayNone")){
					formInput.classList.remove("displayNone")
				}
				presetTareActive = true
			}else{
				btnpcWeight1.disabled = false
				btnsmWeight1.disabled = false
				btnpcPrint.disabled = false
				btnsmPrint.disabled = false
				btnpcWeight1.style.opacity = 1
				btnsmWeight1.style.opacity = 1
				btnpcPrint.style.opacity = 1
				btnsmPrint.style.opacity = 1
				presetTareActive = false
				if(formDropdown.classList.contains("displayNone")){
					formDropdown.classList.remove("displayNone")
				}
				if(!formInput.classList.contains("displayNone")){
					formInput.classList.toggle("displayNone")
				}
			}
//			console.log(pesata)
		});
		websocket_pesata.onopen = () => {
		  console.log('Connessione aperta');
		};		
		websocket_pesata.onclose = (event) => {
			type.textContent = "---"
			weight.textContent = "---"
			tare.textContent = "---"
			status.textContent = "Connessione al server della pesa perso"
			weight.style.backgroundColor = "white"
		};
		websocket_pesata.onerror = (error) => {
			type.textContent = "---"
			weight.textContent = "---"
			tare.textContent = "---"
			status.textContent = "Connessione al server della pesa perso"
			weight.style.backgroundColor = "white"
		};
		let websocket_anagrafica = new WebSocket("ws://"+hostname+":8000/wsanagrafica_in_corso/"+value)
		console.log("Connessione websocket")
		websocket_anagrafica.addEventListener("message", (event) => {
			console.log(event.data)
		})
		websocket_anagrafica.onopen = () => {
			console.log('Connessione aperta');
		};		
		websocket_anagrafica.onclose = (event) => {
			type.textContent = "---"
			weight.textContent = "---"
			tare.textContent = "---"
			status.textContent = "Connessione al server della pesa perso"
			weight.style.backgroundColor = "white"
		};
		websocket_anagrafica.onerror = (error) => {
			type.textContent = "---"
			weight.textContent = "---"
			tare.textContent = "---"
			status.textContent = "Connessione al server della pesa perso"
			weight.style.backgroundColor = "white"
		};
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
		})
		let licenseplaterequired = "http://"+hostname+":8000/setup/settingsmachine"
		fetch(licenseplaterequired)
		.then(response => response.json())
		.then(json => {
			if(json.message.license_plate_required == true){
				licensePlate.required = true
				descriptionLicensePlate.textContent = "*Necessario inserire targa"
				buttonLicensePlate.disabled = true
			}else{
				licensePlate.required = false
				descriptionLicensePlate.textContent = "*Inserimento targa opzionale"
				buttonLicensePlate.disabled = false
			}
			buttonWeight2.disabled = true
			licensePlateRequired = json.message
		})
		let urlsettingsmachine = "http://"+hostname+":8000/setup/settingsmachine"
		fetch(urlsettingsmachine)
		.then(response => response.json())
		.then(response => {
			console.log(response.message)
			let _min = response.message.division_selected*20
			let text = `Max: ${response.message.max_weigth} | Min: ${_min} | e: ${response.message.division_selected}` 
			infoMovimenti2.textContent = text
			console.log(text)
		})
		body.classList.remove("displayNone")
	}
}

function removeOptions(select)
{
	var i;
	for(i=select.options.length-1;i>=0;i--)
	{
		select.remove(i);
	}
}
function weights2(){
	if(presetTareActive == false){
		removeOptions(select)
		let filters = [
						{
							"campo": "TIPO", 
							"operatore": "=", 
							"valore": 1, 
							"separatore": "and"
						}
					  ]
		fetch('http://'+hostname+':8000/pesate/'+value, {
			method: 'POST',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(filters)
		})
		.then(result => result.json())
		.then(result => {
			console.log(result)
			result.forEach(pesata => {
				if(pesata['TARGA'] != ""){
					var opt = document.createElement('option');
					opt.value = pesata[1];
					opt.innerHTML = "ID = " + pesata[1] + "| TARGA = " + pesata[10];
					select.appendChild(opt);
				}else{
					var opt = document.createElement('option');
					opt.value = pesata[1];
					opt.innerHTML = "ID = " + pesata[1];
					select.appendChild(opt);
				}
			});
			if(select.options.length > 0){
				buttonWeight2.disabled = false
			}else{
				buttonWeight2.disabled = true
			}
		})
	}else{
		buttonWeight2.disabled = false
	}
}

function LicensePlateValue(){
	if(licensePlateRequired){
		if(licensePlate.value.length > 0 ){
			buttonLicensePlate.disabled = false
		}else{
			buttonLicensePlate.disabled = true
		}
	}
}

function Tara(){
	let urlTara = "http://"+hostname+":8000/comando/TARE"
	fetch(urlTara)
	.then(response => response.json())
	.then(json => console.log(json.message))
}

function Zero(){
	let urlZero = "http://"+hostname+":8000/comando/ZERO"
	fetch(urlZero)
	.then(response => response.json())
	.then(json => console.log(json.message))
}

function PresetTara() {
   var presetTara = prompt("Enter a tare:", "");
   if (presetTara != null && presetTara != ""){
	   if(!isNaN(presetTara)){
			let urlTara = "http://"+hostname+":8000/comando/TMAN"+presetTara
			fetch(urlTara)
			.then(response => response.json())
			.then(json => console.log(json.message))   		
			return
	   }else{
	   		alert("La tara deve contenere solo numeri")
	   		return
	   }
	} else if(presetTara == "") {
		alert("Necessario inserire targa")
	} else {
		console.log("No tare")
	}
}

function Print(){
	let urlTara = "http://"+hostname+":8000/print/" + value
	fetch(urlTara)
	.then(response => response.json())
	.then(response => {
		if(response.message == "pesata eseguita"){
			infoMovimenti.style.backgroundColor = "rgb(102, 255, 0)"
			infoMovimenti.textContent = response.message
		}else{
			infoMovimenti.style.backgroundColor = "orange"
			infoMovimenti.textContent = response.message		
		}
		setTimeout(() => {
			infoMovimenti.textContent = ""
			infoMovimenti.style.backgroundColor = "transparent"
		}, 5000);
	})
}

function TypeWeight(typeWeight){
    if(typeWeight == "GS"){
    	return "Peso lordo"
    } else if(typeWeight == "NT"){
    	return "Peso netto"
	} else {
		return "---"
	}
}

function Status(status) {
	if(status == "US") {
		weight.style.backgroundColor = "orange"
		return "Peso instabile"
	} else if(status == "ST"){
		weight.style.backgroundColor = "#66ff00"
		return "Peso stabile"
	} else if(status == "ZR"){
		weight.style.backgroundColor = "#66ff00"
		return "Peso a zero"
	} else if(status == "UL"){
		weight.style.backgroundColor = "#66ff00"
		return "Peso negativo"
	} else if(status == "OL"){
		weight.style.backgroundColor = "red"
		return "Sovraccarico"
	} else if(status == "TL"){
		weight.style.backgroundColor = "red"		
		return "Errore di inclinamento non gestito (mezzi mobili)"
	} else if(status == "ER") {
		weight.style.backgroundColor = "red"
	 	return "Bilancia remota selezionata e bilancia remota disconnessa"
	} else {
		weight.style.backgroundColor = "white"
		type.textContent = "---"
		weight.textContent = "---"
		tare.textContent = "---"
		return status
	}
}

function Pesata1(){
	let url = "http://"+hostname+":8000/weight1/"+value
	if (licensePlate.value != ""){
		url = url + "?targa=" + licensePlate.value
	}
	fetch(url)
	.then(response => response.json())
	.then(response => {
		if(response.message == "pesata eseguita"){
			infoMovimenti.style.backgroundColor = "rgb(102, 255, 0)"
			infoMovimenti.textContent = response.message
		}else{
			infoMovimenti.style.backgroundColor = "orange"
			infoMovimenti.textContent = response.message		
		}
		setTimeout(() => {
			infoMovimenti.textContent = ""
			infoMovimenti.style.backgroundColor = "transparent"
		}, 5000);
	})
	licensePlate.value = ""
}

function Pesata2(){
	if(presetTareActive == false){
		let url = "http://"+hostname+":8000/weight2/" + select.value + "/" + value
		fetch(url)
		.then(response => response.json())
		.then(response => {
			if(response.message == "pesata eseguita"){
				infoMovimenti.style.backgroundColor = "rgb(102, 255, 0)"
				infoMovimenti.textContent = response.message
			}else{
				infoMovimenti.style.backgroundColor = "orange"
				infoMovimenti.textContent = response.message		
			}
			setTimeout(() => {
				infoMovimenti.textContent = ""
				infoMovimenti.style.backgroundColor = "transparent"
			}, 5000);
		})
	}else{
		let url = "http://"+hostname+":8000/weight2/"+value
		if (licensePlate2.value != ""){
			url = url + "?targa=" + licensePlate2.value
		}
		fetch(url)
		.then(response => response.json())
		.then(response => {
			if(response.message == "pesata eseguita"){
				infoMovimenti.style.backgroundColor = "rgb(102, 255, 0)"
				infoMovimenti.textContent = response.message
			}else{
				infoMovimenti.style.backgroundColor = "orange"
				infoMovimenti.textContent = response.message		
			}
			setTimeout(() => {
				infoMovimenti.textContent = ""
				infoMovimenti.style.backgroundColor = "transparent"
			}, 5000);
		})
		licensePlate2.value = ""
	}
}

let logout = document.getElementById("logout")
function Logout(){
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    let date = new Date();
    document.cookie = "tokenBaron="+value + "; expires=" + "Thu, 01 Jan 1970 00:00:00 UTC";
	window.location.replace("http://"+host+"/login.html")
};
var pesata1 = document.getElementById('pesata1Modal')
pesata1.addEventListener('show.bs.modal', function (event) {
  var button = event.relatedTarget
  var recipient = button.getAttribute('data-bs-whatever')
  var modalTitle = exampleModal.querySelector('.modal-title')
  var modalBodyInput = exampleModal.querySelector('.modal-body input')
})
var pesata2 = document.getElementById('pesata2Modal')
pesata2.addEventListener('show.bs.modal', function (event) {
  var button = event.relatedTarget
  var recipient = button.getAttribute('data-bs-whatever')
  var modalTitle = exampleModal.querySelector('.modal-title')
  var modalBodyInput = exampleModal.querySelector('.modal-body input')
})

weight.addEventListener("dblclick", function(event){
	fetch("http://"+hostname+":8000/comando/C")
	.then(response => response.json())
	.then(response => console.log(response))
})

