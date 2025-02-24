let body = document.getElementById("body")
let host = window.location.host
let hostname = window.location.hostname
let username = document.getElementById("username")
let infomachine = document.getElementById("infomachine")

window.onload = function(){  
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    if(value == ""){
		window.location.replace("http://"+host+"/login.html")
	}else{
		let url = "http://"+hostname+":8000/user/"+value
		fetch(url)
		.then(response => response.json())
		.then(json => {
			username.textContent = "Ciao, " + json.username
		})
		let urlinfomachine = "http://"+hostname+":8000/infomachine/"+value
		fetch(urlinfomachine)
		.then(response => response.json())
		.then(json => {
			infomachine.textContent = "Firmware: " + json.firmware + " | Model name: " + json.model_name + " | Serial number: " + json.serial_number
		})
		body.classList.remove("displayNone")
	}
}    

function EnterText(){
    let token = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
	let text = document.getElementById("testo").value.trimStart().trimEnd()
	let second = 5;
	let sendMessage = {
		"text": text,
		"seconds": second,
		"token": token
	}
	fetch('http://'+hostname+':8000/sendmessage', {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(sendMessage)
	})
	.then(response => response.json())
	.then(response => {
		if(response.message){
			alert(response.message)
		}else{
			alert("Errore nell'invio del messaggio")
		}
	})
}

let logout = document.getElementById("logout")
function Logout(){
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    let date = new Date();
    document.cookie = "tokenBaron="+value + "; expires=" + "Thu, 01 Jan 1970 00:00:00 UTC";
	window.location.replace("http://"+host+"/login.html")
};
