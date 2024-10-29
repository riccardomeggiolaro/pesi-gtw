let body = document.getElementById("body")
let host = window.location.host
let hostname = window.location.hostname
let username = document.getElementById("username")
let buttonProfile = document.getElementById("buttonProfile")
let buttonPassword = document.getElementById("buttonPassword")
let buttonUsers = document.getElementById("buttonUsers")
let buttonSetup = document.getElementById("buttonSetup")
let formProfile = document.getElementById("formProfile")
let inputUsername = document.getElementById("inputUsername")
let inputDescription = document.getElementById("inputDescription")
let inputSeclev = document.getElementById("inputSeclev")
let inputOldPassword = document.getElementById("oldPassword")
let inputNewPassword = document.getElementById("newPassword")
let inputRepeatPassword = document.getElementById("repeatPassword")
let formPassword = document.getElementById("formPassword")
let formSetup = document.getElementById("formSetup")
let checkbox = document.getElementById("flexCheckChecked")
let progrCheckbox = document.getElementById("progr")
let pidCheckbox = document.getElementById("pid")
let bilCheckbox = document.getElementById("bil")
let customerCheckbox = document.getElementById("customer")
let supplierCheckbox = document.getElementById("supplier")
let materialCheckbox = document.getElementById("material")
let plateCheckbox = document.getElementById("plate")
let netWeightCheckbox = document.getElementById("netWeight")
let dateTimeOneCheckbox = document.getElementById("dateTimeOne")
let weightOneCheckbox = document.getElementById("weightOne")
let dateTimeTwoCheckbox = document.getElementById("dateTimeTwo")
let weightTwoCheckbox = document.getElementById("weightTwo")
let buttonTare = document.getElementById("tare")
let buttonPTare = document.getElementById("p_tare")
let buttonZero = document.getElementById("zero")
let buttonPrint = document.getElementById("print")
let buttonWeightOne = document.getElementById("weight_one")
let buttonWeightTwo = document.getElementById("weight_two")
let tableUsers = document.getElementById("tableUsers")
let infomachine = document.getElementById("infomachine")
let token
let myUsername
let popup = document.getElementById("containerPopup")
let closePopup = document.getElementById("closePopup")
let select = document.getElementById("divisions")
let maxWeight = document.getElementById("maxWeigth")
let nameSerial = document.getElementById("nameSerial")

