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
let containerrole = document.getElementById("containerrole")
let form = document.querySelector(".form")
let cerca = document.querySelector("#cerca")
let cancella = document.querySelector("#cancella")
let infomachine = document.getElementById("infomachine")
let value;
let p;
let input_dates = document.getElementById("date")
let prog_delete = document.getElementById("prog_delete")
let cliente_delete = document.getElementById("cliente_delete")
let targa_delete = document.getElementById("targa_delete")
let range = document.getElementById("range")
let bil_delete = document.getElementById("bil_delete")
let tipo_delete = document.getElementById("tipo_delete")
let prog = document.getElementById("prog")
let cliente = document.getElementById("cliente")
let targa = document.getElementById("targa")
let data = document.getElementById("data")
let bil = document.getElementById("bil")
let tipo = document.getElementById("tipo")
let prog_value = prog.value
let cliente_value = cliente.value
let targa_value = targa.value
let bil_value = bil.value
let data_value = data.value
let tipo_value = tipo.checked

window.onload = (event) => {  
    value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    if(value == ""){
		window.location.replace("http://"+host+"/login.html")
	}else{
		containerrole.classList.remove("displayNone")
		fetch('http://'+hostname+':8000/pesate/'+value, {
			method: 'POST',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify([])
		})
		.then(response => response.json())
		.then(response => {
			AddRows(response)
			console.log(response)
			containerrole.classList.toggle("displayNone")
		})
		.catch((e) => {
			containerrole.classList.toggle("displayNone")
			console.log(e)
		})
	}
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
	body.classList.remove("displayNone")
	
	setInterval(IfChangeCerca, 1000)
}

function IfChangeCerca() {
	if (prog.value !== prog_value || cliente.value !== cliente_value || targa.value !== targa_value || bil.value !== bil_value || data.value !== data_value || tipo.checked !== tipo_value) { // Controlla se è cambiato
		Cerca()
		if (prog.value !== prog_value) prog_value = prog.value; // Aggiorna il valore precedente
		if (cliente.value !== cliente_value) cliente_value = cliente.value;
		if (targa.value !== targa_value) targa_value = targa.value;
		if (bil.value !== bil_value) bil_value = bil.value;
		if (data.value !== data_value) data_value = data.value;
		if (tipo.checked !== tipo_value) tipo_value = tipo.checked;
	}
}
  

function changeValue() {
    let selectBox = document.getElementById("righe");
    let selectedValue = selectBox.options[selectBox.selectedIndex].value;
    console.log(selectedValue);
}    

let logout = document.getElementById("logout")
function Logout(){
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
    let date = new Date();
    document.cookie = "tokenBaron="+value + "; expires=" + "Thu, 01 Jan 1970 00:00:00 UTC";
	window.location.replace("http://"+host+"/login.html")
};

cerca.addEventListener("click", Cerca)

function Cerca() {
	containerrole.classList.remove("displayNone")
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
	let filters = AddFilters()
	console.log(JSON.stringify(filters))
	fetch('http://'+hostname+':8000/pesate/'+value, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(filters)
	})
	.then(response => response.json())
	.then(response => {
		AddRows(response)
		console.log(response)
		containerrole.classList.toggle("displayNone")
	})
	.catch((e) => {
		containerrole.classList.toggle("displayNone")
		console.log(e)
	})
}

function Elimina() {
	let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
	let filters = AddFilters()
	console.log(JSON.stringify(filters))
	fetch('http://'+hostname+':8000/delete/pesate/'+value, {
		method: 'DELETE',
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(filters)
	})
	.then(response => response.json())
	.then(response => {
		Cerca()
	})
	.catch((e) => {
		console.log(e)
	})
}

function exportData(type) {
	containerrole.classList.remove("displayNone")
    let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
	let filters = AddFilters()
	console.log(JSON.stringify(filters))
	fetch('http://'+hostname+':8000/export/'+type+'/'+value, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(filters)
	})
	.then((response) => {
		if (!response.ok) {
		  throw new Error("Errore nella richiesta.");
		}
		return response.blob(); // Ottieni il corpo della risposta come un oggetto Blob
	  })
	  .then((blob) => {
		// Crea un URL oggetto temporaneo per il Blob
		const url = window.URL.createObjectURL(blob);
	
		// Crea un elemento <a> per il download
		const a = document.createElement("a");
		a.href = url;
		a.download = `pesate.${type}`; // Nome del file da scaricare
		a.style.display = "none";
	
		// Aggiungi l'elemento <a> al documento e scatena il download
		document.body.appendChild(a);
		a.click();
	
		// Rimuovi l'elemento <a> e rilascia l'URL oggetto
		window.URL.revokeObjectURL(url);
		containerrole.classList.toggle("displayNone")
	  })
	  .catch((error) => {
		console.error("Errore:", error);
		containerrole.classList.toggle("displayNone")
	  });
}

function TryParseInt(str,defaultValue) {
     var retValue = defaultValue;
     if(str !== null) {
         if(str.length > 0) {
             if (!isNaN(str)) {
                 retValue = parseInt(str);
             }
         }
     }
     return retValue;
}