let pesata
window.onload = function(){  
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    token = value
    if(value == ""){
		window.location.replace("http://"+host+"/login.html")
	}else{
		let url = "http://"+hostname+":8000/user/"+value
		fetch(url)
		.then(response => response.json())
		.then(json => {
			if(json.username){
				username.textContent = "Ciao, " + json.username
				myUsername = json.username
				inputUsername.placeholder = json.username
				inputDescription.placeholder = json.descrizione
				if (json.seclev == 5){
					inputSeclev.placeholder = "ADMIN"
				} else {
					buttonUsers.classList.toggle("displayNone")
					buttonSetup.classList.toggle("displayNone")
					inputSeclev.placeholder = "USER"
				}
			}
		})
		let urlinfomachine = "http://"+hostname+":8000/infomachine/"+value
		fetch(urlinfomachine)
		.then(response => response.json())
		.then(json => {
			infomachine.textContent = "Firmware: " + json.firmware + " | Model name: " + json.model_name + " | Serial number: " + json.serial_number
		})
		let urlsettingsmachine = "http://"+hostname+":8000/setup/settingsmachine"
		fetch(urlsettingsmachine)
		.then(response => response.json())
		.then(response => {
			if (response.message.license_plate_required == true){
				checkbox.checked = true
			}else{
				checkbox.checked = false
			}
			Object.keys(response.message.list_settings).forEach(element => {
				console.log(element)
				switch(element){
					case "progr":
						progrCheckbox.checked = response.message.list_settings.progr;
					case "pid":
						pidCheckbox.checked = response.message.list_settings.pid;
					case "bil":
						bilCheckbox.checked = response.message.list_settings.bil;
					case "customer":
						customerCheckbox.checked = response.message.list_settings.customer;
					case "supplier":
						supplierCheckbox.checked = response.message.list_settings.supplier;
					case "material":
						materialCheckbox.checked = response.message.list_settings.material;
					case "plate":
						plateCheckbox.checked = response.message.list_settings.plate;
					case "net_weight":
						netWeightCheckbox.checked = response.message.list_settings.net_weight;
					case "date_time_one":
						dateTimeOneCheckbox.checked = response.message.list_settings.date_time_one;
					case "weight_one":
						weightOneCheckbox.checked = response.message.list_settings.weight_one;
					case "date_time_two":
						dateTimeTwoCheckbox.checked = response.message.list_settings.date_time_two;
					case "weight_two":
						weightTwoCheckbox.checked = response.message.list_settings.weight_two;
				}
			})
			Object.keys(response.message.buttons_settings).forEach(element => {
				console.log(element)
				switch(element){
					case "tare":
						buttonTare.checked = response.message.buttons_settings.tare;
					case "p_tare":
						buttonPTare.checked = response.message.buttons_settings.p_tare;
					case "zero":
						buttonZero.checked = response.message.buttons_settings.zero;
					case "print":
						buttonPrint.checked = response.message.buttons_settings.print;
					case "weight_one":
						buttonWeightOne.checked = response.message.buttons_settings.weight_one;
					case "weight_two":
						buttonWeightTwo.checked = response.message.buttons_settings.weight_two;
				}
			})
			for(let i=0; i<response.message.options_divisions.length; i++){
	  			let option = document.createElement("option")
	  			option.text = response.message.options_divisions[i]
	  			option.value = response.message.options_divisions[i]
	  			if(response.message.options_divisions[i] == response.message.division_selected){
	  				option.selected = true
	  			}
	  			select.add(option)
			}
			maxWeight.placeholder = response.message.max_weigth
			nameSerial.placeholder = response.message.name_serial
		})
		body.classList.remove("displayNone")
	}
}    

function profileShow(){
	if(formProfile.classList.contains("displayNone")){
		if(!formPassword.classList.contains("displayNone")){formPassword.classList.toggle("displayNone")}
		if(!tableUsers.classList.contains("displayNone")){tableUsers.classList.toggle("displayNone")}
		if(!formSetup.classList.contains("displayNone")){formSetup.classList.toggle("displayNone")}
		formProfile.classList.remove("displayNone")
	}
}

function passwordShow(){
	if(formPassword.classList.contains("displayNone")){
		if(!formProfile.classList.contains("displayNone")){formProfile.classList.toggle("displayNone")}
		if(!tableUsers.classList.contains("displayNone")){tableUsers.classList.toggle("displayNone")}	
		if(!formSetup.classList.contains("displayNone")){formSetup.classList.toggle("displayNone")}
		formPassword.classList.remove("displayNone")
	}
}

function usersShow(){
	if(tableUsers.classList.contains("displayNone")){
		if(!formProfile.classList.contains("displayNone")){formProfile.classList.toggle("displayNone")}
		if(!formPassword.classList.contains("displayNone")){formPassword.classList.toggle("displayNone")}
		if(!formSetup.classList.contains("displayNone")){formSetup.classList.toggle("displayNone")}
		tableUsers.classList.remove("displayNone")
	}
	getUsers()
}

function setupShow(){
	if (formSetup.classList.contains("displayNone")){
		if(!formProfile.classList.contains("displayNone")){formProfile.classList.toggle("displayNone")}
		if(!formPassword.classList.contains("displayNone")){formPassword.classList.toggle("displayNone")}
		if(!tableUsers.classList.contains("displayNone")){tableUsers.classList.toggle("displayNone")}
		formSetup.classList.remove("displayNone")
	}
}

function changeUser(){
	conf = confirm("Sei sicuro di voler modificare l'utente?")
	if(conf){
		obj = {}
		if(inputUsername.value){
			obj["username"] = inputUsername.value
		}
		if(inputDescription.value){
			obj["descrizione"] = inputDescription.value
		}
    	let token = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];		
		fetch('http://'+hostname+':8000/putuser/'+token, {
			method: 'PUT',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(obj)
		})
		.then(response => response.json())
		.then(response => {
			document.cookie = "tokenBaron="+response.new_token
			location.reload()
		})
	}
}

function changePassword(){
	if(inputOldPassword.value == ""){
		alert("La vecchia password deve essere inserita")
		return
	}
	if(inputNewPassword.value == ""){
		alert("La nuova password eve essere inserita")
		return
	}
	if(inputRepeatPassword.value == ""){
		alert("La ripetizione della password deve essere inserita")
		return
	}
	if(inputNewPassword.value != inputRepeatPassword.value){
		alert("La nuova e la ripetizione della password devono essere uguali")
		return
	}
	fetch("http://"+hostname+":8000/password/"+token+"/"+inputOldPassword.value)
	.then(response => response.json())
	.then(response => {
		if(response.message != true){
			alert("The old password is not correct")
			return
		}else{
			let conf = confirm("Sei sicuro di voler cambiare la password?")
			if(conf){
				obj = {"password": inputRepeatPassword.value}
				fetch('http://'+hostname+':8000/putuser/'+token, {
					method: 'PUT',
					headers: {
						'Accept': 'application/json',
						'Content-Type': 'application/json'
					},
					body: JSON.stringify(obj)
				})
				.then(response => response.json())
				.then(response => {
					if(response.new_token){
						document.cookie = "tokenBaron="+response.new_token
						alert("Password changed succesfully")
					}else{
						console.log(response)
					}
				})
			}
		}
	})
}

function getUsers(){
	fetch("http://"+hostname+":8000/alluser/"+token)
	.then(response => response.json())
	.then(json => {
		console.log(json)
		$('#table').find('tbody').detach();
		$('#table').append($('<tbody>'))
		for(let i=0; i<=json.length; i++){
			if(json[i].username == "admin" || json[i].username == myUsername){				
				let type = "";
				if(json[i].username == "admin") type = "Super amministratore"
				else type = "Amministratore"
				$('#table tbody').append(`<tr><td>${json[i].username}</td><td>${json[i].descrizione}</td><td>${type}</td><td></td></tr>`);
			}else{
				let type = "";
				if(json[i].seclev == 4) type = "Utente"
				else type = "Amministratore"
				button = `<button type='submit' class='btn btn-danger' onclick='deleteUser(event)' name='${json[i].username}'>Elimina</button>`
				$('#table tbody').append(`<tr><td>${json[i].username}</td><td>${json[i].descrizione}</td><td>${type}</td><td>${button}</td></tr>`);
			}
		}
	})
}

function deleteUser(event){
	conf = confirm("Sei sicuro di voler eliminare questo utente?")
	if(conf){
		fetch("http://"+hostname+":8000/deleteuser/"+event.currentTarget.name+"/"+token, {
				method: 'DELETE',
				headers: {
					'Accept': 'application/json',
					'Content-Type': 'application/json'
				}
		})
		.then(response => response.json())
		.then(json => {
			alert(json.message)
			getUsers()
		})
	}
}

function addUser(){
	let newUsername = document.getElementById("newUsername").value
	let newDescription = document.getElementById("newDescription").value
	let newNewPassword = document.getElementById("newNewPassword").value
	let newRepeatPassword = document.getElementById("newRepeatPassword").value
	let newSeclev = document.getElementById("newSeclev").value
	if(newUsername == "" || newDescription == "" || newNewPassword == "" || newRepeatPassword == "" || newSeclev == ""){
		alert("All of input must to be compiled")
		return
	}
	if(newNewPassword != newRepeatPassword){
		alert("Le password devono essere uguali")
		return
	}
	obj = {
			  "username": newUsername,
			  "password": newNewPassword,
			  "descrizione": newDescription,
			  "seclev": newSeclev
		  }
	fetch('http://'+hostname+':8000/adduser/'+token, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(obj)
	})
	.then(response => response.json())
	.then(response => {
		if(response.message){
			getUsers()
			alert(response.message)
		}else{
			alert("Problema nell'aggiunta dell'utente")
		}
	})
}

function LicensePlateRequired(){
	let checked
	if(checkbox.checked){
		checked = true
	}else{
		checked = false
	}
	fetch("http://"+hostname+":8000/setup/licenseplaterequired/"+checked+"/"+token)
	.then(response => response.json())
	.then(response => {
		console.log(response.message)
	})
}