function AddFilters(){
	let arr_filters = []
	let f_prog = document.getElementById("prog")
	let f_cliente = document.getElementById("cliente")
	let f_targa = document.getElementById("targa")
	let f_data = document.getElementById("data")
	let f_bil = document.getElementById("bil")
	let _prog = TryParseInt(f_prog.value, null)
	let f_tipo = document.getElementById("tipo")
	let filtri = [
					{"CLIENTE": `${f_cliente.value}`},
					{"TARGA": `${f_targa.value}`}
				]
	for (let i in filtri){
		let obj = filtri[i]
		let key = Object.keys(filtri[i])[0];
		if((obj[key] != "" && obj[key] != null && obj[key] != undefined) || typeof obj[key] == 'number'){
			let new_filter = {"campo": key, "operatore": "LIKE", "valore": `${obj[key]}%`, "separatore": "and"}
			arr_filters.push(new_filter)
		}
	}
	
	if (_prog != null && _prog != ""){
		let new_filter1 = {"campo": "PROG1", "operatore": "=", "valore": _prog, "separatore": "or"}
		let new_filter2 = {"campo": "PROG2", "operatore": "=", "valore": _prog, "separatore": "and"}
		arr_filters.push(new_filter1)
		arr_filters.push(new_filter2)
		prog_delete.textContent = `- con progressivo "${_prog}"`
	}else{
		prog_delete.textContent = ""
	}
	if (f_cliente.value != "" && f_cliente.value != null && f_cliente.value != undefined){
		cliente_delete.textContent = `- con cliente che inizia con "${f_cliente.value}"`
	}else{
		cliente_delete.textContent = ""
	}
	if (f_targa.value != "" && f_targa.value != null && f_targa.value != undefined){
		targa_delete.textContent = `- con targa che inizia con "${f_targa.value}"`
	}else{
		targa_delete.textContent = ""
	}
	if (f_data.value != "" && f_data.value != null && f_data.value != undefined){
		let arrdt = f_data.value.split(" ")
		if (arrdt.length == 3){
			let f_data = arrdt[0]
			let t_data = arrdt[2]
			let from_data1 = {"campo": "DATA1", "operatore": ">=", "valore": f_data, "separatore": "and"}
			let to_data1 = {"campo": "DATA1", "operatore": "<=", "valore": t_data, "separatore": "or"}
			let from_data2 = {"campo": "DATA2", "operatore": ">=", "valore": f_data, "separatore": "and"}
			let to_data2 = {"campo": "DATA2", "operatore": "<=", "valore": t_data, "separatore": "and"}
			arr_filters.push(from_data1)
			arr_filters.push(to_data1)
			arr_filters.push(from_data2)
			arr_filters.push(to_data2)
			range.textContent = `- dalla data "${f_data}" alla data "${t_data}"`
		}
	}else{
		range.textContent = ""
	}
	if(f_bil.value != null && f_bil.value != ""){
		let new_filter = {"campo": "BIL", "operatore": "=", "valore": f_bil.value, "separatore": "and"}
		arr_filters.push(new_filter)
		bil_delete.textContent = `- con bilancia numero "${f_bil.value}"`
	}else{
		bil_delete.textContent = ""
	}
	if(f_tipo.checked){
		let new_filter = {"campo": "TIPO", "operatore": "=", "valore": 1, "separatore": "and"}
		arr_filters.push(new_filter)
		tipo_delete.textContent = `- con pesata uno non chiusa da una seconda pesata`
	}else{
		tipo_delete.textContent = ""
	}
	return arr_filters
}

function AddRows(data){		
	p = []
	console.log(data.length)
    console.log("populating data table...");
    var length = data.length
	if(length > 0){
//	    $("#example").DataTable().clear();
	    $("#example").DataTable().rows().remove().draw();
		for(var i = 0; i < length; i++) {
		  var d = data[i];
		  let progs = "";
		  if(d[7] != "" && d[8] != "") progs = d[7] + "<br> \n" + d[8]
		  else if(d[7] != "" && d[8] == "") progs = d[7]
		  else if(d[7] == "" && d[8] != "") progs = d[8]
		  let pids = "";
		  if(d[17] != "" && d[19] != "") pids = d[17] + "<br> \n" + d[19]
		  else if(d[17] != "" && d[19] == "") pids = d[17]
		  else if(d[17] == "" && d[19] != "") pids = d[19]
		  const pesata = [
			progs,
			d[11],
			d[10],
			d[12],
			d[13],
			d[20],
			d[3] + "<br> \n" + d[4],
			d[16],
			d[5] + "<br> \n" + d[6],
			d[18],
			pids,
			d[2]
		  ]
		  $('#example').dataTable().fnAddData(pesata);
		  p.push(pesata)
		}
	}else{
	    $("#example").DataTable().rows().remove().draw();
	}
}

//DA SISTEMARE
	$(function() {

	  $('input[name="dates"]').daterangepicker({
		"opens": "center",
		"drops": "auto",
		"showDropdowns": true,
		"ranges": {
		    'Oggi': [moment(), moment()],
		    'Ieri': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
		    'Questa settimana': [moment().subtract(6, 'days'), moment()],
		    'Questo mese': [moment().startOf('month'), moment().endOf('month')],
		    'Lo scorso mese': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
		},
		autoUpdateInput: false,
		locale: {
		    cancelLabel: 'Cancella',
			format: "DD/MM/YYYY"
		},
	  });

	  $('input[name="dates"]').on('apply.daterangepicker', function(ev, picker) {
		  $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
		  Cerca()
	  });

	  $('input[name="dates"]').on('cancel.daterangepicker', function(ev, picker) {
		  $(this).val('');
	  });
	});

//FUNZIONA	
cancella.addEventListener("click", (event) => {
	$("#prog").val('')
	$("#cliente").val('')
	$("#targa").val('')
	document.getElementById("data").value = ""
	$("#bil").val('')
	document.getElementById("tipo").checked = false
})

function submitForm() {
	// Prevent the default form submission behavior
	event.preventDefault();
}