function IsRequired(key) {
	let checked_value = null

	switch (key) {
		case "progr":
			checked_value = progrCheckbox.checked
			break
		case "pid":
			checked_value = pidCheckbox.checked
			break
		case "bil":
			checked_value = bilCheckbox.checked
			break
		case "customer":
			checked_value = customerCheckbox.checked
			break
		case "supplier":
			checked_value = supplierCheckbox.checked
			break
		case "material":
			checked_value = materialCheckbox.checked
			break
		case "plate":
			checked_value = plateCheckbox.checked
			break
		case "net_weight":
			checked_value = netWeightCheckbox.checked
			break
		case "date_time_one":
			checked_value = dateTimeOneCheckbox.checked
			break
		case "weight_one":
			checked_value = weightOneCheckbox.checked
			break
		case "date_time_two":
			checked_value = dateTimeTwoCheckbox.checked
			break
		case "weight_two":
			checked_value = weightTwoCheckbox.checked
			break
	}
	console.log({[key]: checked_value})
	fetch("http://" + hostname + ":8000/setup/list/" + token, {
		method: "POST",
		headers: {
		  "Content-Type": "application/json"
		},
		body: JSON.stringify({ [key]: checked_value })
	})
	.then(response => response.json())
	.then(response => {
		console.log(response);
	})
}

function IsActive(key) {
	let checked_value = null

	switch (key) {
		case "tare":
			checked_value = buttonTare.checked
			break
		case "p_tare":
			checked_value = buttonPTare.checked
			break
		case "zero":
			checked_value = buttonZero.checked
			break
		case "print":
			checked_value = buttonPrint.checked
			break
		case "weight_one":
			checked_value = buttonWeightOne.checked
			break
		case "weight_two":
			checked_value = buttonWeightTwo.checked
			break
	}
	console.log({[key]: checked_value})
	fetch("http://" + hostname + ":8000/setup/buttons/" + token, {
		method: "POST",
		headers: {
		  "Content-Type": "application/json"
		},
		body: JSON.stringify({ [key]: checked_value })
	})
	.then(response => response.json())
	.then(response => {
		console.log(response);
	})
}

let logout = document.getElementById("logout")
function Logout(){
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    let date = new Date();
    document.cookie = "tokenBaron="+value + "; expires=" + "Thu, 01 Jan 1970 00:00:00 UTC";
	window.location.replace("http://"+host+"/login.html")
};

var exampleModal = document.getElementById('exampleModal')
exampleModal.addEventListener('show.bs.modal', function (event) {
  // Button that triggered the modal
  var button = event.relatedTarget
  // Extract info from data-bs-* attributes
  var recipient = button.getAttribute('data-bs-whatever')
  // If necessary, you could initiate an AJAX request here
  // and then do the updating in a callback.
  //
  // Update the modal's content.
  var modalTitle = exampleModal.querySelector('.modal-title')
  var modalBodyInput = exampleModal.querySelector('.modal-body input')
})

function SaveMaxWeigth(){
	let newMaxWeigth = maxWeight.value
	let urlmaxweigth = "http://"+hostname+":8000/setup/maxweigth/"+newMaxWeigth+"/"+token
	fetch(urlmaxweigth)
	.then(response => response.json())
	.then(response => alert(response.message))
}

function SetNameSerial(){
	let newNameSerial = nameSerial.value
	if(newNameSerial != ""){
		fetch('http://'+hostname+':8000/setnomeseriale', {
			method: 'POST',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				"token": token,
				"name_serial": newNameSerial
			})
		})
		.then(response => response.json())
		.then(response => {
			if(response.message){
				alert(response.message)
				if(response.status_code == 200){
					nameSerial.placeholder = newNameSerial
				}
			}else{
				alert("Problema nella modifica della porta seriale")
			}
		})
	}else{
		alert("Necessario inserire valore")
	}
}

select.addEventListener("change", (event) => {
	let newDivisionSelected = event.target.value
	let urldivisionselected = "http://"+hostname+":8000/setup/divisionselected/"+newDivisionSelected+"/"+token
	fetch(urldivisionselected)
	.then(response => response.json())
	.then(response => console.log(response))
});
